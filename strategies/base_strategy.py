"""
Clase base abstracta para estrategias de trading
"""
from abc import ABC, abstractmethod
import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


@dataclass
class Signal:
    """Representa una señal de trading"""
    timestamp: datetime
    signal_type: str  # 'BUY', 'SELL', 'CLOSE_LONG', 'CLOSE_SHORT'
    price: float
    stop_loss: Optional[float] = None
    take_profit: Optional[float] = None
    position_size: float = 0.0
    metadata: Dict = field(default_factory=dict)
    
    def __repr__(self):
        return f"Signal({self.signal_type} @ {self.price:.5f} at {self.timestamp})"


@dataclass
class Position:
    """Representa una posición abierta"""
    entry_timestamp: datetime
    entry_price: float
    position_type: str  # 'LONG' or 'SHORT'
    size: float
    stop_loss: Optional[float] = None
    take_profit: Optional[float] = None
    trailing_stop: Optional[float] = None
    highest_price: float = 0.0  # Para trailing stop en LONG
    lowest_price: float = float('inf')  # Para trailing stop en SHORT
    
    def update_trailing_stop(self, current_price: float, trailing_pct: float) -> None:
        """
        Actualiza el trailing stop basado en el precio actual
        
        Args:
            current_price: Precio actual
            trailing_pct: Porcentaje del trailing stop
        """
        if self.position_type == 'LONG':
            if current_price > self.highest_price:
                self.highest_price = current_price
                self.trailing_stop = current_price * (1 - trailing_pct)
        else:  # SHORT
            if current_price < self.lowest_price:
                self.lowest_price = current_price
                self.trailing_stop = current_price * (1 + trailing_pct)


