"""
Ejemplo de uso del sistema de backtesting
Este script demuestra cómo usar todos los componentes del sistema
"""
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

# Importar módulos del sistema
from data_manager import MT5DataManager
from backtest_engine import BacktestEngine
from strategies.moving_average_crossover import MovingAverageCrossover
from analysis.reporting import ReportGenerator
from config.settings import MT5Config, BacktestConfig, StrategyConfig


def generate_sample_data(days=365, initial_price=1.1000):
    """
    Genera datos de muestra para testing sin MT5
    
    Args:
        days: Número de días de datos
        initial_price: Precio inicial
        
    Returns:
        DataFrame con datos OHLC
    """
    logger.info(f"Generating {days} days of sample data...")
    
    # Generar fechas
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    dates = pd.date_range(start=start_date, end=end_date, freq='H')
    
    # Simular precios con movimiento browniano y tendencia
    n = len(dates)
    returns = np.random.normal(0.0001, 0.01, n)  # Drift pequeño y volatilidad
    
    # Añadir componente de tendencia y ciclos
    trend = np.linspace(0, 0.1, n)
    cycle = 0.05 * np.sin(np.linspace(0, 8*np.pi, n))
    returns = returns + trend/n + cycle/n
    
    # Calcular precios
    prices = initial_price * np.exp(np.cumsum(returns))
    
    # Crear OHLC
    data = pd.DataFrame({
        'open': prices,
        'high': prices * (1 + np.abs(np.random.normal(0, 0.005, n))),
        'low': prices * (1 - np.abs(np.random.normal(0, 0.005, n))),
        'close': prices * (1 + np.random.normal(0, 0.003, n)),
        'tick_volume': np.random.randint(100, 1000, n),
        'spread': np.random.randint(1, 5, n),
        'real_volume': np.random.randint(1000, 10000, n)
    }, index=dates)
    
    # Asegurar que high sea el máximo y low el mínimo
    data['high'] = data[['open', 'high', 'close']].max(axis=1)
    data['low'] = data[['open', 'low', 'close']].min(axis=1)
    
    logger.info(f"Sample data generated: {len(data)} bars from {data.index[0]} to {data.index[-1]}")
    
    return data


def example_with_mt5():
    """
    Ejemplo completo usando MetaTrader 5
    """
    logger.info("="*80)
    logger.info("EXAMPLE 1: Backtesting with MetaTrader 5 Data")
    logger.info("="*80)
    
    # Configuración MT5
    mt5_config = MT5Config()
    
    # Crear gestor de datos
    data_manager = MT5DataManager(mt5_config)
    
    # Conectar a MT5
    if not data_manager.connect():
        logger.error("Failed to connect to MT5. Make sure MT5 is installed and running.")
        return
    
    try:
        # Configurar símbolo y período
        symbol = "EURUSD"
        timeframe = "H1"
        start_date = datetime.now() - timedelta(days=365)
        
        # Validar símbolo
        if not data_manager.validate_symbol(symbol):
            logger.error(f"Symbol {symbol} not available")
            return
        
        # Obtener información del símbolo
        symbol_info = data_manager.get_symbol_info(symbol)
        logger.info(f"Symbol info: {symbol_info}")
        
        # Descargar datos históricos
        data = data_manager.get_historical_data(
            symbol=symbol,
            timeframe=timeframe,
            start_date=start_date,
            count=5000
        )
        
        if data is None or len(data) == 0:
            logger.error("No data retrieved")
            return
        
        logger.info(f"Downloaded {len(data)} bars of {symbol} data")
        
        # Crear estrategia
        strategy = MovingAverageCrossover(
            fast_period=10,
            slow_period=30,
            ma_type='EMA',
            rsi_period=14,
            rsi_overbought=70,
            rsi_oversold=30,
            risk_per_trade=0.02,
            use_trailing_stop=True
        )
        
        # Configurar backtest
        backtest_config = BacktestConfig(
            initial_capital=10000.0,
            commission_pct=0.0001,  # 0.01%
            slippage_pct=0.0005,    # 0.05%
            use_spread=True
        )
        
        # Crear motor de backtest
        engine = BacktestEngine(backtest_config)
        
        # Ejecutar backtest
        logger.info("Running backtest...")
        result = engine.run(strategy, data, symbol_info)
        
        # Mostrar resumen
        print(result.summary())
        
        # Generar reporte
        logger.info("Generating report...")
        report_gen = ReportGenerator(result)
        
        # Guardar reporte HTML
        report_gen.save_report_html('backtest_report_mt5.html')
        
        # Crear gráfico interactivo
        fig = report_gen.create_full_report()
        fig.show()
        
        logger.info("Backtest completed successfully!")
        
    finally:
        # Desconectar
        data_manager.disconnect()


