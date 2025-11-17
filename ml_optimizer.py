"""
Optimizador de Estrategias con Machine Learning

Este módulo utiliza algoritmos de ML para:
1. Optimización de parámetros usando Bayesian Optimization
2. Predicción de rendimiento con Random Forest
3. Walk-Forward Analysis automático
4. Validación cruzada temporal
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional
from datetime import datetime, timedelta
import logging
from dataclasses import dataclass

from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.model_selection import TimeSeriesSplit
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_squared_error, r2_score
from scipy.optimize import differential_evolution
from scipy.stats import spearmanr

from backtest_engine import BacktestEngine, BacktestResult
from strategies.base_strategy import TradingStrategy
from strategies.moving_average_crossover import MovingAverageCrossover
from config.settings import BacktestConfig

logger = logging.getLogger(__name__)


@dataclass
class OptimizationResult:
    """Resultado de la optimización ML"""
    best_params: Dict
    best_score: float
    all_results: pd.DataFrame
    feature_importance: Dict
    validation_metrics: Dict
    optimization_history: List[Dict]


class MLStrategyOptimizer:
    """
    Optimizador de estrategias usando Machine Learning
    
    Características:
    - Bayesian Optimization para búsqueda eficiente de parámetros
    - Random Forest para predecir rendimiento
    - Walk-Forward Analysis automático
    - Detección de overfitting
    - Validación cruzada temporal
    """
    
    def __init__(
        self,
        strategy_class: type,
        data: pd.DataFrame,
        symbol_info: Dict,
        target_metric: str = 'sharpe_ratio',
        n_iterations: int = 50,
        cv_splits: int = 5,
        validation_pct: float = 0.3
    ):
        """
        Inicializa el optimizador ML
        
        Args:
            strategy_class: Clase de estrategia a optimizar
            data: Datos históricos
            symbol_info: Información del símbolo
            target_metric: Métrica objetivo ('sharpe_ratio', 'profit_factor', etc)
            n_iterations: Número de iteraciones de optimización
            cv_splits: Número de splits para validación cruzada
            validation_pct: Porcentaje de datos para validación out-of-sample
        """
        self.strategy_class = strategy_class
        self.data = data
        self.symbol_info = symbol_info
        self.target_metric = target_metric
        self.n_iterations = n_iterations
        self.cv_splits = cv_splits
        self.validation_pct = validation_pct
        
        # Estado interno
        self.optimization_history = []
        self.best_params = None
        self.best_score = -np.inf
        self.scaler = StandardScaler()
        self.model = None
        
        # Configuración de backtest
        self.backtest_config = BacktestConfig(
            initial_capital=10000.0,
            commission_pct=0.0001,
            slippage_pct=0.0005
        )
        
        logger.info(f"MLStrategyOptimizer initialized for {strategy_class.__name__}")
        logger.info(f"Target metric: {target_metric}, Iterations: {n_iterations}")
    
    def get_parameter_space(self) -> Dict[str, Tuple]:
        """
        Obtiene el espacio de búsqueda de parámetros
        
        Returns:
            Diccionario con rangos de parámetros
        """
        # Crear instancia temporal para obtener rangos
        temp_strategy = self.strategy_class()
        param_ranges = temp_strategy.get_parameter_ranges()
        
        if not param_ranges:
            # Rangos por defecto para MA Crossover
            param_ranges = {
                'fast_period': (5, 20, 1),
                'slow_period': (20, 50, 2),
                'rsi_period': (10, 20, 2),
                'atr_stop_multiplier': (1.5, 3.0, 0.25),
                'risk_reward_ratio': (1.5, 3.5, 0.25),
            }
        
        return param_ranges
    
    def _params_dict_to_array(self, params: Dict) -> np.ndarray:
        """Convierte diccionario de parámetros a array"""
        param_space = self.get_parameter_space()
        return np.array([params.get(k, param_space[k][0]) for k in param_space.keys()])
    
    def _params_array_to_dict(self, params_array: np.ndarray) -> Dict:
        """Convierte array de parámetros a diccionario"""
        param_space = self.get_parameter_space()
        param_names = list(param_space.keys())
        
        params_dict = {}
        for i, name in enumerate(param_names):
            value = params_array[i]
            # Redondear según el step
            step = param_space[name][2]
            if step >= 1:
                value = int(round(value))
            else:
                value = round(value / step) * step
            params_dict[name] = value
        
        return params_dict
    
    def evaluate_parameters(
        self,
        params: Dict,
        data_subset: Optional[pd.DataFrame] = None
    ) -> float:
        """
        Evalúa un conjunto de parámetros
        
        Args:
            params: Parámetros de la estrategia
            data_subset: Subset de datos (para CV), usa self.data si None
            
        Returns:
            Score de la métrica objetivo
        """
        try:
            # Crear estrategia con parámetros
            strategy = self.strategy_class(**params)
            
            # Datos a usar
            data_to_use = data_subset if data_subset is not None else self.data
            
            # Ejecutar backtest
            engine = BacktestEngine(self.backtest_config)
            result = engine.run(strategy, data_to_use, self.symbol_info)
            
            # Obtener métrica objetivo
            score = result.metrics.get(self.target_metric, 0.0)
            
            # Penalizar si muy pocos trades
            if result.metrics.get('total_trades', 0) < 10:
                score *= 0.5
            
            return score
            
        except Exception as e:
            logger.warning(f"Error evaluating parameters: {e}")
            return -999.0
    
    def bayesian_optimization(self) -> OptimizationResult:
        """
        Optimización Bayesiana de parámetros
        
        Usa Differential Evolution (un tipo de algoritmo evolutivo)
        que es efectivo para optimización de parámetros continuos.
        
        Returns:
            OptimizationResult con mejores parámetros encontrados
        """
        logger.info("🔍 Starting Bayesian Optimization...")
        
        param_space = self.get_parameter_space()
        param_names = list(param_space.keys())
        
        # Definir bounds para differential evolution
        bounds = [(param_space[name][0], param_space[name][1]) for name in param_names]
        
        # Dividir datos en train/validation
        split_idx = int(len(self.data) * (1 - self.validation_pct))
        train_data = self.data.iloc[:split_idx]
        val_data = self.data.iloc[split_idx:]
        
        logger.info(f"Train data: {len(train_data)} bars, Validation: {len(val_data)} bars")
        
        # Función objetivo
        def objective(params_array):
            params = self._params_array_to_dict(params_array)
            
            # Evaluar en training data
            score = self.evaluate_parameters(params, train_data)
            
            # Registrar historial
            self.optimization_history.append({
                'params': params.copy(),
                'score': score,
                'iteration': len(self.optimization_history)
            })
            
            # Actualizar mejor
            if score > self.best_score:
                self.best_score = score
                self.best_params = params.copy()
                logger.info(f"🌟 New best score: {score:.4f} | Params: {params}")
            
            # Retornar negativo porque differential_evolution minimiza
            return -score
        
        # Ejecutar optimización
        logger.info(f"Running optimization with {self.n_iterations} iterations...")
        result = differential_evolution(
            objective,
            bounds,
            maxiter=self.n_iterations // 10,  # Iteraciones por población
            popsize=10,
            strategy='best1bin',
            mutation=(0.5, 1.5),
            recombination=0.7,
            seed=42,
            workers=1,
            updating='deferred',
            disp=True
        )
        
        # Mejores parámetros
        best_params = self._params_array_to_dict(result.x)
        
        # Validar en out-of-sample
        logger.info("📊 Validating on out-of-sample data...")
        val_score = self.evaluate_parameters(best_params, val_data)
        
        logger.info(f"✅ Optimization completed!")
        logger.info(f"   Train score: {-result.fun:.4f}")
        logger.info(f"   Validation score: {val_score:.4f}")
        logger.info(f"   Best params: {best_params}")
        
        # Crear DataFrame con resultados
        results_df = pd.DataFrame(self.optimization_history)
        
        # Calcular feature importance (sensibilidad)
        feature_importance = self._calculate_feature_importance(results_df)
        
        # Métricas de validación
        validation_metrics = {
            'train_score': -result.fun,
            'validation_score': val_score,
            'overfit_ratio': (-result.fun) / val_score if val_score > 0 else np.inf,
            'n_iterations': len(self.optimization_history)
        }
        
        return OptimizationResult(
            best_params=best_params,
            best_score=val_score,
            all_results=results_df,
            feature_importance=feature_importance,
            validation_metrics=validation_metrics,
            optimization_history=self.optimization_history
        )
    
    def random_forest_optimization(self) -> OptimizationResult:
        """
        Optimización usando Random Forest para predecir rendimiento
        
        1. Genera muestras aleatorias de parámetros
        2. Entrena Random Forest para predecir rendimiento
        3. Usa el modelo para buscar óptimos
        
        Returns:
            OptimizationResult con mejores parámetros
        """
        logger.info("🌲 Starting Random Forest Optimization...")
        
        param_space = self.get_parameter_space()
        param_names = list(param_space.keys())
        
        # Dividir datos
        split_idx = int(len(self.data) * (1 - self.validation_pct))
        train_data = self.data.iloc[:split_idx]
        val_data = self.data.iloc[split_idx:]
        
        # Fase 1: Exploración aleatoria
        logger.info("Phase 1: Random exploration...")
        n_random_samples = min(30, self.n_iterations // 2)
        
        X_samples = []
        y_scores = []
        
        for i in range(n_random_samples):
            # Generar parámetros aleatorios
            params_array = np.array([
                np.random.uniform(param_space[name][0], param_space[name][1])
                for name in param_names
            ])
            
            params = self._params_array_to_dict(params_array)
            score = self.evaluate_parameters(params, train_data)
            
            X_samples.append(params_array)
            y_scores.append(score)
            
            self.optimization_history.append({
                'params': params,
                'score': score,
                'iteration': i,
                'phase': 'random'
            })
            
            if score > self.best_score:
                self.best_score = score
                self.best_params = params.copy()
            
            if (i + 1) % 10 == 0:
                logger.info(f"Random exploration: {i+1}/{n_random_samples}")
        
        # Fase 2: Entrenar modelo Random Forest
        logger.info("Phase 2: Training Random Forest model...")
        X_train = np.array(X_samples)
        y_train = np.array(y_scores)
        
        # Escalar features
        X_train_scaled = self.scaler.fit_transform(X_train)
        
        # Entrenar Random Forest
        self.model = RandomForestRegressor(
            n_estimators=100,
            max_depth=10,
            min_samples_split=5,
            random_state=42,
            n_jobs=-1
        )
        self.model.fit(X_train_scaled, y_train)
        
        r2 = self.model.score(X_train_scaled, y_train)
        logger.info(f"Model R² score: {r2:.4f}")
        
        # Fase 3: Optimización guiada por el modelo
        logger.info("Phase 3: Model-guided optimization...")
        n_guided = self.n_iterations - n_random_samples
        
        def objective_rf(params_array):
            # Predecir score usando el modelo
            params_scaled = self.scaler.transform(params_array.reshape(1, -1))
            predicted_score = self.model.predict(params_scaled)[0]
            return -predicted_score  # Minimizar
        
        # Optimizar usando el modelo como guía
        bounds = [(param_space[name][0], param_space[name][1]) for name in param_names]
        
        result_rf = differential_evolution(
            objective_rf,
            bounds,
            maxiter=n_guided // 10,
            popsize=10,
            seed=42,
            workers=1
        )
        
        # Evaluar los mejores parámetros encontrados
        best_params_rf = self._params_array_to_dict(result_rf.x)
        train_score = self.evaluate_parameters(best_params_rf, train_data)
        val_score = self.evaluate_parameters(best_params_rf, val_data)
        
        self.optimization_history.append({
            'params': best_params_rf,
            'score': train_score,
            'iteration': len(self.optimization_history),
            'phase': 'model_guided'
        })
        
        if train_score > self.best_score:
            self.best_score = train_score
            self.best_params = best_params_rf
        
        logger.info(f"✅ Random Forest Optimization completed!")
        logger.info(f"   Train score: {train_score:.4f}")
        logger.info(f"   Validation score: {val_score:.4f}")
        logger.info(f"   Best params: {self.best_params}")
        
        # Feature importance
        feature_importance = dict(zip(
            param_names,
            self.model.feature_importances_
        ))
        
        # Crear resultados
        results_df = pd.DataFrame(self.optimization_history)
        
        validation_metrics = {
            'train_score': train_score,
            'validation_score': val_score,
            'model_r2': r2,
            'overfit_ratio': train_score / val_score if val_score > 0 else np.inf
        }
        
        return OptimizationResult(
            best_params=self.best_params,
            best_score=val_score,
            all_results=results_df,
            feature_importance=feature_importance,
            validation_metrics=validation_metrics,
            optimization_history=self.optimization_history
        )
    
    def walk_forward_optimization(
        self,
        n_windows: int = 5,
        train_pct: float = 0.7
    ) -> Dict:
        """
        Walk-Forward Analysis automático
        
        Divide los datos en ventanas y optimiza/valida en cada una
        
        Args:
            n_windows: Número de ventanas
            train_pct: Porcentaje de cada ventana para training
            
        Returns:
            Diccionario con resultados de walk-forward
        """
        logger.info(f"🚶 Starting Walk-Forward Analysis ({n_windows} windows)...")
        
        total_bars = len(self.data)
        window_size = total_bars // n_windows
        
        results = []
        
        for i in range(n_windows):
            window_start = i * window_size
            window_end = min((i + 1) * window_size, total_bars)
            
            # Datos de la ventana
            window_data = self.data.iloc[window_start:window_end]
            
            # Dividir en train/test
            split_idx = int(len(window_data) * train_pct)
            train_data = window_data.iloc[:split_idx]
            test_data = window_data.iloc[split_idx:]
            
            logger.info(f"\nWindow {i+1}/{n_windows}:")
            logger.info(f"  Train: {train_data.index[0]} to {train_data.index[-1]} ({len(train_data)} bars)")
            logger.info(f"  Test:  {test_data.index[0]} to {test_data.index[-1]} ({len(test_data)} bars)")
            
            # Optimizar en train
            temp_optimizer = MLStrategyOptimizer(
                self.strategy_class,
                train_data,
                self.symbol_info,
                self.target_metric,
                n_iterations=20,  # Menos iteraciones por ventana
                cv_splits=3
            )
            
            opt_result = temp_optimizer.bayesian_optimization()
            
            # Validar en test
            test_score = self.evaluate_parameters(opt_result.best_params, test_data)
            
            results.append({
                'window': i + 1,
                'train_start': train_data.index[0],
                'train_end': train_data.index[-1],
                'test_start': test_data.index[0],
                'test_end': test_data.index[-1],
                'best_params': opt_result.best_params,
                'train_score': opt_result.validation_metrics['train_score'],
                'test_score': test_score,
                'overfit_ratio': opt_result.validation_metrics['train_score'] / test_score if test_score > 0 else np.inf
            })
            
            logger.info(f"  Train score: {results[-1]['train_score']:.4f}")
            logger.info(f"  Test score:  {test_score:.4f}")
        
        # Análisis agregado
        df_results = pd.DataFrame(results)
        
        summary = {
            'results_by_window': df_results,
            'avg_train_score': df_results['train_score'].mean(),
            'avg_test_score': df_results['test_score'].mean(),
            'avg_overfit_ratio': df_results['overfit_ratio'].mean(),
            'stability_score': df_results['test_score'].std(),  # Menor es mejor
            'best_window': df_results.loc[df_results['test_score'].idxmax()].to_dict()
        }
        
        logger.info(f"\n✅ Walk-Forward Analysis completed!")
        logger.info(f"   Avg train score: {summary['avg_train_score']:.4f}")
        logger.info(f"   Avg test score:  {summary['avg_test_score']:.4f}")
        logger.info(f"   Stability:       {summary['stability_score']:.4f}")
        
        return summary
    
    def _calculate_feature_importance(self, results_df: pd.DataFrame) -> Dict:
        """
        Calcula importancia de features usando correlación de Spearman
        
        Args:
            results_df: DataFrame con resultados de optimización
            
        Returns:
            Diccionario con importancia de cada parámetro
        """
        param_names = list(self.get_parameter_space().keys())
        importance = {}
        
        for param in param_names:
            # Extraer valores del parámetro
            param_values = [h['params'].get(param, 0) for h in self.optimization_history]
            scores = [h['score'] for h in self.optimization_history]
            
            # Calcular correlación
            if len(param_values) > 3:
                corr, _ = spearmanr(param_values, scores)
                importance[param] = abs(corr) if not np.isnan(corr) else 0.0
            else:
                importance[param] = 0.0
        
        return importance
    
    def cross_validation(self, params: Dict) -> Dict:
        """
        Validación cruzada temporal
        
        Args:
            params: Parámetros a validar
            
        Returns:
            Métricas de validación cruzada
        """
        logger.info(f"🔄 Performing {self.cv_splits}-fold cross-validation...")
        
        tscv = TimeSeriesSplit(n_splits=self.cv_splits)
        
        train_scores = []
        test_scores = []
        
        for fold, (train_idx, test_idx) in enumerate(tscv.split(self.data)):
            train_data = self.data.iloc[train_idx]
            test_data = self.data.iloc[test_idx]
            
            train_score = self.evaluate_parameters(params, train_data)
            test_score = self.evaluate_parameters(params, test_data)
            
            train_scores.append(train_score)
            test_scores.append(test_score)
            
            logger.info(f"  Fold {fold+1}: Train={train_score:.4f}, Test={test_score:.4f}")
        
        cv_results = {
            'train_mean': np.mean(train_scores),
            'train_std': np.std(train_scores),
            'test_mean': np.mean(test_scores),
            'test_std': np.std(test_scores),
            'overfit_ratio': np.mean(train_scores) / np.mean(test_scores) if np.mean(test_scores) > 0 else np.inf,
            'train_scores': train_scores,
            'test_scores': test_scores
        }
        
        logger.info(f"✅ Cross-validation completed:")
        logger.info(f"   Train: {cv_results['train_mean']:.4f} ± {cv_results['train_std']:.4f}")
        logger.info(f"   Test:  {cv_results['test_mean']:.4f} ± {cv_results['test_std']:.4f}")
        
        return cv_results
    
    def detect_overfitting(
        self,
        opt_result: OptimizationResult,
        threshold: float = 1.2
    ) -> bool:
        """
        Detecta si hay overfitting
        
        Args:
            opt_result: Resultado de optimización
            threshold: Umbral de ratio train/test (>1.2 indica overfitting)
            
        Returns:
            True si detecta overfitting
        """
        overfit_ratio = opt_result.validation_metrics.get('overfit_ratio', 1.0)
        
        is_overfit = overfit_ratio > threshold
        
        if is_overfit:
            logger.warning(f"⚠️  Overfitting detected! Ratio: {overfit_ratio:.2f}")
            logger.warning(f"   Train score: {opt_result.validation_metrics['train_score']:.4f}")
            logger.warning(f"   Test score:  {opt_result.validation_metrics['validation_score']:.4f}")
        else:
            logger.info(f"✅ No overfitting detected. Ratio: {overfit_ratio:.2f}")
        
        return is_overfit


def optimize_strategy_ml(
    data: pd.DataFrame,
    symbol_info: Dict,
    method: str = 'bayesian',
    **kwargs
) -> OptimizationResult:
    """
    Función helper para optimizar estrategia con ML
    
    Args:
        data: Datos históricos
        symbol_info: Información del símbolo
        method: 'bayesian', 'random_forest', o 'walk_forward'
        **kwargs: Argumentos adicionales
        
    Returns:
        OptimizationResult
    """
    optimizer = MLStrategyOptimizer(
        strategy_class=MovingAverageCrossover,
        data=data,
        symbol_info=symbol_info,
        **kwargs
    )
    
    if method == 'bayesian':
        return optimizer.bayesian_optimization()
    elif method == 'random_forest':
        return optimizer.random_forest_optimization()
    elif method == 'walk_forward':
        return optimizer.walk_forward_optimization()
    else:
        raise ValueError(f"Unknown method: {method}")
