"""
Motor de Backtesting para estrategias de trading
Simula ejecución de órdenes, gestión de riesgo y cálculo de métricas
"""
import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime
import logging
from strategies.base_strategy import TradingStrategy, Signal, Position
from config.settings import BacktestConfig

logger = logging.getLogger(__name__)


@dataclass
class Trade:
    """Representa una operación completa (entrada y salida)"""
    entry_time: datetime
    exit_time: datetime
    entry_price: float
    exit_price: float
    trade_type: str  # 'LONG' or 'SHORT'
    size: float
    pnl: float
    pnl_pct: float
    commission: float
    slippage: float
    stop_loss: Optional[float] = None
    take_profit: Optional[float] = None
    exit_reason: str = 'signal'
    mae: float = 0.0  # Maximum Adverse Excursion
    mfe: float = 0.0  # Maximum Favorable Excursion
    duration_bars: int = 0
    
    def __repr__(self):
        return f"Trade({self.trade_type}: {self.pnl:.2f} ({self.pnl_pct:.2%}))"


@dataclass
class BacktestResult:
    """Resultado completo del backtesting"""
    trades: List[Trade]
    equity_curve: pd.Series
    balance_curve: pd.Series
    drawdown_curve: pd.Series
    metrics: Dict
    data_with_signals: pd.DataFrame
    initial_capital: float
    final_capital: float
    
    def summary(self) -> str:
        """Retorna un resumen del backtest"""
        lines = [
            "=" * 60,
            "BACKTEST SUMMARY",
            "=" * 60,
            f"Initial Capital: ${self.initial_capital:,.2f}",
            f"Final Capital: ${self.final_capital:,.2f}",
            f"Net P&L: ${self.final_capital - self.initial_capital:,.2f}",
            f"Return: {((self.final_capital/self.initial_capital - 1) * 100):.2f}%",
            "",
            f"Total Trades: {self.metrics.get('total_trades', 0)}",
            f"Win Rate: {self.metrics.get('win_rate', 0):.2%}",
            f"Profit Factor: {self.metrics.get('profit_factor', 0):.2f}",
            f"Sharpe Ratio: {self.metrics.get('sharpe_ratio', 0):.2f}",
            f"Max Drawdown: {self.metrics.get('max_drawdown', 0):.2%}",
            f"Average Win: ${self.metrics.get('avg_win', 0):.2f}",
            f"Average Loss: ${self.metrics.get('avg_loss', 0):.2f}",
            f"Expectancy: ${self.metrics.get('expectancy', 0):.2f}",
            "=" * 60
        ]
        return "\n".join(lines)


