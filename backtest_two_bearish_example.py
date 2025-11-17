"""
Script de ejemplo para ejecutar backtest de la estrategia Two Bearish Pattern

Este script demuestra cómo:
1. Cargar datos históricos
2. Configurar la estrategia
3. Ejecutar el backtest
4. Visualizar resultados
"""

import sys
import os
import pandas as pd
import MetaTrader5 as mt5
from datetime import datetime, timedelta
import logging

# Añadir el directorio actual al path
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

# Importar módulos del proyecto
try:
    # Intentar importar desde strategies/
    from strategies.two_bearish_pattern_strategy import TwoBearishPatternStrategy
except ImportError:
    # Si no funciona, intentar import directo
    try:
        from two_bearish_pattern_strategy import TwoBearishPatternStrategy
    except ImportError:
        print("Error: No se puede importar TwoBearishPatternStrategy")
        print("Asegúrate de que el archivo está en el directorio correcto")
        sys.exit(1)

# Importar BacktestEngine
try:
    from backtest_engine import BacktestEngine
except ImportError:
    print("Error: No se puede importar BacktestEngine")
    print("Asegúrate de tener backtest_engine.py en el directorio del proyecto")
    sys.exit(1)

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def get_historical_data(symbol: str, timeframe, num_bars: int = 1000):
    """
    Obtiene datos históricos de MT5
    
    Args:
        symbol: Símbolo a obtener
        timeframe: Timeframe (mt5.TIMEFRAME_H4)
        num_bars: Número de barras
        
    Returns:
        DataFrame con datos OHLC
    """
    # Inicializar MT5
    if not mt5.initialize():
        logger.error("Error al inicializar MT5")
        return None
    
    try:
        # Obtener datos
        rates = mt5.copy_rates_from_pos(symbol, timeframe, 0, num_bars)
        
        if rates is None or len(rates) == 0:
            logger.error(f"No se pudieron obtener datos de {symbol}")
            return None
        
        # Convertir a DataFrame
        df = pd.DataFrame(rates)
        df['time'] = pd.to_datetime(df['time'], unit='s')
        df.set_index('time', inplace=True)
        
        # Renombrar columnas para compatibilidad
        df.columns = ['open', 'high', 'low', 'close', 'tick_volume', 
                      'spread', 'real_volume']
        
        logger.info(f"Datos obtenidos: {len(df)} barras de {symbol}")
        logger.info(f"Periodo: {df.index[0]} a {df.index[-1]}")
        
        return df
        
    finally:
        mt5.shutdown()


