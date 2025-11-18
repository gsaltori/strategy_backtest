"""
Script de Ejecución y Prueba de Estrategia ML - VERSIÓN COMPLETA CON MT5

Este script permite:
1. Ejecutar backtests con la estrategia ML
2. Comparar con otras estrategias
3. Generar reportes de rendimiento
4. Analizar feature importance
5. Usar datos REALES de MetaTrader 5

Versión: Compatible con tu estructura de proyecto + MT5
"""

import sys
import os
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import logging

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Importar módulos del proyecto
try:
    from strategies.ml_advanced_strategy import MLAdvancedStrategy
    from backtest_engine import BacktestEngine
    from config.settings import BacktestConfig
except ImportError as e:
    logger.error(f"Error al importar módulos: {e}")
    print("\n❌ Error: Asegúrate de que todos los módulos estén en el directorio correcto")
    sys.exit(1)


def generate_sample_data(days: int = 365, bars_per_day: int = 24) -> pd.DataFrame:
    """
    Genera datos de muestra para testing (XAUUSD simulado)
    
    Args:
        days: Número de días de datos
        bars_per_day: Barras por día (24 = horario)
        
    Returns:
        DataFrame con datos OHLCV
    """
    logger.info(f"Generando {days} días de datos de muestra...")
    
    total_bars = days * bars_per_day
    
    # Generar fechas
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    dates = pd.date_range(start=start_date, end=end_date, periods=total_bars)
    
    # Precio base XAUUSD
    base_price = 2000.0
    
    # Generar precio con tendencia y ruido
    trend = np.linspace(0, 200, total_bars)
    noise = np.random.randn(total_bars) * 10
    cycles = 50 * np.sin(np.linspace(0, 20 * np.pi, total_bars))
    
    close = base_price + trend + noise + cycles
    
    # Generar OHLC
    high = close + abs(np.random.randn(total_bars) * 5)
    low = close - abs(np.random.randn(total_bars) * 5)
    open_price = close + np.random.randn(total_bars) * 3
    
    # Volumen
    volume = np.random.randint(1000, 5000, total_bars)
    
    # Crear DataFrame
    data = pd.DataFrame({
        'open': open_price,
        'high': high,
        'low': low,
        'close': close,
        'tick_volume': volume,
        'spread': np.ones(total_bars) * 2,
        'real_volume': volume
    }, index=dates)
    
    logger.info(f"✅ Datos generados: {len(data)} barras desde {data.index[0]} hasta {data.index[-1]}")
    
    return data