class BacktestEngine:
    """
    Motor de backtesting completo con:
    - Simulación realista de ejecución de órdenes
    - Gestión de margen y apalancamiento
    - Cálculo de spread, comisiones y slippage
    - Métricas de rendimiento completas
    """
    
    def __init__(self, config: Optional[BacktestConfig] = None):
        """
        Inicializa el motor de backtesting
        
        Args:
            config: Configuración del backtest
        """
        self.config = config or BacktestConfig()
        
        # Estado del backtest
        self.current_balance = self.config.initial_capital
        self.equity = self.config.initial_capital
        self.current_position: Optional[Position] = None
        self.trades: List[Trade] = []
        self.equity_curve: List[float] = [self.config.initial_capital]
        self.balance_curve: List[float] = [self.config.initial_capital]
        self.timestamps: List[datetime] = []
        
        # Tracking para MAE/MFE
        self.position_high = 0.0
        self.position_low = float('inf')
        
        logger.info(f"BacktestEngine initialized with capital: ${self.config.initial_capital:,.2f}")
    
    def run(
        self,
        strategy: TradingStrategy,
        data: pd.DataFrame,
        symbol_info: Optional[Dict] = None
    ) -> BacktestResult:
        """
        Ejecuta el backtest completo
        
        Args:
            strategy: Estrategia a probar
            data: Datos históricos
            symbol_info: Información del símbolo (spread, point, etc)
            
        Returns:
            Resultado completo del backtest
        """
        logger.info(f"Starting backtest for strategy: {strategy.name}")
        
        # Resetear estado
        self._reset()
        
        # Ejecutar estrategia para obtener indicadores y señales
        data_with_indicators, signals = strategy.run(data)
        
        # Crear índice de señales para búsqueda rápida
        signals_dict = {s.timestamp: s for s in signals}
        
        # Simular trading
        for i, (timestamp, bar) in enumerate(data_with_indicators.iterrows()):
            # Actualizar timestamp
            self.timestamps.append(timestamp)
            
            # Verificar señales de entrada
            if timestamp in signals_dict and self.current_position is None:
                signal = signals_dict[timestamp]
                if signal.signal_type in ['BUY', 'SELL']:
                    self._open_position(signal, bar, symbol_info, strategy)
            
            # Gestión de posición abierta
            if self.current_position:
                # Verificar condiciones de salida
                exit_signal = strategy.check_exit_conditions(self.current_position, bar)
                
                if exit_signal:
                    self._close_position(exit_signal, bar, symbol_info)
                else:
                    # Actualizar MAE/MFE
                    self._update_mae_mfe(bar)
                    
                    # Actualizar equity
                    self._update_equity(bar)
            
            # Registrar balance y equity
            self.balance_curve.append(self.current_balance)
            self.equity_curve.append(self.equity)
        
        # Cerrar posición abierta al final
        if self.current_position:
            final_bar = data_with_indicators.iloc[-1]
            exit_signal = Signal(
                timestamp=final_bar.name,
                signal_type='CLOSE_LONG' if self.current_position.position_type == 'LONG' else 'CLOSE_SHORT',
                price=final_bar['close'],
                metadata={'reason': 'end_of_data'}
            )
            self._close_position(exit_signal, final_bar, symbol_info)
        
        # Calcular métricas
        metrics = self._calculate_metrics()
        
        # Crear curvas como Series
        equity_series = pd.Series(self.equity_curve, index=self.timestamps + [self.timestamps[-1]])
        balance_series = pd.Series(self.balance_curve, index=self.timestamps + [self.timestamps[-1]])
        
        # Calcular drawdown
        drawdown_series = self._calculate_drawdown(equity_series)
        
        # Añadir señales al dataframe
        data_with_signals = self._add_signals_to_data(data_with_indicators, signals, self.trades)
        
        result = BacktestResult(
            trades=self.trades,
            equity_curve=equity_series,
            balance_curve=balance_series,
            drawdown_curve=drawdown_series,
            metrics=metrics,
            data_with_signals=data_with_signals,
            initial_capital=self.config.initial_capital,
            final_capital=self.equity
        )
        
        logger.info(f"Backtest completed: {len(self.trades)} trades executed")
        logger.info(f"Final Capital: ${self.equity:,.2f} (Return: {((self.equity/self.config.initial_capital - 1) * 100):.2f}%)")
        
        return result
    
    def _open_position(
        self,
        signal: Signal,
        bar: pd.Series,
        symbol_info: Optional[Dict],
        strategy: TradingStrategy
    ) -> None:
        """
        Abre una nueva posición
        
        Args:
            signal: Señal de entrada
            bar: Barra actual
            symbol_info: Información del símbolo
            strategy: Estrategia que genera la señal
        """
        # Aplicar gestión de riesgo
        signal = strategy.manage_risk(signal, bar['close'], self.current_balance)
        
        # Calcular precio de ejecución con slippage
        execution_price = self._apply_slippage(signal.price, signal.signal_type)
        
        # Aplicar spread si está habilitado
        if self.config.use_spread and symbol_info:
            spread = symbol_info.get('spread', 0) * symbol_info.get('point', 0.00001)
            if signal.signal_type == 'BUY':
                execution_price += spread
            else:
                execution_price -= spread
        
        # Verificar margen disponible
        required_margin = self._calculate_required_margin(
            execution_price, signal.position_size, symbol_info
        )
        
        if required_margin > self.current_balance * 0.9:  # 90% del balance
            logger.warning(f"Insufficient margin for position: {required_margin:.2f} > {self.current_balance:.2f}")
            return
        
        # Crear posición
        position_type = 'LONG' if signal.signal_type == 'BUY' else 'SHORT'
        
        self.current_position = Position(
            entry_timestamp=signal.timestamp,
            entry_price=execution_price,
            position_type=position_type,
            size=signal.position_size,
            stop_loss=signal.stop_loss,
            take_profit=signal.take_profit
        )
        
        # Inicializar MAE/MFE tracking
        self.position_high = execution_price
        self.position_low = execution_price
        
        logger.info(f"Opened {position_type} position: {signal.position_size} @ {execution_price:.5f}")
    
    def _close_position(
        self,
        signal: Signal,
        bar: pd.Series,
        symbol_info: Optional[Dict]
    ) -> None:
        """
        Cierra la posición actual
        
        Args:
            signal: Señal de salida
            bar: Barra actual
            symbol_info: Información del símbolo
        """
        if not self.current_position:
            return
        
        # Calcular precio de ejecución con slippage
        execution_price = self._apply_slippage(signal.price, signal.signal_type)
        
        # Aplicar spread
        if self.config.use_spread and symbol_info:
            spread = symbol_info.get('spread', 0) * symbol_info.get('point', 0.00001)
            if signal.signal_type == 'CLOSE_LONG':
                execution_price -= spread
            else:
                execution_price += spread
        
        # Calcular P&L
        if self.current_position.position_type == 'LONG':
            pnl = (execution_price - self.current_position.entry_price) * self.current_position.size
        else:  # SHORT
            pnl = (self.current_position.entry_price - execution_price) * self.current_position.size
        
        # Calcular comisiones
        commission = self._calculate_commission(
            self.current_position.entry_price,
            execution_price,
            self.current_position.size,
            symbol_info
        )
        
        # PnL neto
        net_pnl = pnl - commission
        pnl_pct = net_pnl / (self.current_position.entry_price * self.current_position.size)
        
        # Actualizar balance
        self.current_balance += net_pnl
        self.equity = self.current_balance
        
        # Calcular MAE/MFE
        mae, mfe = self._calculate_mae_mfe(execution_price)
        
        # Calcular duración
        duration = len([t for t in self.timestamps if t >= self.current_position.entry_timestamp])
        
        # Crear registro de trade
        trade = Trade(
            entry_time=self.current_position.entry_timestamp,
            exit_time=signal.timestamp,
            entry_price=self.current_position.entry_price,
            exit_price=execution_price,
            trade_type=self.current_position.position_type,
            size=self.current_position.size,
            pnl=net_pnl,
            pnl_pct=pnl_pct,
            commission=commission,
            slippage=abs(execution_price - signal.price) * self.current_position.size,
            stop_loss=self.current_position.stop_loss,
            take_profit=self.current_position.take_profit,
            exit_reason=signal.metadata.get('reason', 'signal'),
            mae=mae,
            mfe=mfe,
            duration_bars=duration
        )
        
        self.trades.append(trade)
        
        logger.info(f"Closed {trade.trade_type} position: PnL = ${net_pnl:.2f} ({pnl_pct:.2%}) - Reason: {trade.exit_reason}")
        
        # Limpiar posición
        self.current_position = None
    
    def _apply_slippage(self, price: float, signal_type: str) -> float:
        """
        Aplica slippage al precio de ejecución
        
        Args:
            price: Precio teórico
            signal_type: Tipo de señal
            
        Returns:
            Precio con slippage aplicado
        """
        slippage = price * self.config.slippage_pct
        
        if signal_type in ['BUY', 'CLOSE_SHORT']:
            return price + slippage
        else:
            return price - slippage
    
    def _calculate_commission(
        self,
        entry_price: float,
        exit_price: float,
        size: float,
        symbol_info: Optional[Dict]
    ) -> float:
        """
        Calcula comisiones de la operación
        
        Args:
            entry_price: Precio de entrada
            exit_price: Precio de salida
            size: Tamaño de la posición
            symbol_info: Información del símbolo
            
        Returns:
            Comisión total
        """
        # Comisión fija
        fixed_commission = self.config.commission * 2  # Entrada y salida
        
        # Comisión porcentual
        volume = (entry_price + exit_price) * size
        pct_commission = volume * self.config.commission_pct
        
        return fixed_commission + pct_commission
    
    def _calculate_required_margin(
        self,
        price: float,
        size: float,
        symbol_info: Optional[Dict]
    ) -> float:
        """
        Calcula el margen requerido para una posición
        
        Args:
            price: Precio de entrada
            size: Tamaño de la posición
            symbol_info: Información del símbolo
            
        Returns:
            Margen requerido
        """
        contract_size = 1.0
        if symbol_info:
            contract_size = symbol_info.get('trade_contract_size', 1.0)
        
        position_value = price * size * contract_size
        required_margin = position_value / self.config.leverage
        
        return required_margin
    
    def _update_mae_mfe(self, bar: pd.Series) -> None:
        """
        Actualiza Maximum Adverse/Favorable Excursion
        
        Args:
            bar: Barra actual
        """
        self.position_high = max(self.position_high, bar['high'])
        self.position_low = min(self.position_low, bar['low'])
    
    def _calculate_mae_mfe(self, exit_price: float) -> Tuple[float, float]:
        """
        Calcula MAE y MFE al cierre de la posición
        
        Args:
            exit_price: Precio de salida
            
        Returns:
            Tupla (MAE, MFE)
        """
        if not self.current_position:
            return 0.0, 0.0
        
        entry = self.current_position.entry_price
        
        if self.current_position.position_type == 'LONG':
            mae = (self.position_low - entry) / entry
            mfe = (self.position_high - entry) / entry
        else:  # SHORT
            mae = (entry - self.position_high) / entry
            mfe = (entry - self.position_low) / entry
        
        return mae, mfe
    
    def _update_equity(self, bar: pd.Series) -> None:
        """
        Actualiza el equity considerando posiciones abiertas
        
        Args:
            bar: Barra actual
        """
        if not self.current_position:
            self.equity = self.current_balance
            return
        
        current_price = bar['close']
        
        if self.current_position.position_type == 'LONG':
            unrealized_pnl = (current_price - self.current_position.entry_price) * self.current_position.size
        else:
            unrealized_pnl = (self.current_position.entry_price - current_price) * self.current_position.size
        
        self.equity = self.current_balance + unrealized_pnl
    
    def _calculate_metrics(self) -> Dict:
        """
        Calcula todas las métricas de rendimiento
        
        Returns:
            Diccionario con métricas
        """
        if not self.trades:
            return {'total_trades': 0}
        
        # Datos básicos
        total_trades = len(self.trades)
        wins = [t for t in self.trades if t.pnl > 0]
        losses = [t for t in self.trades if t.pnl <= 0]
        
        winning_trades = len(wins)
        losing_trades = len(losses)
        
        # Win rate
        win_rate = winning_trades / total_trades if total_trades > 0 else 0
        
        # P&L
        total_pnl = sum(t.pnl for t in self.trades)
        gross_profit = sum(t.pnl for t in wins)
        gross_loss = abs(sum(t.pnl for t in losses))
        
        # Profit factor
        profit_factor = gross_profit / gross_loss if gross_loss > 0 else float('inf')
        
        # Average win/loss
        avg_win = gross_profit / winning_trades if winning_trades > 0 else 0
        avg_loss = gross_loss / losing_trades if losing_trades > 0 else 0
        
        # Expectancy
        expectancy = (win_rate * avg_win) - ((1 - win_rate) * avg_loss)
        
        # Risk/Reward ratio
        avg_risk_reward = avg_win / avg_loss if avg_loss > 0 else 0
        
        # Sharpe Ratio
        returns = pd.Series([t.pnl_pct for t in self.trades])
        sharpe_ratio = self._calculate_sharpe_ratio(returns)
        
        # Maximum Drawdown
        equity_series = pd.Series(self.equity_curve)
        max_drawdown = self._calculate_max_drawdown(equity_series)
        
        # Average MAE/MFE
        avg_mae = np.mean([t.mae for t in self.trades])
        avg_mfe = np.mean([t.mfe for t in self.trades])
        
        # Duración promedio
        avg_duration = np.mean([t.duration_bars for t in self.trades])
        
        # Recovery Factor
        recovery_factor = total_pnl / abs(max_drawdown * self.config.initial_capital) if max_drawdown != 0 else 0
        
        # Calmar Ratio
        annual_return = (self.equity / self.config.initial_capital - 1)
        calmar_ratio = annual_return / abs(max_drawdown) if max_drawdown != 0 else 0
        
        metrics = {
            'total_trades': total_trades,
            'winning_trades': winning_trades,
            'losing_trades': losing_trades,
            'win_rate': win_rate,
            'total_pnl': total_pnl,
            'gross_profit': gross_profit,
            'gross_loss': gross_loss,
            'profit_factor': profit_factor,
            'avg_win': avg_win,
            'avg_loss': avg_loss,
            'expectancy': expectancy,
            'avg_risk_reward': avg_risk_reward,
            'sharpe_ratio': sharpe_ratio,
            'max_drawdown': max_drawdown,
            'recovery_factor': recovery_factor,
            'calmar_ratio': calmar_ratio,
            'avg_mae': avg_mae,
            'avg_mfe': avg_mfe,
            'avg_duration_bars': avg_duration,
            'total_commission': sum(t.commission for t in self.trades),
            'total_slippage': sum(t.slippage for t in self.trades),
        }
        
        return metrics
    
    def _calculate_sharpe_ratio(self, returns: pd.Series, risk_free_rate: float = 0.02) -> float:
        """
        Calcula el Sharpe Ratio
        
        Args:
            returns: Serie de retornos
            risk_free_rate: Tasa libre de riesgo anual
            
        Returns:
            Sharpe Ratio
        """
        if len(returns) == 0:
            return 0.0
        
        excess_returns = returns - (risk_free_rate / 252)  # Daily risk-free rate
        
        if excess_returns.std() == 0:
            return 0.0
        
        sharpe = excess_returns.mean() / excess_returns.std() * np.sqrt(252)
        
        return sharpe
    
    def _calculate_max_drawdown(self, equity_curve: pd.Series) -> float:
        """
        Calcula el máximo drawdown
        
        Args:
            equity_curve: Serie de equity
            
        Returns:
            Máximo drawdown como porcentaje
        """
        cummax = equity_curve.cummax()
        drawdown = (equity_curve - cummax) / cummax
        max_dd = drawdown.min()
        
        return max_dd
    
    def _calculate_drawdown(self, equity_curve: pd.Series) -> pd.Series:
        """
        Calcula la serie de drawdown
        
        Args:
            equity_curve: Serie de equity
            
        Returns:
            Serie de drawdown
        """
        cummax = equity_curve.cummax()
        drawdown = (equity_curve - cummax) / cummax
        
        return drawdown
    
    def _add_signals_to_data(
        self,
        data: pd.DataFrame,
        signals: List[Signal],
        trades: List[Trade]
    ) -> pd.DataFrame:
        """
        Añade columnas de señales y trades al dataframe
        
        Args:
            data: DataFrame original
            signals: Lista de señales
            trades: Lista de trades
            
        Returns:
            DataFrame con señales añadidas
        """
        df = data.copy()
        
        # Inicializar columnas
        df['signal'] = 0
        df['position'] = 0
        df['trade_pnl'] = 0.0
        
        # Añadir señales
        for signal in signals:
            if signal.timestamp in df.index:
                if signal.signal_type == 'BUY':
                    df.loc[signal.timestamp, 'signal'] = 1
                elif signal.signal_type == 'SELL':
                    df.loc[signal.timestamp, 'signal'] = -1
        
        # Añadir trades
        for trade in trades:
            mask = (df.index >= trade.entry_time) & (df.index <= trade.exit_time)
            df.loc[mask, 'position'] = 1 if trade.trade_type == 'LONG' else -1
            df.loc[trade.exit_time, 'trade_pnl'] = trade.pnl
        
        return df
    
    def _reset(self) -> None:
        """Resetea el estado del backtest"""
        self.current_balance = self.config.initial_capital
        self.equity = self.config.initial_capital
        self.current_position = None
        self.trades = []
        self.equity_curve = [self.config.initial_capital]
        self.balance_curve = [self.config.initial_capital]
        self.timestamps = []
        self.position_high = 0.0
        self.position_low = float('inf')
