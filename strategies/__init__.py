"""Strategies module"""
from .base_strategy import TradingStrategy, Signal, Position
from .moving_average_crossover import MovingAverageCrossover

__all__ = [
    'TradingStrategy',
    'Signal',
    'Position',
    'MovingAverageCrossover',
]