def run_backtest_example():
    """
    Ejecuta un backtest de ejemplo con la estrategia Two Bearish Pattern
    """
    print("="*70)
    print("BACKTEST - ESTRATEGIA TWO BEARISH PATTERN")
    print("="*70)
    
    # Configuración
    symbol = "EURUSD"
    timeframe = mt5.TIMEFRAME_H4
    initial_balance = 10000.0
    num_bars = 1000
    
    print(f"\nConfiguración:")
    print(f"  Símbolo: {symbol}")
    print(f"  Timeframe: H4")
    print(f"  Balance inicial: ${initial_balance:,.2f}")
    print(f"  Barras a analizar: {num_bars}")
    
    # Obtener datos
    print("\n" + "="*70)
    print("1. Obteniendo datos históricos...")
    print("="*70)
    
    data = get_historical_data(symbol, timeframe, num_bars)
    
    if data is None:
        print("Error: No se pudieron obtener datos históricos")
        return
    
    # Crear estrategia
    print("\n" + "="*70)
    print("2. Configurando estrategia...")
    print("="*70)
    
    strategy = TwoBearishPatternStrategy(
        risk_reward_ratio=2.0,        # Take Profit 1:2
        risk_per_trade=0.02,          # Riesgo 2% por operación
        min_body_ratio=1.0,           # Cuerpo alcista >= cuerpo bajista
        use_trailing_stop=False,      # Sin trailing stop
    )
    
    print(f"\nEstrategia creada: {strategy}")
    print(f"  Risk/Reward: 1:{strategy.parameters['risk_reward_ratio']}")
    print(f"  Riesgo por trade: {strategy.risk_per_trade*100}%")
    print(f"  Ratio mínimo de cuerpo: {strategy.parameters['min_body_ratio']}")
    
    # Configurar backtest engine
    print("\n" + "="*70)
    print("3. Configurando motor de backtest...")
    print("="*70)
    
    # Importar configuración
    try:
        from config.settings import BacktestConfig
        config = BacktestConfig(
            initial_capital=initial_balance,
            commission_pct=0.0,        # Sin comisiones para simplificar
            slippage_pct=0.01,         # 1% de slippage
            use_spread=False
        )
    except ImportError:
        # Si no existe BacktestConfig, crear una configuración básica
        from dataclasses import dataclass
        
        @dataclass
        class BacktestConfig:
            initial_capital: float = 10000.0
            commission_pct: float = 0.0
            slippage_pct: float = 0.01
            use_spread: bool = False
        
        config = BacktestConfig(
            initial_capital=initial_balance,
            commission_pct=0.0,
            slippage_pct=0.01,
            use_spread=False
        )
    
    backtest = BacktestEngine(config=config)
    
    print(f"\nBacktest Engine configurado")
    print(f"  Balance inicial: ${initial_balance:,.2f}")
    print(f"  Comisión: 0%")
    print(f"  Slippage: 1 pip")
    
    # Ejecutar backtest
    print("\n" + "="*70)
    print("4. Ejecutando backtest...")
    print("="*70)
    
    results = backtest.run(strategy=strategy, data=data)
    
    # Mostrar resultados
    print("\n" + "="*70)
    print("5. RESULTADOS DEL BACKTEST")
    print("="*70)
    
    metrics = results.metrics
    trades = results.trades
    equity_curve = results.equity_curve
    
    print(f"\n📊 MÉTRICAS GENERALES")
    print(f"{'─'*70}")
    print(f"  Total de operaciones: {metrics['total_trades']}")
    print(f"  Operaciones ganadoras: {metrics['winning_trades']} "
          f"({metrics['win_rate']*100:.1f}%)")
    print(f"  Operaciones perdedoras: {metrics['losing_trades']} "
          f"({(1-metrics['win_rate'])*100:.1f}%)")
    
    print(f"\n💰 RESULTADOS FINANCIEROS")
    print(f"{'─'*70}")
    print(f"  Balance inicial: ${results.initial_capital:,.2f}")
    print(f"  Balance final: ${results.final_capital:,.2f}")
    print(f"  Ganancia neta: ${metrics['total_pnl']:,.2f}")
    
    # Calcular retorno
    total_return = (results.final_capital / results.initial_capital) - 1
    print(f"  Retorno: {total_return*100:.2f}%")
    
    print(f"\n📈 RENDIMIENTO")
    print(f"{'─'*70}")
    print(f"  Profit Factor: {metrics['profit_factor']:.2f}")
    print(f"  Sharpe Ratio: {metrics.get('sharpe_ratio', 0):.2f}")
    print(f"  Max Drawdown: {metrics['max_drawdown']*100:.2f}%")
    print(f"  Promedio ganancia: ${metrics['avg_win']:,.2f}")
    print(f"  Promedio pérdida: ${metrics['avg_loss']:,.2f}")
    
    # Mostrar últimas operaciones
    if len(trades) > 0:
        print(f"\n📋 ÚLTIMAS 5 OPERACIONES")
        print(f"{'─'*70}")
        
        # Tomar las últimas 5 operaciones
        last_trades = trades[-5:] if len(trades) >= 5 else trades
        
        for idx, trade in enumerate(last_trades, 1):
            pnl_symbol = "✅" if trade.pnl > 0 else "❌"
            
            print(f"\n  {pnl_symbol} Trade #{idx}")
            print(f"     Entry: {trade.entry_time.strftime('%Y-%m-%d %H:%M')} "
                  f"@ {trade.entry_price:.5f}")
            print(f"     Exit:  {trade.exit_time.strftime('%Y-%m-%d %H:%M')} "
                  f"@ {trade.exit_price:.5f}")
            print(f"     P&L: ${trade.pnl:,.2f} ({trade.pnl_pct*100:.2f}%)")
            print(f"     Razón: {trade.exit_reason}")
    
    # Generar reporte detallado (opcional)
    try:
        print(f"\n" + "="*70)
        print("6. Generando reporte detallado...")
        print("="*70)
        
        from reporting import ReportGenerator
        report = ReportGenerator(results)
        fig = report.create_full_report()
        
        # Guardar reporte
        report_path = 'backtest_two_bearish_pattern.html'
        fig.write_html(report_path)
        
        print(f"\n✅ Reporte HTML generado: {report_path}")
    except Exception as e:
        print(f"\n⚠️  No se pudo generar reporte HTML: {e}")
        print("   Continuando sin reporte...")
    
    # Resumen final
    print(f"\n" + "="*70)
    print("RESUMEN EJECUTIVO")
    print("="*70)
    
    if metrics['total_trades'] > 0:
        total_return = (results.final_capital / results.initial_capital) - 1
        
        if metrics['total_pnl'] > 0:
            print(f"\n✅ Estrategia RENTABLE")
            print(f"   Ganancia: ${metrics['total_pnl']:,.2f} "
                  f"({total_return*100:.2f}%)")
        else:
            print(f"\n❌ Estrategia NO RENTABLE")
            print(f"   Pérdida: ${metrics['total_pnl']:,.2f} "
                  f"({total_return*100:.2f}%)")
        
        print(f"\n   Win Rate: {metrics['win_rate']*100:.1f}%")
        print(f"   Profit Factor: {metrics['profit_factor']:.2f}")
        print(f"   Max Drawdown: {metrics['max_drawdown']*100:.2f}%")
    else:
        print(f"\n⚠️  No se generaron operaciones en el periodo analizado")
    
    print(f"\n" + "="*70)