def load_mt5_data(symbol: str = "XAUUSD", days: int = 365, timeframe_str: str = "H1"):
    """
    Carga datos REALES desde MetaTrader 5
    
    Args:
        symbol: Símbolo a descargar (ej: XAUUSD, EURUSD)
        days: Número de días históricos
        timeframe_str: Timeframe (M1, M5, M15, M30, H1, H4, D1)
        
    Returns:
        Tupla de (data, symbol_info) o (None, None) si falla
    """
    try:
        import MetaTrader5 as mt5
        from data_manager import MT5DataManager
    except ImportError as e:
        logger.error(f"Error al importar MT5: {e}")
        print("\n❌ Error: MetaTrader5 no está instalado")
        print("   Instala con: pip install MetaTrader5")
        return None, None
    
    logger.info(f"Conectando a MetaTrader 5...")
    
    # Crear data manager
    data_manager = MT5DataManager()
    
    # Conectar
    if not data_manager.connect():
        logger.error("No se pudo conectar a MT5")
        print("\n❌ Error: No se pudo conectar a MetaTrader 5")
        print("   Verifica que:")
        print("   1. MT5 está abierto y funcionando")
        print("   2. Tienes una cuenta activa (demo o real)")
        print("   3. No hay otro programa usando MT5")
        return None, None
    
    logger.info("✅ Conectado a MT5")
    
    # Mapear timeframe string a constante MT5
    timeframe_map = {
        'M1': mt5.TIMEFRAME_M1,
        'M5': mt5.TIMEFRAME_M5,
        'M15': mt5.TIMEFRAME_M15,
        'M30': mt5.TIMEFRAME_M30,
        'H1': mt5.TIMEFRAME_H1,
        'H4': mt5.TIMEFRAME_H4,
        'D1': mt5.TIMEFRAME_D1,
        'W1': mt5.TIMEFRAME_W1,
    }
    
    timeframe = timeframe_map.get(timeframe_str.upper(), mt5.TIMEFRAME_H1)
    
    # Calcular fechas
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    
    logger.info(f"Descargando datos de {symbol} ({timeframe_str})...")
    logger.info(f"Período: {start_date.strftime('%Y-%m-%d')} a {end_date.strftime('%Y-%m-%d')}")
    
    # Descargar datos - usar count en lugar de end_date
    # Calcular número aproximado de barras según timeframe
    bars_per_day = {
        'M1': 1440, 'M5': 288, 'M15': 96, 'M30': 48,
        'H1': 24, 'H4': 6, 'D1': 1, 'W1': 1
    }
    
    timeframe_upper = timeframe_str.upper()
    bars_mult = bars_per_day.get(timeframe_upper, 24)
    count = days * bars_mult
    
    data = data_manager.get_historical_data(
        symbol=symbol,
        timeframe=timeframe_str,
        start_date=start_date,
        count=count  # Usar count en lugar de end_date
    )
    
    if data is None or len(data) == 0:
        logger.error(f"No se pudieron descargar datos de {symbol}")
        print(f"\n❌ Error: No se pudieron descargar datos de {symbol}")
        print("   Verifica que:")
        print(f"   1. El símbolo '{symbol}' existe en tu broker")
        print(f"   2. El símbolo está en 'Market Watch'")
        print(f"   3. Tienes datos históricos disponibles")
        data_manager.disconnect()
        return None, None
    
    logger.info(f"✅ Datos descargados: {len(data)} barras")
    
    # Obtener información del símbolo
    symbol_info = data_manager.get_symbol_info(symbol)
    
    if symbol_info is None:
        logger.error(f"No se pudo obtener información de {symbol}")
        data_manager.disconnect()
        return None, None
    
    logger.info(f"✅ Información del símbolo obtenida")
    
    # Desconectar
    data_manager.disconnect()
    logger.info("✅ Desconectado de MT5")
    
    return data, symbol_info


