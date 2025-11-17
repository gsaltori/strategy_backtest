"""
Ejemplo Completo: Backtesting y Optimización ML
Estrategia NY Range Breakout para XAUUSD

Este script demuestra:
1. Cómo cargar datos de XAUUSD
2. Ejecutar backtest de la estrategia
3. Analizar resultados
4. Optimizar parámetros con ML
5. Generar reportes completos

Autor: Sistema de Backtesting
Fecha: 2024
"""

import sys
import logging
from datetime import datetime, timedelta
import pandas as pd
import numpy as np

# Importar módulos del sistema
from data_manager import MT5DataManager
from backtest_engine import BacktestEngine
from config.settings import MT5Config, BacktestConfig
from analysis.reporting import ReportGenerator
from analysis.performance import PerformanceAnalyzer

# Importar la estrategia
from strategies.ny_range_breakout_strategy import NYRangeBreakout

# Importar optimizador ML (si está disponible)
try:
    from ml_optimizer import MLStrategyOptimizer
    ML_AVAILABLE = True
except ImportError:
    ML_AVAILABLE = False
    print("⚠️ ML Optimizer no disponible. Instala scikit-learn para usar optimización ML")

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def generate_sample_xauusd_data(days=365, start_price=2000.0) -> pd.DataFrame:
    """
    Genera datos de muestra para XAUUSD
    
    Args:
        days: Número de días de datos
        start_price: Precio inicial
        
    Returns:
        DataFrame con datos OHLC simulados
    """
    print("\n📊 Generando datos de muestra para XAUUSD...")
    
    # Generar timestamps (barras de 5 minutos)
    bars_per_day = 288  # 24 * 60 / 5 = 288 barras de 5 min
    total_bars = days * bars_per_day
    dates = pd.date_range(
        end=datetime.now(),
        periods=total_bars,
        freq='5min'
    )
    
    # Simular precio con tendencia y volatilidad realista
    np.random.seed(42)
    
    # Tendencia alcista suave
    trend = np.linspace(0, 100, total_bars)
    
    # Volatilidad diaria (más alta en sesión NY)
    volatility = np.ones(total_bars) * 0.0005
    for i, dt in enumerate(dates):
        hour = dt.hour
        # Mayor volatilidad en horario NY (14:00-22:00 UTC)
        if 14 <= hour <= 22:
            volatility[i] *= 1.5
    
    # Generar precios
    returns = np.random.normal(0.0001, volatility)
    prices = start_price + trend + np.cumsum(returns * start_price)
    
    # Crear OHLC
    data = pd.DataFrame({
        'open': prices,
        'high': prices * (1 + np.abs(np.random.normal(0, 0.0003, total_bars))),
        'low': prices * (1 - np.abs(np.random.normal(0, 0.0003, total_bars))),
        'close': prices * (1 + np.random.normal(0, 0.0002, total_bars)),
        'tick_volume': np.random.randint(100, 1000, total_bars),
        'spread': 20,  # Spread típico de XAUUSD en pips
        'real_volume': np.random.randint(1000, 10000, total_bars)
    }, index=dates)
    
    # Asegurar que high >= open, close y low <= open, close
    data['high'] = data[['open', 'high', 'close']].max(axis=1)
    data['low'] = data[['open', 'low', 'close']].min(axis=1)
    
    print(f"✅ Generados {len(data)} barras de 5 minutos ({days} días)")
    print(f"   Rango de precios: {data['low'].min():.2f} - {data['high'].max():.2f}")
    print(f"   Período: {data.index[0]} a {data.index[-1]}")
    
    return data


def load_mt5_data() -> pd.DataFrame:
    """
    Carga datos reales desde MetaTrader 5
    
    Returns:
        DataFrame con datos OHLC
    """
    print("\n📊 Cargando datos desde MetaTrader 5...")
    
    # Configurar MT5
    config = MT5Config()
    data_manager = MT5DataManager(config)
    
    try:
        # Conectar
        if not data_manager.connect():
            raise Exception("No se pudo conectar a MT5")
        
        # Validar símbolo
        symbol_info = data_manager.validate_symbol("XAUUSD")
        if not symbol_info:
            raise Exception("XAUUSD no disponible")
        
        # Descargar datos (1 año de datos de 5 minutos)
        data = data_manager.get_historical_data(
            symbol="XAUUSD",
            timeframe="M5",
            start_date=datetime.now() - timedelta(days=365),
            count=100000  # Suficientes barras para 1 año
        )
        
        print(f"✅ Datos cargados: {len(data)} barras")
        print(f"   Período: {data.index[0]} a {data.index[-1]}")
        
        return data, symbol_info
        
    finally:
        data_manager.disconnect()


