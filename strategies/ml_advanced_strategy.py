"""
Estrategia Avanzada de Trading con Machine Learning - VERSIÓN COMPATIBLE

NOTA IMPORTANTE: Esta versión está adaptada para funcionar con tu estructura existente
de base_strategy.py que usa Signal en lugar de TradeSignal.

Esta estrategia combina múltiples modelos de ML para:
1. Predicción de dirección del precio (Random Forest, XGBoost, LightGBM)
2. Predicción de volatilidad
3. Gestión dinámica de riesgo
4. Detección de regímenes de mercado
5. Optimización adaptativa de parámetros

Autor: Sistema de Trading Avanzado
Fecha: 2024
Versión: 1.0 - Compatible
"""

import numpy as np
import pandas as pd
from typing import Dict, Optional, Tuple, List
from datetime import datetime, timedelta
import logging

from sklearn.ensemble import RandomForestClassifier, GradientBoostingRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import TimeSeriesSplit
import warnings
warnings.filterwarnings('ignore')

try:
    import xgboost as xgb
    XGBOOST_AVAILABLE = True
except ImportError:
    XGBOOST_AVAILABLE = False
    logging.warning("XGBoost no disponible. Se usará solo Random Forest.")

try:
    import lightgbm as lgb
    LIGHTGBM_AVAILABLE = True
except ImportError:
    LIGHTGBM_AVAILABLE = False
    logging.warning("LightGBM no disponible. Se usará solo Random Forest.")

from strategies.base_strategy import TradingStrategy, Signal

logger = logging.getLogger(__name__)


