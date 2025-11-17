"""Configuration module"""
from .settings import (
    MT5Config,
    BacktestConfig,
    StrategyConfig,
    OptimizationConfig,
    TIMEFRAMES,
    DEFAULT_CONFIG,
    get_config,
    update_config
)

__all__ = [
    'MT5Config',
    'BacktestConfig',
    'StrategyConfig',
    'OptimizationConfig',
    'TIMEFRAMES',
    'DEFAULT_CONFIG',
    'get_config',
    'update_config'
]