def run_simple_backtest(use_mt5_data: bool = False):
    """
    Ejecuta un backtest simple con parámetros por defecto
    
    Args:
        use_mt5_data: Si True, usa datos de MT5; si False, usa datos de muestra
    """
    print("\n" + "="*80)
    print("🚀 BACKTEST SIMPLE - NY RANGE BREAKOUT")
    print("="*80)
    
    # Cargar datos
    if use_mt5_data:
        try:
            data, symbol_info = load_mt5_data()
        except Exception as e:
            print(f"⚠️ Error al cargar datos de MT5: {e}")
            print("   Usando datos de muestra...")
            data = generate_sample_xauusd_data(days=365)
            symbol_info = {
                'point': 0.01,
                'digits': 2,
                'trade_contract_size': 100.0,
                'volume_min': 0.01,
                'volume_max': 100.0,
                'volume_step': 0.01
            }
    else:
        data = generate_sample_xauusd_data(days=365)
        symbol_info = {
            'point': 0.01,
            'digits': 2,
            'trade_contract_size': 100.0,
            'volume_min': 0.01,
            'volume_max': 100.0,
            'volume_step': 0.01
        }
    
    # Crear estrategia con parámetros por defecto
    print("\n📈 Creando estrategia NY Range Breakout...")
    strategy = NYRangeBreakout(
        range_start_hour=21,
        range_start_minute=50,
        range_end_hour=22,
        range_end_minute=15,
        stop_loss_pips=34.0,
        take_profit_pips=83.0,
        timezone='America/New_York',
        pip_value=0.10,
        min_range_pips=5.0,
        max_trades_per_day=1,
        use_trailing_stop=True,         # Activar trailing stop
        trailing_stop_pips=20.0,        # 20 pips de trailing
        trailing_activation_pips=30.0   # Activar tras 30 pips de ganancia
    )
    
    # Configurar backtest
    config = BacktestConfig(
        initial_capital=10000.0,
        commission_pct=0.0001,  # 0.01% comisión
        slippage_pct=0.0005,    # 0.05% slippage
        use_spread=True
    )
    
    # Ejecutar backtest
    print("\n⚙️ Ejecutando backtest...")
    engine = BacktestEngine(config)
    result = engine.run(strategy, data, symbol_info)
    
    # Mostrar resumen
    print("\n" + "="*80)
    print("📊 RESULTADOS DEL BACKTEST")
    print("="*80)
    print(result.summary())
    
    # Generar reportes
    print("\n📄 Generando reportes...")
    report_gen = ReportGenerator(result)
    
    html_path = report_gen.save_report_html('ny_range_backtest_report.html')
    print(f"✅ Reporte HTML guardado: {html_path}")
    
    # Nota: save_charts_html no está disponible en ReportGenerator
    # Los gráficos ya están incluidos en el reporte principal
    print(f"✅ Gráficos incluidos en el reporte principal")
    
    # Análisis adicional
    if len(result.trades) > 0:
        analyzer = PerformanceAnalyzer(
            trades=result.trades,
            equity_curve=result.equity_curve,
            initial_capital=config.initial_capital
        )
        
        print("\n📊 ANÁLISIS ADICIONAL:")
        print(f"   Sortino Ratio: {analyzer._calculate_sortino_ratio():.2f}")
        print(f"   Omega Ratio: {analyzer._calculate_omega_ratio():.2f}")
        print(f"   Max Consecutive Wins: {analyzer._calculate_max_consecutive_wins()}")
        print(f"   Max Consecutive Losses: {analyzer._calculate_max_consecutive_losses()}")
    else:
        print("\n⚠️ No se ejecutaron trades - Sin métricas adicionales")
    
    return result