def run_ml_backtest(
    data: pd.DataFrame,
    config: BacktestConfig,
    symbol_info: dict,
    strategy_params: dict = None,
    data_source: str = "muestra"
):
    """
    Ejecuta un backtest con la estrategia ML
    
    Args:
        data: Datos históricos
        config: Configuración del backtest
        symbol_info: Información del símbolo
        strategy_params: Parámetros de la estrategia (opcional)
        data_source: Fuente de datos ("muestra" o "MT5")
        
    Returns:
        Resultado del backtest
    """
    logger.info("="*80)
    logger.info(f"INICIANDO BACKTEST CON ESTRATEGIA ML - DATOS: {data_source.upper()}")
    logger.info("="*80)
    
    # Crear estrategia con parámetros
    if strategy_params:
        strategy = MLAdvancedStrategy(**strategy_params)
    else:
        strategy = MLAdvancedStrategy(
            prediction_threshold=0.50,      # Más permisivo
            min_train_samples=300,          # Menos restrictivo
            risk_per_trade=0.02,
            max_positions=3,
            use_dynamic_stops=True,
            min_volatility=0.0001,          # Filtro relajado
            max_volatility=0.10,
            min_volume_ratio=0.3,           # Filtro relajado
            detect_regime=False             # Desactivar para más trades
        )
    
    logger.info(f"Estrategia creada: {strategy.name}")
    logger.info(f"Parámetros: {strategy.parameters}")
    
    # Crear motor de backtest
    engine = BacktestEngine(config)
    
    # Ejecutar backtest
    logger.info("\nEjecutando backtest...")
    logger.info(f"Total de barras: {len(data)}")
    logger.info(f"Período: {data.index[0]} a {data.index[-1]}")
    
    result = engine.run(strategy, data, symbol_info)
    
    # Debug: verificar entrenamiento
    logger.info(f"\n🔍 DEBUG:")
    logger.info(f"   Modelo entrenado: {strategy.is_trained}")
    if strategy.is_trained:
        logger.info(f"   Modelos ML: {[name for name, _ in strategy.direction_model]}")
        logger.info(f"   Régimen actual: {strategy.current_regime}")
    
    # Mostrar resumen
    logger.info("\n" + "="*80)
    logger.info("RESUMEN DE RESULTADOS")
    logger.info("="*80)
    
    metrics = result.metrics
    total_return = (result.final_capital / result.initial_capital) - 1
    
    print(f"\n📊 RESULTADOS DEL BACKTEST ML")
    print(f"{'='*60}")
    print(f"Fuente de Datos: {data_source.upper()}")
    print(f"Período: {data.index[0].strftime('%Y-%m-%d')} a {data.index[-1].strftime('%Y-%m-%d')}")
    print(f"Total Barras: {len(data)}")
    print(f"\nTotal de Operaciones: {metrics.get('total_trades', 0)}")
    print(f"Operaciones Ganadoras: {metrics.get('winning_trades', 0)}")
    print(f"Operaciones Perdedoras: {metrics.get('losing_trades', 0)}")
    print(f"Win Rate: {metrics.get('win_rate', 0)*100:.2f}%")
    print(f"\nRetorno Total: {total_return*100:.2f}%")
    print(f"Profit Factor: {metrics.get('profit_factor', 0):.2f}")
    print(f"Sharpe Ratio: {metrics.get('sharpe_ratio', 0):.2f}")
    print(f"Max Drawdown: {metrics.get('max_drawdown', 0)*100:.2f}%")
    print(f"\nCapital Inicial: ${result.initial_capital:,.2f}")
    print(f"Capital Final: ${result.final_capital:,.2f}")
    print(f"Ganancia Neta: ${result.final_capital - result.initial_capital:,.2f}")
    print(f"{'='*60}")
    
    if metrics.get('total_trades', 0) == 0:
        print("\n⚠️  ADVERTENCIA: No se generaron operaciones")
        print("    Posibles causas:")
        print("    1. Datos insuficientes para entrenar el modelo")
        print("    2. Filtros muy estrictos (volatilidad, volumen, régimen)")
        print("    3. Threshold de confianza muy alto")
        print("\n    Sugerencias:")
        print("    - Aumenta la cantidad de datos (días)")
        print("    - Reduce prediction_threshold a 0.45-0.50")
        print("    - Desactiva detect_regime=False")
        print("    - Relaja los filtros de volatilidad")
    
    return result


def compare_strategies(
    data: pd.DataFrame,
    config: BacktestConfig,
    symbol_info: dict,
    data_source: str = "muestra"
):
    """
    Compara la estrategia ML con diferentes configuraciones
    
    Args:
        data: Datos históricos
        config: Configuración del backtest
        symbol_info: Información del símbolo
        data_source: Fuente de datos
        
    Returns:
        DataFrame con comparación de métricas
    """
    logger.info("\n" + "="*80)
    logger.info("COMPARACIÓN DE CONFIGURACIONES ML")
    logger.info("="*80)
    
    results = {}
    
    # 1. Configuración Conservadora
    logger.info("\n1. Ejecutando ML Conservative...")
    ml_conservative = MLAdvancedStrategy(
        prediction_threshold=0.55,
        risk_per_trade=0.01,
        max_positions=2,
        min_volatility=0.0001,
        detect_regime=False
    )
    engine = BacktestEngine(config)
    conservative_result = engine.run(ml_conservative, data, symbol_info)
    results['ML Conservative'] = conservative_result
    
    # 2. Configuración Balanceada (default)
    logger.info("\n2. Ejecutando ML Balanced...")
    ml_balanced = MLAdvancedStrategy(
        prediction_threshold=0.50,
        min_volatility=0.0001,
        detect_regime=False
    )
    engine = BacktestEngine(config)
    balanced_result = engine.run(ml_balanced, data, symbol_info)
    results['ML Balanced'] = balanced_result
    
    # 3. Configuración Agresiva
    logger.info("\n3. Ejecutando ML Aggressive...")
    ml_aggressive = MLAdvancedStrategy(
        prediction_threshold=0.45,
        risk_per_trade=0.03,
        max_positions=5,
        min_volatility=0.0001,
        detect_regime=False
    )
    engine = BacktestEngine(config)
    aggressive_result = engine.run(ml_aggressive, data, symbol_info)
    results['ML Aggressive'] = aggressive_result
    
    # Crear tabla comparativa
    comparison_data = []
    
    for name, result in results.items():
        metrics = result.metrics
        total_return = (result.final_capital / result.initial_capital) - 1
        
        comparison_data.append({
            'Estrategia': name,
            'Trades': metrics.get('total_trades', 0),
            'Win Rate %': f"{metrics.get('win_rate', 0) * 100:.1f}%",
            'Return %': f"{total_return * 100:.1f}%",
            'Sharpe': f"{metrics.get('sharpe_ratio', 0):.2f}",
            'Max DD %': f"{metrics.get('max_drawdown', 0) * 100:.1f}%",
            'Profit Factor': f"{metrics.get('profit_factor', 0):.2f}",
            'Capital Final': f"${result.final_capital:,.0f}"
        })
    
    comparison_df = pd.DataFrame(comparison_data)
    
    logger.info("\n" + "="*80)
    logger.info("TABLA COMPARATIVA")
    logger.info("="*80)
    print("\n")
    print(comparison_df.to_string(index=False))
    print("\n")
    
    return comparison_df


