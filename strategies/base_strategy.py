"""
Clase base abstracta para estrategias de trading
VERSIÓN CORREGIDA - Cálculo de lotaje correcto para todos los instrumentos
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
            risk_per_trade: Porcentaje de riesgo por operación (default 2%)
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
        account_balance: float,
        symbol_info: Optional[Dict] = None
    ) -> Signal:
        """
        Gestiona el riesgo de una señal calculando stop loss, take profit y tamaño.
        
        ⚠️ VERSIÓN CORREGIDA - Usa fórmula correcta para cálculo de lotaje
        
        Args:
            signal: Señal original
            current_price: Precio actual
            account_balance: Balance de la cuenta
            symbol_info: Información del símbolo (REQUERIDO para cálculo correcto)
                - point: Tamaño del punto (ej: 0.00001 para EURUSD, 0.01 para XAUUSD)
                - trade_contract_size: Tamaño del contrato (ej: 100000 para EURUSD, 100 para XAUUSD)
                - volume_min: Volumen mínimo permitido
                - volume_max: Volumen máximo permitido
                - volume_step: Incremento de volumen
            
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
        # IMPORTANTE: Pasar symbol_info para cálculo correcto
        signal.position_size = self._calculate_position_size(
            signal, 
            current_price, 
            account_balance,
            symbol_info
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
        account_balance: float,
        symbol_info: Optional[Dict] = None
    ) -> float:
        """
        ✅ FÓRMULA CORREGIDA - Calcula el tamaño de la posición basado en el riesgo.
        
        Fórmula Universal: Lotes = Riesgo_USD / (Distancia_Stop_Pips × Valor_Por_Pip)
        
        Args:
            signal: Señal de trading
            current_price: Precio actual
            account_balance: Balance de la cuenta
            symbol_info: Información del símbolo (REQUERIDO para cálculo correcto)
                - point: Tamaño del punto
                - trade_contract_size: Tamaño del contrato
                - volume_min: Volumen mínimo
                - volume_max: Volumen máximo
                - volume_step: Incremento de volumen
            
        Returns:
            Tamaño de la posición en lotes
            
        Examples:
            >>> # EURUSD: Balance $10k, Risk 2%, Entry 1.1000, SL 1.0980
            >>> symbol_info = {'point': 0.00001, 'trade_contract_size': 100000}
            >>> position_size = strategy._calculate_position_size(signal, 1.1000, 10000, symbol_info)
            >>> # Resultado: 1.00 lotes (200 USD / (200 pips × $1/pip))
            
            >>> # XAUUSD: Balance $10k, Risk 2%, Entry 2650, SL 2616
            >>> symbol_info = {'point': 0.01, 'trade_contract_size': 100}
            >>> position_size = strategy._calculate_position_size(signal, 2650, 10000, symbol_info)
            >>> # Resultado: 0.06 lotes (200 USD / (3400 pips × $1/pip))
        """
        # Cantidad en riesgo (USD)
        risk_amount = account_balance * self.risk_per_trade
        
        # Calcular stop loss en precio si no existe
        if signal.stop_loss is None:
            stop_loss = self._calculate_stop_loss(signal, current_price)
        else:
            stop_loss = signal.stop_loss
        
        # Validar que tenemos información del símbolo
        if symbol_info is None:
            logger.warning(
                "⚠️ symbol_info not provided to _calculate_position_size. "
                "Using default values for FOREX (EURUSD-like). "
                "This may produce INCORRECT results for other instruments like GOLD, INDICES, etc."
            )
            symbol_info = {
                'point': 0.00001,
                'trade_contract_size': 100000,
                'volume_min': 0.01,
                'volume_max': 100.0,
                'volume_step': 0.01
            }
        
        # Obtener información del instrumento
        point_size = symbol_info.get('point', 0.00001)
        contract_size = symbol_info.get('trade_contract_size', 100000)
        
        # Calcular distancia del stop en pips/puntos
        stop_distance_price = abs(current_price - stop_loss)
        stop_distance_pips = stop_distance_price / point_size
        
        # Validación: stop distance debe ser mayor a 0
        if stop_distance_pips == 0:
            logger.error(
                f"❌ Stop distance is zero! Entry: {current_price}, SL: {stop_loss}. "
                f"Using minimum position size."
            )
            return symbol_info.get('volume_min', 0.01)
        
        # Calcular valor por pip (cuánto vale 1 pip de movimiento por 1 lote)
        value_per_pip = contract_size * point_size
        
        # ✅ FÓRMULA CORRECTA
        # Lotes = Riesgo_USD / (Distancia_Stop_Pips × Valor_Por_Pip)
        position_size_calculated = risk_amount / (stop_distance_pips * value_per_pip)
        
        # Obtener límites del broker
        min_size = symbol_info.get('volume_min', 0.01)
        max_size = symbol_info.get('volume_max', 100.0)
        volume_step = symbol_info.get('volume_step', 0.01)
        
        # Redondear al step válido del broker
        position_size = round(position_size_calculated / volume_step) * volume_step
        
        # Aplicar límites del broker
        position_size = max(min_size, min(position_size, max_size))
        
        # Redondear a 2 decimales para claridad
        position_size = round(position_size, 2)
        
        # Logging detallado
        logger.info(
            f"📊 Position size calculation: "
            f"Risk=${risk_amount:.2f} ({self.risk_per_trade*100:.1f}%), "
            f"Stop={stop_distance_pips:.1f} pips, "
            f"Value/pip=${value_per_pip:.5f}, "
            f"Result={position_size:.2f} lots"
        )
        
        # Validación adicional: alertar si el tamaño es inusual
        if position_size == max_size:
            logger.warning(
                f"⚠️ Position size hit maximum limit of {max_size} lots. "
                f"Consider reducing risk or increasing stop distance."
            )
        
        if position_size == min_size and position_size_calculated < min_size:
            logger.warning(
                f"⚠️ Position size hit minimum limit of {min_size} lots. "
                f"Calculated size was {position_size_calculated:.4f} lots. "
                f"Actual risk may be higher than intended."
            )
        
        # Calcular el riesgo real que se va a tomar
        actual_risk = position_size * stop_distance_pips * value_per_pip
        actual_risk_pct = (actual_risk / account_balance) * 100
        
        logger.info(
            f"💰 Actual risk: ${actual_risk:.2f} ({actual_risk_pct:.2f}% of balance)"
        )
        
        # Alerta si el riesgo real difiere significativamente del objetivo
        risk_difference = abs(actual_risk - risk_amount)
        if risk_difference > risk_amount * 0.1:  # Más de 10% de diferencia
            logger.warning(
                f"⚠️ Actual risk (${actual_risk:.2f}) differs from target "
                f"(${risk_amount:.2f}) by ${risk_difference:.2f}"
            )
        
        return position_size
    
    def check_exit_conditions(
        self,
        position: Position,
        current_bar: pd.Series
    ) -> Optional[Signal]:
        """
        Verifica si se deben cerrar posiciones abiertas
        
        Args:
            position: Posición actual
            current_bar: Barra actual
            
        Returns:
            Signal de cierre si se cumplen condiciones, None en caso contrario
        """
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
        
        # Verificar trailing stop
        if self.use_trailing_stop and position.trailing_stop:
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
    
    # =========================================================================
    # MÉTODOS DE UTILIDAD PARA INDICADORES TÉCNICOS
    # =========================================================================
    
    @staticmethod
    def calculate_sma(series: pd.Series, period: int) -> pd.Series:
        """Calcula Simple Moving Average"""
        return series.rolling(window=period).mean()
    
    @staticmethod
    def calculate_ema(series: pd.Series, period: int) -> pd.Series:
        """Calcula Exponential Moving Average"""
        return series.ewm(span=period, adjust=False).mean()
    
    @staticmethod
    def calculate_rsi(series: pd.Series, period: int = 14) -> pd.Series:
        """Calcula Relative Strength Index"""
        delta = series.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        
        return rsi
    
    @staticmethod
    def calculate_atr(data: pd.DataFrame, period: int = 14) -> pd.Series:
        """Calcula Average True Range"""
        high = data['high']
        low = data['low']
        close = data['close']
        
        tr1 = high - low
        tr2 = abs(high - close.shift())
        tr3 = abs(low - close.shift())
        
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        atr = tr.rolling(window=period).mean()
        
        return atr
    
    @staticmethod
    def calculate_bollinger_bands(
        series: pd.Series,
        period: int = 20,
        num_std: float = 2.0
    ) -> Tuple[pd.Series, pd.Series, pd.Series]:
        """Calcula Bandas de Bollinger"""
        middle = series.rolling(window=period).mean()
        std = series.rolling(window=period).std()
        
        upper = middle + (std * num_std)
        lower = middle - (std * num_std)
        
        return upper, middle, lower
    
    @staticmethod
    def calculate_macd(
        series: pd.Series,
        fast: int = 12,
        slow: int = 26,
        signal: int = 9
    ) -> Tuple[pd.Series, pd.Series, pd.Series]:
        """Calcula MACD"""
        ema_fast = series.ewm(span=fast, adjust=False).mean()
        ema_slow = series.ewm(span=slow, adjust=False).mean()
        
        macd_line = ema_fast - ema_slow
        signal_line = macd_line.ewm(span=signal, adjust=False).mean()
        histogram = macd_line - signal_line
        
        return macd_line, signal_line, histogram
    
    @staticmethod
    def calculate_stochastic(
        data: pd.DataFrame,
        period: int = 14,
        smooth_k: int = 3,
        smooth_d: int = 3
    ) -> Tuple[pd.Series, pd.Series]:
        """Calcula Estocástico"""
        low_min = data['low'].rolling(window=period).min()
        high_max = data['high'].rolling(window=period).max()
        
        k = 100 * ((data['close'] - low_min) / (high_max - low_min))
        k = k.rolling(window=smooth_k).mean()
        d = k.rolling(window=smooth_d).mean()
        
        return k, d