def run_parameter_optimization():
    """
    Ejecuta una optimización de parámetros
    """
    print("\n" + "="*70)
    print("OPTIMIZACIÓN DE PARÁMETROS")
    print("="*70)
    
    # Obtener datos
    symbol = "EURUSD"
    timeframe = mt5.TIMEFRAME_H4
    data = get_historical_data(symbol, timeframe, 1000)
    
    if data is None:
        return
    
    # Definir rangos de parámetros a probar
    param_grid = {
        'risk_reward_ratio': [1.5, 2.0, 2.5, 3.0],
        'min_body_ratio': [0.8, 1.0, 1.2, 1.5],
        'risk_per_trade': [0.01, 0.02, 0.03]
    }
    
    print(f"\nProbando combinaciones de parámetros:")
    for param, values in param_grid.items():
        print(f"  {param}: {values}")
    
    best_return = -float('inf')
    best_params = None
    best_metrics = None
    
    total_combinations = (len(param_grid['risk_reward_ratio']) * 
                         len(param_grid['min_body_ratio']) * 
                         len(param_grid['risk_per_trade']))
    
    print(f"\nTotal de combinaciones: {total_combinations}")
    print(f"\nEjecutando backtests...\n")
    
    count = 0
    for rr in param_grid['risk_reward_ratio']:
        for body_ratio in param_grid['min_body_ratio']:
            for risk in param_grid['risk_per_trade']:
                count += 1
                
                # Crear estrategia con parámetros
                strategy = TwoBearishPatternStrategy(
                    risk_reward_ratio=rr,
                    min_body_ratio=body_ratio,
                    risk_per_trade=risk
                )
                
                # Ejecutar backtest
                try:
                    from config.settings import BacktestConfig
                    config = BacktestConfig(
                        initial_capital=10000.0,
                        commission_pct=0.0,
                        slippage_pct=0.01
                    )
                except ImportError:
                    from dataclasses import dataclass
                    @dataclass
                    class BacktestConfig:
                        initial_capital: float = 10000.0
                        commission_pct: float = 0.0
                        slippage_pct: float = 0.01
                    config = BacktestConfig(
                        initial_capital=10000.0,
                        commission_pct=0.0,
                        slippage_pct=0.01
                    )
                
                backtest = BacktestEngine(config=config)
                results = backtest.run(strategy=strategy, data=data)
                metrics = results.metrics
                
                # Calcular retorno total
                total_return = (results.final_capital / results.initial_capital) - 1
                
                # Actualizar mejor resultado
                if total_return > best_return:
                    best_return = total_return
                    best_params = {
                        'risk_reward_ratio': rr,
                        'min_body_ratio': body_ratio,
                        'risk_per_trade': risk
                    }
                    best_metrics = metrics
                
                # Mostrar progreso
                print(f"[{count}/{total_combinations}] "
                      f"RR:{rr} BR:{body_ratio} Risk:{risk*100}% -> "
                      f"Return: {total_return*100:.2f}% "
                      f"Trades: {metrics.get('total_trades', 0)}")
    
    # Mostrar mejores parámetros
    print(f"\n" + "="*70)
    print("MEJORES PARÁMETROS ENCONTRADOS")
    print("="*70)
    print(f"\nParámetros:")
    for param, value in best_params.items():
        print(f"  {param}: {value}")
    
    print(f"\nResultados:")
    print(f"  Retorno: {best_return*100:.2f}%")
    print(f"  Win Rate: {best_metrics.get('win_rate', 0)*100:.1f}%")
    print(f"  Profit Factor: {best_metrics.get('profit_factor', 0):.2f}")
    print(f"  Total Trades: {best_metrics.get('total_trades', 0)}")
    print(f"  Max Drawdown: {best_metrics.get('max_drawdown', 0)*100:.2f}%")


if __name__ == "__main__":
    """
    Punto de entrada principal
    """
    print("\n" + "="*70)
    print("BACKTEST - TWO BEARISH PATTERN STRATEGY")
    print("Patrón: 2 velas bajistas precedidas de vela alcista")
    print("Timeframe: H4")
    print("="*70)
    
    # Menú de opciones
    print("\nOpciones:")
    print("  1. Ejecutar backtest simple")
    print("  2. Ejecutar optimización de parámetros")
    print("  0. Salir")
    
    try:
        option = input("\nSeleccione una opción: ").strip()
        
        if option == "1":
            run_backtest_example()
        elif option == "2":
            run_parameter_optimization()
        elif option == "0":
            print("Saliendo...")
        else:
            print("Opción no válida")
            
    except KeyboardInterrupt:
        print("\n\nInterrumpido por el usuario")
    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)