def example_with_sample_data():
    """
    Ejemplo usando datos de muestra (sin necesidad de MT5)
    """
    logger.info("="*80)
    logger.info("EXAMPLE 2: Backtesting with Sample Data (No MT5 Required)")
    logger.info("="*80)
    
    # Generar datos de muestra
    data = generate_sample_data(days=365, initial_price=1.1000)
    
    # Información del símbolo simulado
    symbol_info = {
        'name': 'EURUSD',
        'point': 0.00001,
        'digits': 5,
        'spread': 2,
        'trade_contract_size': 100000,
    }
    
    # Crear estrategia con diferentes parámetros
    strategy = MovingAverageCrossover(
        fast_period=12,
        slow_period=26,
        ma_type='EMA',
        rsi_period=14,
        rsi_overbought=65,
        rsi_oversold=35,
        atr_stop_multiplier=2.5,
        risk_reward_ratio=2.0,
        risk_per_trade=0.015,
        use_trailing_stop=True,
        trailing_stop_pct=0.02
    )
    
    # Configurar backtest
    backtest_config = BacktestConfig(
        initial_capital=10000.0,
        commission_pct=0.0001,
        slippage_pct=0.0005,
        use_spread=True,
        leverage=100.0
    )
    
    # Crear motor de backtest
    engine = BacktestEngine(backtest_config)
    
    # Ejecutar backtest
    logger.info("Running backtest...")
    result = engine.run(strategy, data, symbol_info)
    
    # Mostrar resumen
    print(result.summary())
    
    # Generar reporte
    logger.info("Generating comprehensive report...")
    report_gen = ReportGenerator(result)
    
    # Tabla de métricas
    metrics_df = report_gen.create_metrics_table()
    print("\n" + "="*80)
    print("DETAILED METRICS")
    print("="*80)
    print(metrics_df.to_string(index=False))
    
    # Tabla de trades
    trades_df = report_gen.create_trades_dataframe()
    print("\n" + "="*80)
    print("TRADE HISTORY (First 10 trades)")
    print("="*80)
    print(trades_df.head(10).to_string(index=False))
    
    # Guardar reporte HTML
    report_gen.save_report_html('backtest_report_sample.html')
    logger.info("HTML report saved: backtest_report_sample.html")
    
    # Crear y mostrar gráfico interactivo
    logger.info("Creating interactive charts...")
    fig = report_gen.create_full_report('backtest_charts.html')
    logger.info("Interactive charts saved: backtest_charts.html")
    
    # Análisis temporal
    from analysis.performance import PerformanceAnalyzer
    analyzer = PerformanceAnalyzer(result.trades, result.equity_curve, result.initial_capital)
    time_analysis = analyzer.analyze_trades_by_time()
    
    if time_analysis:
        print("\n" + "="*80)
        print("TEMPORAL ANALYSIS")
        print("="*80)
        print("\nPerformance by Day of Week:")
        if 'by_day_of_week' in time_analysis:
            for day, stats in time_analysis['by_day_of_week']['mean'].items():
                print(f"  Day {day}: ${stats:.2f}")
    
    logger.info("Backtest completed successfully!")
    
    return result