def analyze_feature_importance(
    strategy: MLAdvancedStrategy,
    data: pd.DataFrame
):
    """
    Analiza la importancia de features en el modelo ML
    
    Args:
        strategy: Estrategia ML entrenada
        data: Datos usados para entrenar
        
    Returns:
        DataFrame con feature importance
    """
    if not strategy.is_trained:
        logger.warning("❌ La estrategia no está entrenada. No se puede analizar feature importance.")
        return pd.DataFrame()
    
    logger.info("\n" + "="*80)
    logger.info("ANÁLISIS DE FEATURE IMPORTANCE")
    logger.info("="*80)
    
    try:
        # Calcular indicadores
        data_with_indicators = strategy.calculate_indicators(data)
        
        # Obtener features
        X, feature_names = strategy._create_feature_matrix(data_with_indicators)
        
        # Obtener importancia de los modelos
        importance_scores = []
        
        for model_name, model in strategy.direction_model:
            if hasattr(model, 'feature_importances_'):
                importance_scores.append(model.feature_importances_)
        
        if not importance_scores:
            logger.warning("Los modelos no tienen feature_importances_")
            return pd.DataFrame()
        
        # Promediar importancias
        avg_importance = np.mean(importance_scores, axis=0)
        
        # Crear DataFrame
        importance_df = pd.DataFrame({
            'Feature': feature_names,
            'Importance': avg_importance
        })
        
        # Ordenar por importancia
        importance_df = importance_df.sort_values('Importance', ascending=False)
        
        logger.info("\n📊 Top 20 Features Más Importantes:")
        print("\n")
        print(importance_df.head(20).to_string(index=False))
        print("\n")
        
        return importance_df
        
    except Exception as e:
        logger.error(f"Error en análisis de features: {e}")
        return pd.DataFrame()


