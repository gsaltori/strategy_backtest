"""
MT5 Strategy Backtesting System

Sistema completo de backtesting para estrategias de trading con MetaTrader 5.

Componentes principales:
- data_manager: Gestión de conexión y datos MT5
- backtest_engine: Motor de backtesting con simulación realista
- strategies: Sistema de estrategias base y ejemplos
- analysis: Análisis de rendimiento y reportes
- config: Configuraciones del sistema

Ejemplo de uso:
    >>> from data_manager import MT5DataManager
    >>> from backtest_engine import BacktestEngine
    >>> from strategies.moving_average_crossover import MovingAverageCrossover
    >>> 
    >>> # Generar datos de muestra
    >>> import pandas as pd
    >>> import numpy as np
    >>> from datetime import datetime, timedelta
    >>> 
    >>> dates = pd.date_range(end=datetime.now(), periods=8760, freq='H')
    >>> prices = 1.1 * np.exp(np.cumsum(np.random.normal(0.0001, 0.01, len(dates))))
    >>> data = pd.DataFrame({
    ...     'open': prices, 'high': prices*1.005, 'low': prices*0.995,
    ...     'close': prices, 'tick_volume': 100, 'spread': 2, 'real_volume': 1000
    ... }, index=dates)
    >>> 
    >>> # Crear y ejecutar backtest
    >>> strategy = MovingAverageCrossover(fast_period=10, slow_period=30)
    >>> engine = BacktestEngine()
    >>> result = engine.run(strategy, data)
    >>> print(result.summary())

Versión: 1.0.0
Autor: Backtesting System
Licencia: MIT
"""

__version__ = '1.0.0'
__author__ = 'Backtesting System'
__license__ = 'MIT'

# Importaciones principales para acceso rápido
from .data_manager import MT5DataManager
from .backtest_engine import BacktestEngine, BacktestResult, Trade
from .strategies.base_strategy import TradingStrategy, Signal, Position
from .strategies.moving_average_crossover import MovingAverageCrossover
from .analysis.performance import PerformanceAnalyzer
from .analysis.reporting import ReportGenerator

__all__ = [
    # Data Management
    'MT5DataManager',
    
    # Backtesting
    'BacktestEngine',
    'BacktestResult',
    'Trade',
    
    # Strategies
    'TradingStrategy',
    'Signal',
    'Position',
    'MovingAverageCrossover',
    
    # Analysis
    'PerformanceAnalyzer',
    'ReportGenerator',
]