class MLAdvancedStrategy(TradingStrategy):
    """
    Estrategia de Trading Avanzada con Machine Learning
    
    Características:
    - Ensemble de modelos ML (RF, XGBoost, LightGBM)
    - 50+ features técnicos e ingenieriles
    - Predicción de dirección y volatilidad
    - Gestión dinámica de riesgo basada en ML
    - Detección automática de regímenes de mercado
    - Filtros de calidad de señales
    - Auto-reentrenamiento periódico
    """
    
    def __init__(
        self,
        # Parámetros de ML
        lookback_period: int = 60,
        min_train_samples: int = 500,
        retrain_frequency: int = 100,
        prediction_threshold: float = 0.55,
        
        # Parámetros de features
        use_price_features: bool = True,
        use_volume_features: bool = True,
        use_volatility_features: bool = True,
        use_pattern_features: bool = True,
        
        # Gestión de riesgo
        risk_per_trade: float = 0.02,
        max_positions: int = 3,
        use_dynamic_stops: bool = True,
        atr_multiplier: float = 2.0,
        
        # Filtros
        min_volatility: float = 0.0005,
        max_volatility: float = 0.05,
        min_volume_ratio: float = 0.5,
        
        # Regímenes de mercado
        detect_regime: bool = True,
        regime_window: int = 50,
        
        **kwargs
    ):
        """
        Inicializa la estrategia ML avanzada
        """
        # Crear diccionario de parámetros
        parameters = {
            'lookback_period': lookback_period,
            'min_train_samples': min_train_samples,
            'retrain_frequency': retrain_frequency,
            'prediction_threshold': prediction_threshold,
            'use_price_features': use_price_features,
            'use_volume_features': use_volume_features,
            'use_volatility_features': use_volatility_features,
            'use_pattern_features': use_pattern_features,
            'risk_per_trade': risk_per_trade,
            'max_positions': max_positions,
            'use_dynamic_stops': use_dynamic_stops,
            'atr_multiplier': atr_multiplier,
            'min_volatility': min_volatility,
            'max_volatility': max_volatility,
            'min_volume_ratio': min_volume_ratio,
            'detect_regime': detect_regime,
            'regime_window': regime_window
        }
        
        # Inicializar clase base
        super().__init__(
            name="ML Advanced Strategy",
            parameters=parameters,
            risk_per_trade=risk_per_trade,
            use_trailing_stop=kwargs.get('use_trailing_stop', True),
            trailing_stop_pct=kwargs.get('trailing_stop_pct', 0.02)
        )
        
        # Parámetros de ML
        self.lookback_period = lookback_period
        self.min_train_samples = min_train_samples
        self.retrain_frequency = retrain_frequency
        self.prediction_threshold = prediction_threshold
        
        # Features
        self.use_price_features = use_price_features
        self.use_volume_features = use_volume_features
        self.use_volatility_features = use_volatility_features
        self.use_pattern_features = use_pattern_features
        
        # Gestión de riesgo
        self.risk_per_trade = risk_per_trade
        self.max_positions = max_positions
        self.use_dynamic_stops = use_dynamic_stops
        self.atr_multiplier = atr_multiplier
        
        # Filtros
        self.min_volatility = min_volatility
        self.max_volatility = max_volatility
        self.min_volume_ratio = min_volume_ratio
        
        # Regímenes
        self.detect_regime = detect_regime
        self.regime_window = regime_window
        
        # Modelos ML
        self.direction_model = None
        self.volatility_model = None
        self.scaler = StandardScaler()
        
        # Estado
        self.bars_since_train = 0
        self.training_data = []
        self.is_trained = False
        self.current_regime = 'neutral'
        
        # Métricas
        self.prediction_accuracy = []
        self.model_confidence = []
        
        logger.info(f"MLAdvancedStrategy inicializada: lookback={lookback_period}, "
                   f"threshold={prediction_threshold}, risk={risk_per_trade}")
    
    def calculate_indicators(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Calcula todos los indicadores y features necesarios
        """
        df = data.copy()
        
        # ===== FEATURES DE PRECIO =====
        if self.use_price_features:
            for period in [1, 3, 5, 10, 20]:
                df[f'return_{period}'] = df['close'].pct_change(period)
                df[f'log_return_{period}'] = np.log(df['close'] / df['close'].shift(period))
            
            for period in [5, 10, 20, 50, 100, 200]:
                df[f'sma_{period}'] = df['close'].rolling(period).mean()
                df[f'ema_{period}'] = df['close'].ewm(span=period, adjust=False).mean()
            
            df['dist_sma_20'] = (df['close'] - df['sma_20']) / df['sma_20']
            df['dist_sma_50'] = (df['close'] - df['sma_50']) / df['sma_50']
            df['dist_ema_20'] = (df['close'] - df['ema_20']) / df['ema_20']
            
            df['ma_cross_20_50'] = (df['sma_20'] > df['sma_50']).astype(int)
            df['ma_cross_50_200'] = (df['sma_50'] > df['sma_200']).astype(int)
            
            df['roc_10'] = ((df['close'] - df['close'].shift(10)) / df['close'].shift(10)) * 100
            df['roc_20'] = ((df['close'] - df['close'].shift(20)) / df['close'].shift(20)) * 100
            
            for period in [7, 14, 21]:
                df[f'rsi_{period}'] = self.calculate_rsi(df['close'], period)
            
            exp1 = df['close'].ewm(span=12, adjust=False).mean()
            exp2 = df['close'].ewm(span=26, adjust=False).mean()
            df['macd'] = exp1 - exp2
            df['macd_signal'] = df['macd'].ewm(span=9, adjust=False).mean()
            df['macd_hist'] = df['macd'] - df['macd_signal']
            
            df['bb_mid'] = df['close'].rolling(20).mean()
            df['bb_std'] = df['close'].rolling(20).std()
            df['bb_upper'] = df['bb_mid'] + (df['bb_std'] * 2)
            df['bb_lower'] = df['bb_mid'] - (df['bb_std'] * 2)
            df['bb_position'] = (df['close'] - df['bb_lower']) / (df['bb_upper'] - df['bb_lower'])
        
        # ===== FEATURES DE VOLATILIDAD =====
        if self.use_volatility_features:
            for period in [7, 14, 21]:
                df[f'atr_{period}'] = self.calculate_atr(df, period)
            
            for period in [10, 20, 30]:
                df[f'volatility_{period}'] = df['return_1'].rolling(period).std() * np.sqrt(252)
            
            df['true_range'] = self.calculate_true_range(df)
            df['tr_normalized'] = df['true_range'] / df['close']
            df['hl_ratio'] = (df['high'] - df['low']) / df['close']
        
        # ===== FEATURES DE VOLUMEN =====
        if self.use_volume_features and 'tick_volume' in df.columns:
            df['volume_sma_20'] = df['tick_volume'].rolling(20).mean()
            df['volume_ratio'] = df['tick_volume'] / df['volume_sma_20']
            df['obv'] = (np.sign(df['close'].diff()) * df['tick_volume']).cumsum()
            df['obv_ema'] = df['obv'].ewm(span=20, adjust=False).mean()
            df['vpt'] = (df['tick_volume'] * df['close'].pct_change()).cumsum()
        
        # ===== FEATURES DE PATRONES =====
        if self.use_pattern_features:
            df['body'] = df['close'] - df['open']
            df['body_pct'] = df['body'] / df['open']
            df['upper_shadow'] = df['high'] - df[['open', 'close']].max(axis=1)
            df['lower_shadow'] = df[['open', 'close']].min(axis=1) - df['low']
            df['is_doji'] = (abs(df['body']) / (df['high'] - df['low']) < 0.1).astype(int)
            
            df['bullish_engulfing'] = (
                (df['body'] > 0) & 
                (df['body'].shift(1) < 0) &
                (df['open'] < df['close'].shift(1)) &
                (df['close'] > df['open'].shift(1))
            ).astype(int)
            
            df['bearish_engulfing'] = (
                (df['body'] < 0) & 
                (df['body'].shift(1) > 0) &
                (df['open'] > df['close'].shift(1)) &
                (df['close'] < df['open'].shift(1))
            ).astype(int)
            
            df['consecutive_up'] = (df['close'] > df['close'].shift(1)).astype(int)
            df['consecutive_down'] = (df['close'] < df['close'].shift(1)).astype(int)
            df['up_streak'] = df['consecutive_up'].groupby(
                (df['consecutive_up'] != df['consecutive_up'].shift()).cumsum()
            ).cumsum()
            df['down_streak'] = df['consecutive_down'].groupby(
                (df['consecutive_down'] != df['consecutive_down'].shift()).cumsum()
            ).cumsum()
        
        # ===== FEATURES DE RÉGIMEN =====
        if self.detect_regime:
            df['trend_strength'] = (df['close'] - df['close'].rolling(self.regime_window).mean()) / df['close'].rolling(self.regime_window).std()
            df['regime_volatility'] = df['return_1'].rolling(self.regime_window).std()
            df['autocorr'] = df['return_1'].rolling(20).apply(
                lambda x: x.autocorr(), raw=False
            )
        
        # ===== TARGET PARA ENTRENAMIENTO =====
        df['future_return'] = df['close'].shift(-5) / df['close'] - 1
        df['target_direction'] = np.where(df['future_return'] > 0.0001, 1, 
                                          np.where(df['future_return'] < -0.0001, -1, 0))
        df['future_volatility'] = df['return_1'].shift(-10).rolling(10).std()
        
        return df
    
    def calculate_rsi(self, prices: pd.Series, period: int = 14) -> pd.Series:
        """Calcula el RSI"""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi
    
    def calculate_atr(self, data: pd.DataFrame, period: int = 14) -> pd.Series:
        """Calcula el ATR"""
        tr = self.calculate_true_range(data)
        atr = tr.rolling(window=period).mean()
        return atr
    
    def calculate_true_range(self, data: pd.DataFrame) -> pd.Series:
        """Calcula el True Range"""
        high_low = data['high'] - data['low']
        high_close = abs(data['high'] - data['close'].shift())
        low_close = abs(data['low'] - data['close'].shift())
        tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
        return tr
    
    def _create_feature_matrix(self, data: pd.DataFrame) -> Tuple[np.ndarray, List[str]]:
        """Crea la matriz de features para ML"""
        exclude_cols = ['open', 'high', 'low', 'close', 'tick_volume', 'spread', 'real_volume',
                       'future_return', 'target_direction', 'future_volatility']
        
        feature_cols = [col for col in data.columns if col not in exclude_cols and not col.startswith('sma_') and not col.startswith('ema_')]
        
        important_features = []
        important_features.extend([f'return_{p}' for p in [1, 3, 5, 10, 20] if f'return_{p}' in feature_cols])
        important_features.extend([f'rsi_{p}' for p in [7, 14, 21] if f'rsi_{p}' in feature_cols])
        important_features.extend(['macd', 'macd_signal', 'macd_hist', 'bb_position'] if 'macd' in feature_cols else [])
        important_features.extend(['dist_sma_20', 'dist_sma_50'] if 'dist_sma_20' in feature_cols else [])
        important_features.extend([f'atr_{p}' for p in [7, 14, 21] if f'atr_{p}' in feature_cols])
        important_features.extend([f'volatility_{p}' for p in [10, 20, 30] if f'volatility_{p}' in feature_cols])
        important_features.extend(['tr_normalized', 'hl_ratio'] if 'tr_normalized' in feature_cols else [])
        
        if 'volume_ratio' in feature_cols:
            important_features.extend(['volume_ratio'])
        
        important_features.extend(['body_pct', 'is_doji', 'bullish_engulfing', 'bearish_engulfing'] 
                                  if 'body_pct' in feature_cols else [])
        important_features.extend(['up_streak', 'down_streak'] if 'up_streak' in feature_cols else [])
        important_features.extend(['trend_strength', 'regime_volatility', 'autocorr'] 
                                  if 'trend_strength' in feature_cols else [])
        
        available_features = [f for f in important_features if f in data.columns]
        X = data[available_features].values
        
        return X, available_features
    
    def train_models(self, data: pd.DataFrame) -> bool:
        """Entrena los modelos de ML"""
        try:
            X, feature_names = self._create_feature_matrix(data)
            y_direction = data['target_direction'].values
            y_volatility = data['future_volatility'].values
            
            mask = ~(np.isnan(X).any(axis=1) | np.isnan(y_direction) | np.isnan(y_volatility))
            X_clean = X[mask]
            y_dir_clean = y_direction[mask]
            y_vol_clean = y_volatility[mask]
            
            if len(X_clean) < self.min_train_samples:
                logger.warning(f"Insuficientes muestras para entrenar: {len(X_clean)}")
                return False
            
            X_scaled = self.scaler.fit_transform(X_clean)
            
            clear_direction = y_dir_clean != 0
            X_dir = X_scaled[clear_direction]
            y_dir = y_dir_clean[clear_direction]
            
            if len(X_dir) < 100:
                logger.warning("Insuficientes señales claras para entrenar")
                return False
            
            models = []
            
            rf_model = RandomForestClassifier(
                n_estimators=100,
                max_depth=10,
                min_samples_split=20,
                min_samples_leaf=10,
                random_state=42,
                n_jobs=-1
            )
            rf_model.fit(X_dir, y_dir)
            models.append(('rf', rf_model))
            
            if XGBOOST_AVAILABLE:
                xgb_model = xgb.XGBClassifier(
                    n_estimators=100,
                    max_depth=6,
                    learning_rate=0.1,
                    random_state=42,
                    n_jobs=-1
                )
                xgb_model.fit(X_dir, y_dir)
                models.append(('xgb', xgb_model))
            
            if LIGHTGBM_AVAILABLE:
                lgb_model = lgb.LGBMClassifier(
                    n_estimators=100,
                    max_depth=6,
                    learning_rate=0.1,
                    random_state=42,
                    n_jobs=-1,
                    verbose=-1
                )
                lgb_model.fit(X_dir, y_dir)
                models.append(('lgb', lgb_model))
            
            self.direction_model = models
            
            vol_model = GradientBoostingRegressor(
                n_estimators=100,
                max_depth=5,
                learning_rate=0.1,
                random_state=42
            )
            vol_model.fit(X_scaled, y_vol_clean)
            self.volatility_model = vol_model
            
            self.is_trained = True
            self.bars_since_train = 0
            
            logger.info(f"Modelos entrenados exitosamente con {len(X_clean)} muestras")
            return True
            
        except Exception as e:
            logger.error(f"Error al entrenar modelos: {e}")
            return False
    
    def predict_direction(self, features: np.ndarray) -> Tuple[int, float]:
        """Predice la dirección del mercado"""
        if not self.is_trained or self.direction_model is None:
            return 0, 0.0
        
        try:
            features_scaled = self.scaler.transform(features.reshape(1, -1))
            
            predictions = []
            probabilities = []
            
            for name, model in self.direction_model:
                pred = model.predict(features_scaled)[0]
                
                if hasattr(model, 'predict_proba'):
                    proba = model.predict_proba(features_scaled)[0]
                    conf = max(proba)
                else:
                    conf = 0.6
                
                predictions.append(pred)
                probabilities.append(conf)
            
            final_prediction = int(np.median(predictions))
            final_confidence = np.mean(probabilities)
            
            return final_prediction, final_confidence
            
        except Exception as e:
            logger.error(f"Error en predicción: {e}")
            return 0, 0.0
    
    def predict_volatility(self, features: np.ndarray) -> float:
        """Predice la volatilidad futura"""
        if not self.is_trained or self.volatility_model is None:
            return 0.01
        
        try:
            features_scaled = self.scaler.transform(features.reshape(1, -1))
            volatility = self.volatility_model.predict(features_scaled)[0]
            return max(volatility, 0.0001)
        except Exception as e:
            logger.error(f"Error en predicción de volatilidad: {e}")
            return 0.01
    
    def detect_market_regime(self, data: pd.DataFrame) -> str:
        """Detecta el régimen actual del mercado"""
        if len(data) < self.regime_window:
            return 'neutral'
        
        recent_data = data.iloc[-self.regime_window:]
        
        trend = recent_data['close'].iloc[-1] - recent_data['close'].iloc[0]
        trend_pct = trend / recent_data['close'].iloc[0]
        
        volatility = recent_data['return_1'].std()
        
        if volatility > self.max_volatility:
            return 'high_vol'
        elif abs(trend_pct) < 0.02:
            return 'ranging'
        elif trend_pct > 0.02:
            return 'trending_up'
        else:
            return 'trending_down'
    
    def generate_signals(self, data: pd.DataFrame) -> List[Signal]:
        """
        Genera señales de trading usando ML
        
        IMPORTANTE: Retorna List[Signal] compatible con tu base_strategy.py
        """
        signals = []
        
        # Entrenar o reentrenar modelos
        if not self.is_trained:
            if len(data) >= self.min_train_samples:
                self.train_models(data)
        elif self.bars_since_train >= self.retrain_frequency:
            self.train_models(data)
        
        if not self.is_trained:
            return signals
        
        # Detectar régimen de mercado
        if self.detect_regime:
            self.current_regime = self.detect_market_regime(data)
        
        # Generar features
        X, feature_names = self._create_feature_matrix(data)
        
        # Generar señales para cada barra
        for i in range(len(data)):
            if i < self.lookback_period:
                continue
            
            features = X[i]
            
            if np.isnan(features).any():
                continue
            
            direction, confidence = self.predict_direction(features)
            
            current_bar = data.iloc[i]
            
            # Filtros
            if 'atr_14' in current_bar.index:
                current_vol = current_bar['atr_14'] / current_bar['close']
                if current_vol < self.min_volatility or current_vol > self.max_volatility:
                    continue
            
            if 'volume_ratio' in current_bar.index:
                if current_bar['volume_ratio'] < self.min_volume_ratio:
                    continue
            
            if confidence < self.prediction_threshold:
                continue
            
            if self.detect_regime:
                if self.current_regime == 'high_vol':
                    continue
                
                if self.current_regime == 'trending_up' and direction == -1:
                    continue
                elif self.current_regime == 'trending_down' and direction == 1:
                    continue
            
            # Crear señal compatible con Signal class
            if direction == 1:
                signal_type = 'BUY'
            elif direction == -1:
                signal_type = 'SELL'
            else:
                continue
            
            # Calcular stop loss y take profit
            atr = current_bar.get('atr_14', current_bar['close'] * 0.01)
            
            # Ajustar stops dinámicamente si es posible
            if self.use_dynamic_stops and self.is_trained:
                predicted_vol = self.predict_volatility(features)
                vol_adjustment = predicted_vol / data['return_1'].iloc[:i+1].std()
                adjusted_multiplier = self.atr_multiplier * (1 + vol_adjustment)
                stop_distance = atr * adjusted_multiplier
            else:
                stop_distance = atr * self.atr_multiplier
            
            if signal_type == 'BUY':
                stop_loss = current_bar['close'] - stop_distance
                take_profit = current_bar['close'] + (stop_distance * 2)
            else:
                stop_loss = current_bar['close'] + stop_distance
                take_profit = current_bar['close'] - (stop_distance * 2)
            
            # Crear señal compatible
            signal = Signal(
                timestamp=current_bar.name if hasattr(current_bar.name, 'timestamp') else datetime.now(),
                signal_type=signal_type,
                price=float(current_bar['close']),
                stop_loss=float(stop_loss),
                take_profit=float(take_profit),
                position_size=0.01,  # Será ajustado por manage_risk
                metadata={
                    'confidence': float(confidence),
                    'direction': int(direction),
                    'regime': self.current_regime,
                    'volatility': float(predicted_vol) if self.use_dynamic_stops and self.is_trained else 0.0
                }
            )
            
            signals.append(signal)
            
            self.bars_since_train += 1
        
        logger.info(f"MLAdvancedStrategy generó {len(signals)} señales")
        return signals
    
    def get_strategy_info(self) -> Dict:
        """Retorna información de la estrategia"""
        info = {
            'name': 'ML Advanced Strategy',
            'description': 'Estrategia avanzada con ensemble de modelos ML',
            'version': '1.0.0 - Compatible',
            'type': 'Machine Learning',
            'parameters': self.parameters,
            'is_trained': self.is_trained,
            'current_regime': self.current_regime,
            'models': []
        }
        
        if self.is_trained and self.direction_model:
            info['models'] = [name for name, _ in self.direction_model]
            if self.volatility_model:
                info['models'].append('volatility_predictor')
        
        return info