def save_results(
    result,
    comparison_df: pd.DataFrame = None,
    importance_df: pd.DataFrame = None,
    output_dir: str = 'ml_backtest_results',
    data_source: str = "muestra"
):
    """
    Guarda los resultados del backtest
    
    Args:
        result: Resultado del backtest
        comparison_df: DataFrame de comparación (opcional)
        importance_df: DataFrame de feature importance (opcional)
        output_dir: Directorio de salida
        data_source: Fuente de datos
    """
    # Crear directorio si no existe
    os.makedirs(output_dir, exist_ok=True)
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    # 1. Guardar trades
    if hasattr(result, 'trades') and len(result.trades) > 0:
        trades_file = os.path.join(output_dir, f'trades_{data_source}_{timestamp}.csv')
        result.trades.to_csv(trades_file, index=False)
        logger.info(f"\n✅ Trades guardados en: {trades_file}")
    
    # 2. Guardar equity curve
    if hasattr(result, 'equity_curve'):
        equity_file = os.path.join(output_dir, f'equity_{data_source}_{timestamp}.csv')
        result.equity_curve.to_csv(equity_file)
        logger.info(f"✅ Equity curve guardada en: {equity_file}")
    
    # 3. Guardar métricas
    metrics_file = os.path.join(output_dir, f'metrics_{data_source}_{timestamp}.txt')
    metrics = result.metrics
    total_return = (result.final_capital / result.initial_capital) - 1
    
    with open(metrics_file, 'w', encoding='utf-8') as f:
        f.write(f"RESULTADOS DEL BACKTEST ML\n")
        f.write(f"Fuente de Datos: {data_source.upper()}\n")
        f.write(f"="*60 + "\n\n")
        f.write(f"Total de Operaciones: {metrics.get('total_trades', 0)}\n")
        f.write(f"Operaciones Ganadoras: {metrics.get('winning_trades', 0)}\n")
        f.write(f"Operaciones Perdedoras: {metrics.get('losing_trades', 0)}\n")
        f.write(f"Win Rate: {metrics.get('win_rate', 0)*100:.2f}%\n\n")
        f.write(f"Retorno Total: {total_return*100:.2f}%\n")
        f.write(f"Profit Factor: {metrics.get('profit_factor', 0):.2f}\n")
        f.write(f"Sharpe Ratio: {metrics.get('sharpe_ratio', 0):.2f}\n")
        f.write(f"Max Drawdown: {metrics.get('max_drawdown', 0)*100:.2f}%\n\n")
        f.write(f"Capital Inicial: ${result.initial_capital:,.2f}\n")
        f.write(f"Capital Final: ${result.final_capital:,.2f}\n")
        f.write(f"Ganancia Neta: ${result.final_capital - result.initial_capital:,.2f}\n")
    logger.info(f"✅ Métricas guardadas en: {metrics_file}")
    
    # 4. Guardar comparación si existe
    if comparison_df is not None:
        comparison_file = os.path.join(output_dir, f'comparison_{data_source}_{timestamp}.csv')
        comparison_df.to_csv(comparison_file, index=False)
        logger.info(f"✅ Comparación guardada en: {comparison_file}")
    
    # 5. Guardar feature importance si existe
    if importance_df is not None:
        importance_file = os.path.join(output_dir, f'feature_importance_{data_source}_{timestamp}.csv')
        importance_df.to_csv(importance_file, index=False)
        logger.info(f"✅ Feature importance guardada en: {importance_file}")