def run_parameter_optimization(use_mt5_data: bool = False):
    """
    Ejecuta optimización de parámetros con Machine Learning
    
    Args:
        use_mt5_data: Si True, usa datos de MT5; si False, usa datos de muestra
    """
    if not ML_AVAILABLE:
        print("\n⚠️ Optimización ML no disponible")
        print("   Instala scikit-learn: pip install scikit-learn")
        return
    
    print("\n" + "="*80)
    print("🤖 OPTIMIZACIÓN ML - NY RANGE BREAKOUT")
    print("="*80)
    
    # Cargar datos
    if use_mt5_data:
        try:
            data, symbol_info = load_mt5_data()
        except Exception as e:
            print(f"⚠️ Error al cargar datos de MT5: {e}")
            print("   Usando datos de muestra...")
            data = generate_sample_xauusd_data(days=365)
            symbol_info = {
                'point': 0.01,
                'digits': 2,
                'trade_contract_size': 100.0,
                'volume_min': 0.01,
                'volume_max': 100.0,
                'volume_step': 0.01
            }
    else:
        data = generate_sample_xauusd_data(days=365)
        symbol_info = {
            'point': 0.01,
            'digits': 2,
            'trade_contract_size': 100.0,
            'volume_min': 0.01,
            'volume_max': 100.0,
            'volume_step': 0.01
        }
    
    # Crear optimizador ML
    print("\n🤖 Inicializando optimizador ML...")
    optimizer = MLStrategyOptimizer(
        strategy_class=NYRangeBreakout,
        data=data,
        symbol_info=symbol_info,
        target_metric='sharpe_ratio',
        n_iterations=50,
        cv_splits=5,
        validation_pct=0.3
    )
    
    # Ejecutar optimización
    print("\n⚙️ Ejecutando optimización Bayesiana...")
    print("   Esto puede tomar varios minutos...")
    
    result = optimizer.bayesian_optimization()
    
    # Mostrar resultados
    print("\n" + "="*80)
    print("📊 RESULTADOS DE LA OPTIMIZACIÓN")
    print("="*80)
    
    print("\n🏆 MEJORES PARÁMETROS ENCONTRADOS:")
    for param, value in result.best_params.items():
        print(f"   {param}: {value:.2f}")
    
    print(f"\n📈 MÉTRICAS:")
    print(f"   Mejor Score (train): {result.validation_metrics['train_score']:.4f}")
    print(f"   Score (validation): {result.validation_metrics['validation_score']:.4f}")
    print(f"   Ratio Overfitting: {result.validation_metrics['overfit_ratio']:.2f}")
    print(f"   Iteraciones: {result.validation_metrics['n_iterations']}")
    
    print("\n🔍 IMPORTANCIA DE PARÁMETROS:")
    for param, importance in sorted(result.feature_importance.items(), 
                                    key=lambda x: x[1], reverse=True):
        print(f"   {param}: {importance:.4f}")
    
    # Guardar resultados
    results_path = 'ny_range_optimization_results.csv'
    result.all_results.to_csv(results_path, index=False)
    print(f"\n✅ Resultados guardados: {results_path}")
    
    # Ejecutar backtest con mejores parámetros
    print("\n🔄 Ejecutando backtest con parámetros optimizados...")
    
    best_strategy = NYRangeBreakout(**result.best_params)
    config = BacktestConfig(
        initial_capital=10000.0,
        commission_pct=0.0001,
        slippage_pct=0.0005,
        use_spread=True
    )
    
    engine = BacktestEngine(config)
    optimized_result = engine.run(best_strategy, data, symbol_info)
    
    print("\n📊 RESULTADOS CON PARÁMETROS OPTIMIZADOS:")
    print(optimized_result.summary())
    
    # Generar reportes
    report_gen = ReportGenerator(optimized_result)
    report_gen.save_report_html('ny_range_optimized_report.html')
    print("\n✅ Reportes generados (gráficos incluidos en el reporte principal)")
    
    print("\n✅ Optimización completada!")
    
    return result, optimized_result