def example_parameter_optimization():
    """
    Ejemplo de optimización de parámetros (simple grid search)
    """
    logger.info("="*80)
    logger.info("EXAMPLE 3: Parameter Optimization")
    logger.info("="*80)
    
    # Generar datos
    data = generate_sample_data(days=365, initial_price=1.1000)
    
    symbol_info = {
        'name': 'EURUSD',
        'point': 0.00001,
        'digits': 5,
        'spread': 2,
        'trade_contract_size': 100000,
    }
    
    # Configurar backtest
    backtest_config = BacktestConfig(
        initial_capital=10000.0,
        commission_pct=0.0001,
        slippage_pct=0.0005,
    )
    
    # Rangos de parámetros a probar
    fast_periods = [8, 10, 12]
    slow_periods = [24, 30, 36]
    
    best_sharpe = -999
    best_params = {}
    results_list = []
    
    logger.info(f"Testing {len(fast_periods) * len(slow_periods)} parameter combinations...")
    
    for fast in fast_periods:
        for slow in slow_periods:
            if fast >= slow:
                continue
            
            # Crear estrategia
            strategy = MovingAverageCrossover(
                fast_period=fast,
                slow_period=slow,
                ma_type='EMA',
                risk_per_trade=0.02
            )
            
            # Ejecutar backtest
            engine = BacktestEngine(backtest_config)
            result = engine.run(strategy, data, symbol_info)
            
            # Guardar resultados
            sharpe = result.metrics.get('sharpe_ratio', 0)
            total_return = (result.final_capital / result.initial_capital - 1) * 100
            
            results_list.append({
                'Fast Period': fast,
                'Slow Period': slow,
                'Total Return %': total_return,
                'Sharpe Ratio': sharpe,
                'Total Trades': result.metrics.get('total_trades', 0),
                'Win Rate %': result.metrics.get('win_rate', 0) * 100,
                'Max Drawdown %': result.metrics.get('max_drawdown', 0) * 100,
            })
            
            # Actualizar mejor resultado
            if sharpe > best_sharpe:
                best_sharpe = sharpe
                best_params = {'fast_period': fast, 'slow_period': slow}
            
            logger.info(f"Fast={fast}, Slow={slow}: Return={total_return:.2f}%, Sharpe={sharpe:.2f}")
    
    # Mostrar resultados
    results_df = pd.DataFrame(results_list)
    results_df = results_df.sort_values('Sharpe Ratio', ascending=False)
    
    print("\n" + "="*80)
    print("OPTIMIZATION RESULTS")
    print("="*80)
    print(results_df.to_string(index=False))
    
    print("\n" + "="*80)
    print("BEST PARAMETERS")
    print("="*80)
    print(f"Fast Period: {best_params['fast_period']}")
    print(f"Slow Period: {best_params['slow_period']}")
    print(f"Best Sharpe Ratio: {best_sharpe:.2f}")
    
    # Guardar resultados
    results_df.to_csv('optimization_results.csv', index=False, encoding='utf-8')
    logger.info("Optimization results saved to optimization_results.csv")
    
    return results_df


def main():
    """
    Función principal que ejecuta los ejemplos
    """
    print("""
    ╔════════════════════════════════════════════════════════════════╗
    ║           MT5 STRATEGY BACKTESTING SYSTEM                      ║
    ║                     Example Usage                              ║
    ╚════════════════════════════════════════════════════════════════╝
    """)
    
    print("\nSelect an example to run:")
    print("1. Backtest with MetaTrader 5 data (requires MT5 installed)")
    print("2. Backtest with sample data (no MT5 required) - RECOMMENDED")
    print("3. Parameter optimization example")
    print("4. Run all examples")
    
    choice = input("\nEnter your choice (1-4): ").strip()
    
    try:
        if choice == '1':
            example_with_mt5()
        elif choice == '2':
            example_with_sample_data()
        elif choice == '3':
            example_parameter_optimization()
        elif choice == '4':
            print("\n" + "="*80)
            print("Running Example 2: Sample Data Backtest")
            print("="*80)
            example_with_sample_data()
            
            print("\n" + "="*80)
            print("Running Example 3: Parameter Optimization")
            print("="*80)
            example_parameter_optimization()
        else:
            print("Invalid choice. Running default example (Sample Data)...")
            example_with_sample_data()
    
    except Exception as e:
        logger.error(f"Error during execution: {e}", exc_info=True)
        print(f"\n❌ Error: {e}")
        print("Please check the logs for more details.")
    
    print("\n" + "="*80)
    print("Example execution completed!")
    print("="*80)


if __name__ == "__main__":
    main()
