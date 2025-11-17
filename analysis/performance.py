"""
Módulo de análisis de rendimiento
Cálculo avanzado de métricas y estadísticas
"""
import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
from scipy import stats
import logging

logger = logging.getLogger(__name__)


class PerformanceAnalyzer:
    """
    Analizador avanzado de rendimiento de estrategias
    """
    
    def __init__(self, trades: List, equity_curve: pd.Series, initial_capital: float):
        """
        Inicializa el analizador
        
        Args:
            trades: Lista de trades ejecutados
            equity_curve: Serie de equity
            initial_capital: Capital inicial
        """
        self.trades = trades
        self.equity_curve = equity_curve
        self.initial_capital = initial_capital
        
        # Calcular retornos
        self.returns = self.equity_curve.pct_change().dropna()
    
    def calculate_advanced_metrics(self) -> Dict:
        """
        Calcula métricas avanzadas de rendimiento
        
        Returns:
            Diccionario con métricas avanzadas
        """
        metrics = {}
        
        # Sortino Ratio
        metrics['sortino_ratio'] = self._calculate_sortino_ratio()
        
        # Omega Ratio
        metrics['omega_ratio'] = self._calculate_omega_ratio()
        
        # Tail Ratio
        metrics['tail_ratio'] = self._calculate_tail_ratio()
        
        # Common Sense Ratio
        metrics['common_sense_ratio'] = self._calculate_common_sense_ratio()
        
        # Ulcer Index
        metrics['ulcer_index'] = self._calculate_ulcer_index()
        
        # Serenity Index
        metrics['serenity_index'] = self._calculate_serenity_index()
        
        # Kelly Criterion
        metrics['kelly_criterion'] = self._calculate_kelly_criterion()
        
        # Probabilidad de profit
        metrics['profit_probability'] = self._calculate_profit_probability()
        
        # Consecutive wins/losses
        metrics['max_consecutive_wins'] = self._calculate_max_consecutive_wins()
        metrics['max_consecutive_losses'] = self._calculate_max_consecutive_losses()
        
        # Win/Loss streaks statistics
        metrics['avg_win_streak'] = self._calculate_avg_win_streak()
        metrics['avg_loss_streak'] = self._calculate_avg_loss_streak()
        
        # Trade duration analysis
        metrics['avg_winning_duration'] = self._calculate_avg_winning_duration()
        metrics['avg_losing_duration'] = self._calculate_avg_losing_duration()
        
        # Risk-adjusted metrics
        metrics['risk_adjusted_return'] = self._calculate_risk_adjusted_return()
        
        # Volatility analysis
        metrics['volatility_annual'] = self.returns.std() * np.sqrt(252)
        metrics['downside_volatility'] = self._calculate_downside_volatility()
        
        return metrics
    
    def _calculate_sortino_ratio(self, target_return: float = 0.0) -> float:
        """
        Calcula el Sortino Ratio
        
        Args:
            target_return: Retorno objetivo
            
        Returns:
            Sortino Ratio
        """
        if len(self.returns) == 0:
            return 0.0
        
        excess_returns = self.returns - target_return
        downside_returns = excess_returns[excess_returns < 0]
        
        if len(downside_returns) == 0:
            return float('inf')
        
        downside_std = downside_returns.std()
        
        if downside_std == 0:
            return 0.0
        
        sortino = (excess_returns.mean() / downside_std) * np.sqrt(252)
        
        return sortino
    
    def _calculate_omega_ratio(self, threshold: float = 0.0) -> float:
        """
        Calcula el Omega Ratio
        
        Args:
            threshold: Umbral de retorno
            
        Returns:
            Omega Ratio
        """
        if len(self.returns) == 0:
            return 0.0
        
        excess_returns = self.returns - threshold
        
        gains = excess_returns[excess_returns > 0].sum()
        losses = abs(excess_returns[excess_returns < 0].sum())
        
        if losses == 0:
            return float('inf') if gains > 0 else 0.0
        
        omega = gains / losses
        
        return omega
    
    def _calculate_tail_ratio(self) -> float:
        """
        Calcula el Tail Ratio (95th percentile / 5th percentile)
        
        Returns:
            Tail Ratio
        """
        if len(self.returns) == 0:
            return 0.0
        
        p95 = np.percentile(self.returns, 95)
        p5 = np.percentile(self.returns, 5)
        
        if p5 == 0:
            return 0.0
        
        tail_ratio = abs(p95 / p5)
        
        return tail_ratio
    
    def _calculate_common_sense_ratio(self) -> float:
        """
        Calcula el Common Sense Ratio (Tail Ratio - 1)
        
        Returns:
            Common Sense Ratio
        """
        tail_ratio = self._calculate_tail_ratio()
        return tail_ratio - 1
    
    def _calculate_ulcer_index(self) -> float:
        """
        Calcula el Ulcer Index (medida de drawdown)
        
        Returns:
            Ulcer Index
        """
        if len(self.equity_curve) == 0:
            return 0.0
        
        cummax = self.equity_curve.cummax()
        drawdown = ((self.equity_curve - cummax) / cummax) * 100
        
        ulcer = np.sqrt((drawdown ** 2).mean())
        
        return ulcer
    
    def _calculate_serenity_index(self) -> float:
        """
        Calcula el Serenity Index (Return / Ulcer Index)
        
        Returns:
            Serenity Index
        """
        if len(self.equity_curve) < 2:
            return 0.0
        
        total_return = (self.equity_curve.iloc[-1] / self.equity_curve.iloc[0] - 1) * 100
        ulcer = self._calculate_ulcer_index()
        
        if ulcer == 0:
            return 0.0
        
        serenity = total_return / ulcer
        
        return serenity
    
    def _calculate_kelly_criterion(self) -> float:
        """
        Calcula el Kelly Criterion para tamaño óptimo de posición
        
        Returns:
            Kelly Criterion percentage
        """
        if not self.trades:
            return 0.0
        
        wins = [t.pnl for t in self.trades if t.pnl > 0]
        losses = [abs(t.pnl) for t in self.trades if t.pnl < 0]
        
        if not wins or not losses:
            return 0.0
        
        win_rate = len(wins) / len(self.trades)
        avg_win = np.mean(wins)
        avg_loss = np.mean(losses)
        
        if avg_loss == 0:
            return 0.0
        
        win_loss_ratio = avg_win / avg_loss
        
        kelly = (win_rate * win_loss_ratio - (1 - win_rate)) / win_loss_ratio
        
        # Limitar a valores razonables
        kelly = max(0.0, min(kelly, 1.0))
        
        return kelly
    
    def _calculate_profit_probability(self) -> float:
        """
        Calcula la probabilidad de obtener profit en el próximo trade
        
        Returns:
            Probabilidad de profit
        """
        if not self.trades:
            return 0.0
        
        winning_trades = sum(1 for t in self.trades if t.pnl > 0)
        
        return winning_trades / len(self.trades)
    
    def _calculate_max_consecutive_wins(self) -> int:
        """
        Calcula el máximo de victorias consecutivas
        
        Returns:
            Número máximo de victorias consecutivas
        """
        if not self.trades:
            return 0
        
        max_streak = 0
        current_streak = 0
        
        for trade in self.trades:
            if trade.pnl > 0:
                current_streak += 1
                max_streak = max(max_streak, current_streak)
            else:
                current_streak = 0
        
        return max_streak
    
    def _calculate_max_consecutive_losses(self) -> int:
        """
        Calcula el máximo de pérdidas consecutivas
        
        Returns:
            Número máximo de pérdidas consecutivas
        """
        if not self.trades:
            return 0
        
        max_streak = 0
        current_streak = 0
        
        for trade in self.trades:
            if trade.pnl <= 0:
                current_streak += 1
                max_streak = max(max_streak, current_streak)
            else:
                current_streak = 0
        
        return max_streak
    
    def _calculate_avg_win_streak(self) -> float:
        """
        Calcula el promedio de rachas ganadoras
        
        Returns:
            Promedio de rachas ganadoras
        """
        if not self.trades:
            return 0.0
        
        streaks = []
        current_streak = 0
        
        for trade in self.trades:
            if trade.pnl > 0:
                current_streak += 1
            else:
                if current_streak > 0:
                    streaks.append(current_streak)
                current_streak = 0
        
        if current_streak > 0:
            streaks.append(current_streak)
        
        return np.mean(streaks) if streaks else 0.0
    
    def _calculate_avg_loss_streak(self) -> float:
        """
        Calcula el promedio de rachas perdedoras
        
        Returns:
            Promedio de rachas perdedoras
        """
        if not self.trades:
            return 0.0
        
        streaks = []
        current_streak = 0
        
        for trade in self.trades:
            if trade.pnl <= 0:
                current_streak += 1
            else:
                if current_streak > 0:
                    streaks.append(current_streak)
                current_streak = 0
        
        if current_streak > 0:
            streaks.append(current_streak)
        
        return np.mean(streaks) if streaks else 0.0
    
    def _calculate_avg_winning_duration(self) -> float:
        """
        Calcula duración promedio de trades ganadores
        
        Returns:
            Duración promedio en barras
        """
        winning_durations = [t.duration_bars for t in self.trades if t.pnl > 0]
        
        return np.mean(winning_durations) if winning_durations else 0.0
    
    def _calculate_avg_losing_duration(self) -> float:
        """
        Calcula duración promedio de trades perdedores
        
        Returns:
            Duración promedio en barras
        """
        losing_durations = [t.duration_bars for t in self.trades if t.pnl <= 0]
        
        return np.mean(losing_durations) if losing_durations else 0.0
    
    def _calculate_risk_adjusted_return(self) -> float:
        """
        Calcula retorno ajustado por riesgo
        
        Returns:
            Retorno ajustado por riesgo
        """
        if len(self.returns) == 0:
            return 0.0
        
        total_return = (self.equity_curve.iloc[-1] / self.equity_curve.iloc[0] - 1)
        volatility = self.returns.std()
        
        if volatility == 0:
            return 0.0
        
        return total_return / volatility
    
    def _calculate_downside_volatility(self) -> float:
        """
        Calcula volatilidad a la baja
        
        Returns:
            Volatilidad a la baja anualizada
        """
        negative_returns = self.returns[self.returns < 0]
        
        if len(negative_returns) == 0:
            return 0.0
        
        return negative_returns.std() * np.sqrt(252)
    
    def analyze_trades_by_time(self) -> Dict:
        """
        Analiza trades por diferentes períodos de tiempo
        
        Returns:
            Diccionario con análisis temporal
        """
        if not self.trades:
            return {}
        
        trades_df = pd.DataFrame([
            {
                'entry_time': t.entry_time,
                'pnl': t.pnl,
                'hour': t.entry_time.hour,
                'day_of_week': t.entry_time.dayofweek,
                'month': t.entry_time.month
            }
            for t in self.trades
        ])
        
        analysis = {
            'by_hour': trades_df.groupby('hour')['pnl'].agg(['sum', 'mean', 'count']).to_dict(),
            'by_day_of_week': trades_df.groupby('day_of_week')['pnl'].agg(['sum', 'mean', 'count']).to_dict(),
            'by_month': trades_df.groupby('month')['pnl'].agg(['sum', 'mean', 'count']).to_dict(),
        }
        
        return analysis
    
    def calculate_trade_statistics(self) -> Dict:
        """
        Calcula estadísticas descriptivas de los trades
        
        Returns:
            Diccionario con estadísticas
        """
        if not self.trades:
            return {}
        
        pnls = [t.pnl for t in self.trades]
        pnl_pcts = [t.pnl_pct for t in self.trades]
        
        return {
            'pnl_mean': np.mean(pnls),
            'pnl_median': np.median(pnls),
            'pnl_std': np.std(pnls),
            'pnl_skew': stats.skew(pnls),
            'pnl_kurtosis': stats.kurtosis(pnls),
            'pnl_pct_mean': np.mean(pnl_pcts),
            'pnl_pct_median': np.median(pnl_pcts),
            'pnl_pct_std': np.std(pnl_pcts),
            'pnl_min': min(pnls),
            'pnl_max': max(pnls),
            'pnl_range': max(pnls) - min(pnls),
        }