def run_walk_forward_analysis(use_mt5_data: bool = False):
    """
    Ejecuta Walk-Forward Analysis para validación robusta
    
    Args:
        use_mt5_data: Si True, usa datos de MT5; si False, usa datos de muestra
    """
    if not ML_AVAILABLE:
        print("\n⚠️ Walk-Forward Analysis requiere ML optimizer")
        return
    
    print("\n" + "="*80)
    print("🔄 WALK-FORWARD ANALYSIS - NY RANGE BREAKOUT")
    print("="*80)
    
    # Cargar datos
    if use_mt5_data:
        try:
            data, symbol_info = load_mt5_data()
        except Exception as e:
            print(f"⚠️ Error al cargar datos de MT5: {e}")
            print("   Usando datos de muestra...")
            data = generate_sample_xauusd_data(days=730)  # 2 años para WF
            symbol_info = {
                'point': 0.01,
                'digits': 2,
                'trade_contract_size': 100.0,
                'volume_min': 0.01,
                'volume_max': 100.0,
                'volume_step': 0.01
            }
    else:
        data = generate_sample_xauusd_data(days=730)  # 2 años
        symbol_info = {
            'point': 0.01,
            'digits': 2,
            'trade_contract_size': 100.0,
            'volume_min': 0.01,
            'volume_max': 100.0,
            'volume_step': 0.01
        }
    
    # Configurar WF Analysis
    print("\n📊 Configurando Walk-Forward Analysis...")
    print("   Training window: 3 meses")
    print("   Testing window: 1 mes")
    print("   Re-optimización cada mes")
    
    optimizer = MLStrategyOptimizer(
        strategy_class=NYRangeBreakout,
        data=data,
        symbol_info=symbol_info,
        target_metric='sharpe_ratio',
        n_iterations=30,  # Menos iteraciones por ventana
        cv_splits=3
    )
    
    # Ejecutar WF
    print("\n⚙️ Ejecutando Walk-Forward Analysis...")
    print("   Esto puede tomar bastante tiempo...")
    
    wf_result = optimizer.walk_forward_optimization(
        train_period_months=3,
        test_period_months=1,
        step_months=1
    )
    
    # Mostrar resultados
    print("\n" + "="*80)
    print("📊 RESULTADOS WALK-FORWARD")
    print("="*80)
    
    print(f"\n📈 ESTADÍSTICAS GENERALES:")
    print(f"   Ventanas analizadas: {len(wf_result['windows'])}")
    print(f"   Sharpe promedio (in-sample): {wf_result['avg_train_score']:.4f}")
    print(f"   Sharpe promedio (out-sample): {wf_result['avg_test_score']:.4f}")
    print(f"   Ratio degradación: {wf_result['degradation_ratio']:.2f}")
    print(f"   Consistencia: {wf_result['consistency']:.2f}")
    
    # Guardar resultados detallados
    wf_df = pd.DataFrame(wf_result['windows'])
    wf_df.to_csv('ny_range_walkforward_results.csv', index=False)
    print(f"\n✅ Resultados WF guardados: ny_range_walkforward_results.csv")
    
    return wf_result


def main():
    """Función principal con menú interactivo"""
    print("\n" + "="*80)
    print("🎯 NY RANGE BREAKOUT - SISTEMA DE BACKTESTING Y OPTIMIZACIÓN")
    print("="*80)
    
    print("\nEstrategia: Breakout del Rango NY para XAUUSD")
    print("Horario: 21:50 - 22:15 hora Nueva York")
    print("SL: 34 pips | TP: 83 pips")
    
    print("\n📋 OPCIONES DISPONIBLES:")
    print("1. Backtest simple con datos de muestra")
    print("2. Backtest con datos de MT5 (requiere MT5 instalado)")
    print("3. Optimización ML con datos de muestra")
    print("4. Optimización ML con datos de MT5")
    print("5. Walk-Forward Analysis (datos de muestra)")
    print("6. Walk-Forward Analysis (datos de MT5)")
    print("7. Ejecutar todo (recomendado para primera vez)")
    print("0. Salir")
    
    while True:
        try:
            choice = input("\n🔹 Selecciona una opción (0-7): ").strip()
            
            if choice == '0':
                print("\n👋 ¡Hasta luego!")
                break
                
            elif choice == '1':
                run_simple_backtest(use_mt5_data=False)
                
            elif choice == '2':
                run_simple_backtest(use_mt5_data=True)
                
            elif choice == '3':
                run_parameter_optimization(use_mt5_data=False)
                
            elif choice == '4':
                run_parameter_optimization(use_mt5_data=True)
                
            elif choice == '5':
                run_walk_forward_analysis(use_mt5_data=False)
                
            elif choice == '6':
                run_walk_forward_analysis(use_mt5_data=True)
                
            elif choice == '7':
                print("\n🚀 Ejecutando análisis completo...")
                print("\n📊 Paso 1/3: Backtest Simple")
                run_simple_backtest(use_mt5_data=False)
                
                if ML_AVAILABLE:
                    print("\n📊 Paso 2/3: Optimización ML")
                    run_parameter_optimization(use_mt5_data=False)
                    
                    print("\n📊 Paso 3/3: Walk-Forward Analysis")
                    run_walk_forward_analysis(use_mt5_data=False)
                
                print("\n✅ ¡Análisis completo finalizado!")
                
            else:
                print("❌ Opción inválida. Por favor elige 0-7.")
                
        except KeyboardInterrupt:
            print("\n\n👋 Interrumpido por el usuario. ¡Hasta luego!")
            break
        except Exception as e:
            logger.error(f"Error: {e}", exc_info=True)
            print(f"\n❌ Error: {e}")
            print("   Por favor intenta otra opción.")


if __name__ == "__main__":
    main()