class TradingStrategy(ABC):
    """
    Clase base abstracta para todas las estrategias de trading
    
    Todas las estrategias personalizadas deben heredar de esta clase
    e implementar los métodos abstractos.
    """
    
    def __init__(
        self,
        name: str,
        parameters: Dict,
        risk_per_trade: float = 0.02,
        use_trailing_stop: bool = True,
        trailing_stop_pct: float = 0.02
    ):
        """
        Inicializa la estrategia base
        
        Args:
            name: Nombre de la estrategia
            parameters: Diccionario con parámetros de la estrategia
            risk_per_trade: Porcentaje de riesgo por operación
            use_trailing_stop: Si usar trailing stop
            trailing_stop_pct: Porcentaje del trailing stop
        """
        self.name = name
        self.parameters = parameters
        self.risk_per_trade = risk_per_trade
        self.use_trailing_stop = use_trailing_stop
        self.trailing_stop_pct = trailing_stop_pct
        
        # Estado interno
        self.data: Optional[pd.DataFrame] = None
        self.indicators: Dict[str, pd.Series] = {}
        self.signals: List[Signal] = []
        self.positions: List[Position] = []
        self.current_position: Optional[Position] = None
        
        logger.info(f"Strategy '{name}' initialized with parameters: {parameters}")
    
    @abstractmethod
    def calculate_indicators(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Calcula los indicadores técnicos necesarios para la estrategia
        
        Args:
            data: DataFrame con datos OHLC
            
        Returns:
            DataFrame con indicadores añadidos
        """
        pass
    
    @abstractmethod
    def generate_signals(self, data: pd.DataFrame) -> List[Signal]:
        """
        Genera señales de trading basadas en los indicadores
        
        Args:
            data: DataFrame con datos e indicadores
            
        Returns:
            Lista de señales generadas
        """
        pass
    
    def manage_risk(
        self,
        signal: Signal,
        current_price: float,
        account_balance: float
    ) -> Signal:
        """
        Gestiona el riesgo de una señal calculando stop loss, take profit y tamaño
        
        Args:
            signal: Señal original
            current_price: Precio actual
            account_balance: Balance de la cuenta
            
        Returns:
            Señal con parámetros de riesgo actualizados
        """
        # Calcular stop loss si no está definido
        if signal.stop_loss is None:
            signal.stop_loss = self._calculate_stop_loss(signal, current_price)
        
        # Calcular take profit si no está definido
        if signal.take_profit is None:
            signal.take_profit = self._calculate_take_profit(signal, current_price)
        
        # Calcular tamaño de posición basado en riesgo
        signal.position_size = self._calculate_position_size(
            signal, current_price, account_balance
        )
        
        return signal
    
    def _calculate_stop_loss(self, signal: Signal, current_price: float) -> float:
        """
        Calcula el stop loss para una señal
        
        Args:
            signal: Señal de trading
            current_price: Precio actual
            
        Returns:
            Precio del stop loss
        """
        # Stop loss basado en ATR o porcentaje fijo
        atr_stop_multiplier = self.parameters.get('atr_stop_multiplier', 2.0)
        fixed_stop_pct = self.parameters.get('fixed_stop_pct', 0.02)
        
        if 'ATR' in self.indicators and len(self.indicators['ATR']) > 0:
            atr = self.indicators['ATR'].iloc[-1]
            if signal.signal_type == 'BUY':
                return current_price - (atr * atr_stop_multiplier)
            else:
                return current_price + (atr * atr_stop_multiplier)
        else:
            if signal.signal_type == 'BUY':
                return current_price * (1 - fixed_stop_pct)
            else:
                return current_price * (1 + fixed_stop_pct)
    
    def _calculate_take_profit(self, signal: Signal, current_price: float) -> float:
        """
        Calcula el take profit para una señal
        
        Args:
            signal: Señal de trading
            current_price: Precio actual
            
        Returns:
            Precio del take profit
        """
        # Take profit basado en risk-reward ratio
        risk_reward = self.parameters.get('risk_reward_ratio', 2.0)
        
        if signal.stop_loss:
            risk = abs(current_price - signal.stop_loss)
            reward = risk * risk_reward
            
            if signal.signal_type == 'BUY':
                return current_price + reward
            else:
                return current_price - reward
        else:
            # Fallback a porcentaje fijo
            fixed_tp_pct = self.parameters.get('fixed_tp_pct', 0.04)
            if signal.signal_type == 'BUY':
                return current_price * (1 + fixed_tp_pct)
            else:
                return current_price * (1 - fixed_tp_pct)
    
    def _calculate_position_size(
        self,
        signal: Signal,
        current_price: float,
        account_balance: float
    ) -> float:
        """
        Calcula el tamaño de la posición basado en el riesgo
        
        Args:
            signal: Señal de trading
            current_price: Precio actual
            account_balance: Balance de la cuenta
            
        Returns:
            Tamaño de la posición en unidades
        """
        # Cantidad en riesgo
        risk_amount = account_balance * self.risk_per_trade
        
        # Calcular stop loss en precio si no existe
        if signal.stop_loss is None:
            stop_loss = self._calculate_stop_loss(signal, current_price)
        else:
            stop_loss = signal.stop_loss
        
        # Riesgo por unidad
        risk_per_unit = abs(current_price - stop_loss)
        
        if risk_per_unit == 0:
            logger.warning("Risk per unit is zero, using minimum position size")
            return 0.01
        
        # Tamaño de posición
        position_size = risk_amount / risk_per_unit
        
        # Redondear a 2 decimales
        position_size = round(position_size, 2)
        
        # Asegurar tamaño mínimo
        min_size = self.parameters.get('min_position_size', 0.01)
        position_size = max(position_size, min_size)
        
        # Asegurar tamaño máximo
        max_size = self.parameters.get('max_position_size', 100.0)
        position_size = min(position_size, max_size)
        
        return position_size
    
    def check_exit_conditions(
        self,
        position: Position,
        current_bar: pd.Series
    ) -> Optional[Signal]:
        """
        Verifica condiciones de salida para una posición abierta
        
        Args:
            position: Posición actual
            current_bar: Barra actual con OHLC
            
        Returns:
            Señal de cierre si se cumple alguna condición, None en caso contrario
        """
        current_price = current_bar['close']
        
        # Actualizar trailing stop si está habilitado
        if self.use_trailing_stop:
            position.update_trailing_stop(current_price, self.trailing_stop_pct)
        
        # Verificar stop loss
        if position.stop_loss:
            if position.position_type == 'LONG' and current_bar['low'] <= position.stop_loss:
                return Signal(
                    timestamp=current_bar.name,
                    signal_type='CLOSE_LONG',
                    price=position.stop_loss,
                    metadata={'reason': 'stop_loss'}
                )
            elif position.position_type == 'SHORT' and current_bar['high'] >= position.stop_loss:
                return Signal(
                    timestamp=current_bar.name,
                    signal_type='CLOSE_SHORT',
                    price=position.stop_loss,
                    metadata={'reason': 'stop_loss'}
                )
        
        # Verificar trailing stop
        if position.trailing_stop:
            if position.position_type == 'LONG' and current_bar['low'] <= position.trailing_stop:
                return Signal(
                    timestamp=current_bar.name,
                    signal_type='CLOSE_LONG',
                    price=position.trailing_stop,
                    metadata={'reason': 'trailing_stop'}
                )
            elif position.position_type == 'SHORT' and current_bar['high'] >= position.trailing_stop:
                return Signal(
                    timestamp=current_bar.name,
                    signal_type='CLOSE_SHORT',
                    price=position.trailing_stop,
                    metadata={'reason': 'trailing_stop'}
                )
        
        # Verificar take profit
        if position.take_profit:
            if position.position_type == 'LONG' and current_bar['high'] >= position.take_profit:
                return Signal(
                    timestamp=current_bar.name,
                    signal_type='CLOSE_LONG',
                    price=position.take_profit,
                    metadata={'reason': 'take_profit'}
                )
            elif position.position_type == 'SHORT' and current_bar['low'] <= position.take_profit:
                return Signal(
                    timestamp=current_bar.name,
                    signal_type='CLOSE_SHORT',
                    price=position.take_profit,
                    metadata={'reason': 'take_profit'}
                )
        
        return None
    
    def run(self, data: pd.DataFrame) -> Tuple[pd.DataFrame, List[Signal]]:
        """
        Ejecuta la estrategia completa en los datos proporcionados
        
        Args:
            data: DataFrame con datos OHLC
            
        Returns:
            Tupla con (datos con indicadores, lista de señales)
        """
        # Guardar datos
        self.data = data.copy()
        
        # Calcular indicadores
        self.data = self.calculate_indicators(self.data)
        
        # Generar señales
        self.signals = self.generate_signals(self.data)
        
        logger.info(f"Strategy '{self.name}' generated {len(self.signals)} signals")
        
        return self.data, self.signals
    
    def get_parameter_ranges(self) -> Dict[str, Tuple]:
        """
        Define los rangos de parámetros para optimización
        
        Returns:
            Diccionario con rangos de parámetros {param_name: (min, max, step)}
        """
        # Implementar en estrategias específicas
        return {}
    
    def update_parameters(self, new_parameters: Dict) -> None:
        """
        Actualiza los parámetros de la estrategia
        
        Args:
            new_parameters: Nuevos parámetros
        """
        self.parameters.update(new_parameters)
        logger.info(f"Parameters updated: {self.parameters}")
    
    def reset(self) -> None:
        """Reinicia el estado de la estrategia"""
        self.signals = []
        self.positions = []
        self.current_position = None
        self.indicators = {}
        logger.info(f"Strategy '{self.name}' reset")