def main():
    """Función principal"""
    
    print("""
╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                              ║
║           🤖 SISTEMA DE BACKTESTING CON MACHINE LEARNING 🤖                  ║
║                                                                              ║
║                      Estrategia ML Avanzada v1.0                             ║
║                      Con soporte para MetaTrader 5                           ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
    """)
    
    # Menú de opciones
    print("\n📋 OPCIONES DISPONIBLES:")
    print("  1. Backtest Simple (datos de muestra)")
    print("  2. Comparación de Configuraciones ML (datos de muestra)")
    print("  3. Análisis de Feature Importance")
    print("  4. Backtest Completo con Reportes (datos de muestra)")
    print("  5. 📡 Backtest con datos REALES de MetaTrader 5")
    print("  6. 📡 Comparación ML con datos REALES de MT5")
    print("  7. Salir")
    
    try:
        opcion = input("\n👉 Selecciona una opción (1-7): ").strip()
    except KeyboardInterrupt:
        print("\n\n👋 Saliendo...")
        return
    
    if opcion == '7':
        print("\n👋 ¡Hasta luego!")
        return
    
    # Configuración del backtest
    config = BacktestConfig(
        initial_capital=10000.0,
        commission_pct=0.0001,
        slippage_pct=0.0005,
        use_spread=True
    )
    
    # Variables para datos
    data = None
    symbol_info = None
    data_source = "muestra"
    
    # Determinar fuente de datos
    if opcion in ['5', '6']:
        # DATOS DE MT5
        print("\n" + "="*60)
        print("CONFIGURACIÓN DE DATOS MT5")
        print("="*60)
        
        symbol = input("Símbolo (default: XAUUSD): ").strip() or "XAUUSD"
        
        print("\nTimeframes disponibles:")
        print("  M1, M5, M15, M30, H1 (recomendado), H4, D1, W1")
        timeframe = input("Timeframe (default: H1): ").strip() or "H1"
        
        days_input = input("Días de historia (default: 365): ").strip()
        days = int(days_input) if days_input else 365
        
        # Cargar datos de MT5
        data, symbol_info = load_mt5_data(symbol, days, timeframe)
        
        if data is None:
            print("\n❌ No se pudieron cargar datos de MT5")
            print("   Volviendo a datos de muestra...")
            data = generate_sample_data(days=365)
            symbol_info = {
                'point': 0.01,
                'digits': 2,
                'trade_contract_size': 100.0
            }
            data_source = "muestra"
        else:
            data_source = f"MT5_{symbol}_{timeframe}"
    else:
        # DATOS DE MUESTRA
        print("\n📊 Generando datos de muestra...")
        data = generate_sample_data(days=365)
        
        # Información del símbolo (XAUUSD simulado)
        symbol_info = {
            'point': 0.01,
            'digits': 2,
            'trade_contract_size': 100.0
        }
        data_source = "muestra"
    
    # Ejecutar según opción seleccionada
    if opcion == '1' or opcion == '5':
        # Backtest simple
        result = run_ml_backtest(data, config, symbol_info, data_source=data_source)
        save_results(result, data_source=data_source)
        
    elif opcion == '2' or opcion == '6':
        # Comparación de configuraciones
        comparison_df = compare_strategies(data, config, symbol_info, data_source=data_source)
        
        # Guardar comparación
        output_dir = 'ml_backtest_results'
        os.makedirs(output_dir, exist_ok=True)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        comparison_file = os.path.join(output_dir, f'comparison_{data_source}_{timestamp}.csv')
        comparison_df.to_csv(comparison_file, index=False)
        logger.info(f"\n✅ Comparación guardada en: {comparison_file}")
        
    elif opcion == '3':
        # Análisis de feature importance
        print("\n🎯 Entrenando modelo para análisis...")
        strategy = MLAdvancedStrategy(
            min_train_samples=300,
            prediction_threshold=0.50,
            detect_regime=False
        )
        
        # Calcular indicadores y entrenar
        data_with_indicators = strategy.calculate_indicators(data)
        strategy.train_models(data_with_indicators)
        
        # Analizar importancia
        importance_df = analyze_feature_importance(strategy, data)
        
        # Guardar
        if not importance_df.empty:
            output_dir = 'ml_backtest_results'
            os.makedirs(output_dir, exist_ok=True)
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            importance_file = os.path.join(output_dir, f'feature_importance_{data_source}_{timestamp}.csv')
            importance_df.to_csv(importance_file, index=False)
            logger.info(f"\n✅ Feature importance guardada en: {importance_file}")
        
    elif opcion == '4':
        # Backtest completo
        print("\n🚀 Ejecutando backtest completo...")
        
        # 1. Backtest principal
        result = run_ml_backtest(data, config, symbol_info, data_source=data_source)
        
        # 2. Comparación
        print("\n📊 Comparando configuraciones...")
        comparison_df = compare_strategies(data, config, symbol_info, data_source=data_source)
        
        # 3. Feature importance
        print("\n🎯 Analizando feature importance...")
        strategy = MLAdvancedStrategy(
            min_train_samples=300,
            prediction_threshold=0.50,
            detect_regime=False
        )
        data_with_indicators = strategy.calculate_indicators(data)
        strategy.train_models(data_with_indicators)
        importance_df = analyze_feature_importance(strategy, data)
        
        # 4. Guardar todo
        save_results(result, comparison_df, importance_df, data_source=data_source)
        
        print("\n" + "="*80)
        print("✅ BACKTEST COMPLETO FINALIZADO")
        print("="*80)
        print("\n📁 Todos los resultados guardados en: ml_backtest_results/")
        print("📊 Revisa los archivos CSV para análisis detallado")
    
    else:
        print("\n❌ Opción no válida")
        return
    
    print("\n" + "="*80)
    print("✨ PROCESO COMPLETADO EXITOSAMENTE ✨")
    print("="*80)
    print("\n💡 Siguiente paso: Revisa los archivos generados en ml_backtest_results/")
    print("📊 Puedes usar estos resultados para optimizar parámetros")
    print("🔬 Experimenta con diferentes configuraciones de ML")


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Proceso interrumpido por el usuario. ¡Hasta luego!")
    except Exception as e:
        logger.error(f"Error inesperado: {e}", exc_info=True)
        print(f"\n❌ Error: {e}")
        print("\n💡 Sugerencias:")
        print("   - Verifica que todos los módulos estén instalados")
        print("   - Asegúrate de tener suficiente memoria disponible")
        print("   - Si usas MT5, verifica que esté abierto y funcionando")
        print("   - Revisa el archivo de log para más detalles")