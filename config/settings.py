"""
Configuración global del sistema de backtesting
"""
from dataclasses import dataclass
from typing import Dict, Optional
import pytz


@dataclass
class MT5Config:
    """Configuración para conexión a MetaTrader 5"""
    timeout: int = 60000  # milliseconds
    portable: bool = False
    login: Optional[int] = None
    password: Optional[str] = None
    server: Optional[str] = None
    path: Optional[str] = None  # Path to MT5 terminal


@dataclass
class BacktestConfig:
    """Configuración para el motor de backtesting"""
    initial_capital: float = 10000.0
    commission: float = 0.0  # Commission per trade (in currency)
    commission_pct: float = 0.0  # Commission as percentage
    slippage_pct: float = 0.01  # Slippage as percentage (0.01 = 1%)
    leverage: float = 100.0
    margin_call_level: float = 0.5  # 50%
    stop_out_level: float = 0.2  # 20%
    use_spread: bool = True  # Include spread in calculations
    timezone: str = 'UTC'
    
    def __post_init__(self):
        self.tz = pytz.timezone(self.timezone)


@dataclass
class StrategyConfig:
    """Configuración base para estrategias"""
    risk_per_trade: float = 0.02  # 2% del capital por operación
    max_positions: int = 1  # Máximo de posiciones simultáneas
    use_trailing_stop: bool = True
    trailing_stop_pct: float = 0.02  # 2% trailing stop
    min_risk_reward: float = 2.0  # Ratio mínimo R:R
    max_daily_trades: int = 5
    max_daily_loss_pct: float = 0.05  # 5% pérdida máxima diaria


@dataclass
class OptimizationConfig:
    """Configuración para optimización de parámetros"""
    method: str = 'walk_forward'  # 'grid', 'random', 'walk_forward', 'genetic'
    walk_forward_periods: int = 5
    in_sample_pct: float = 0.7  # 70% para entrenamiento
    out_sample_pct: float = 0.3  # 30% para validación
    n_iterations: int = 100  # Para optimización random/genetic
    cv_folds: int = 5  # Cross-validation folds
    monte_carlo_runs: int = 1000


# Timeframes disponibles en MT5
TIMEFRAMES = {
    'M1': 1,
    'M2': 2,
    'M3': 3,
    'M4': 4,
    'M5': 5,
    'M6': 6,
    'M10': 10,
    'M12': 12,
    'M15': 15,
    'M20': 20,
    'M30': 30,
    'H1': 60,
    'H2': 120,
    'H3': 180,
    'H4': 240,
    'H6': 360,
    'H8': 480,
    'H12': 720,
    'D1': 1440,
    'W1': 10080,
    'MN1': 43200,
}

# Configuración por defecto
DEFAULT_CONFIG = {
    'mt5': MT5Config(),
    'backtest': BacktestConfig(),
    'strategy': StrategyConfig(),
    'optimization': OptimizationConfig(),
}


def get_config(config_type: str = 'backtest') -> object:
    """
    Obtiene una configuración específica
    
    Args:
        config_type: Tipo de configuración ('mt5', 'backtest', 'strategy', 'optimization')
        
    Returns:
        Objeto de configuración correspondiente
    """
    return DEFAULT_CONFIG.get(config_type)


def update_config(config_type: str, **kwargs) -> None:
    """
    Actualiza una configuración con nuevos valores
    
    Args:
        config_type: Tipo de configuración a actualizar
        **kwargs: Parámetros a actualizar
    """
    config = DEFAULT_CONFIG.get(config_type)
    if config:
        for key, value in kwargs.items():
            if hasattr(config, key):
                setattr(config, key, value)
