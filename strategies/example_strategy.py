"""
Estrategia de ejemplo: Cruce de Medias Móviles con filtro RSI
"""

import pandas as pd
import numpy as np
from typing import Optional
from strategies.base_strategy import TradingStrategy, TradeSignal, SignalType


class MovingAverageCrossover(TradingStrategy):
    """
    Estrategia de cruce de medias móviles con filtro RSI
    
    Señales:
    - BUY: EMA rápida cruza por encima de EMA lenta + RSI > 50
    - SELL: EMA rápida cruza por debajo de EMA lenta + RSI < 50
    
    Gestión de riesgo:
    - Stop Loss basado en ATR
    - Take Profit en ratio 2:1
    - Trailing stop dinámico
    """
    
    def __init__(
        self,
        fast_period: int = 12,
        slow_period: int = 26,
        rsi_period: int = 14,
        rsi_overbought: float = 70,
        rsi_oversold: float = 30,
        atr_period: int = 14,
        atr_multiplier: float = 2.0,
        risk_percent: float = 0.02,
        reward_ratio: float = 2.0
    ):
        """
        Inicializa la estrategia
        
        Args:
            fast_period: Período de EMA rápida
            slow_period: Período de EMA lenta
            rsi_period: Período del RSI
            rsi_overbought: Nivel de sobrecompra RSI
            rsi_oversold: Nivel de sobreventa RSI
            atr_period: Período del ATR
            atr_multiplier: Multiplicador ATR para Stop Loss
            risk_percent: Porcentaje de riesgo por operación
            reward_ratio: Ratio Reward/Risk para Take Profit
        """
        parameters = {
            'fast_period': fast_period,
            'slow_period': slow_period,
            'rsi_period': rsi_period,
            'rsi_overbought': rsi_overbought,
            'rsi_oversold': rsi_oversold,
            'atr_period': atr_period,
            'atr_multiplier': atr_multiplier,
            'risk_percent': risk_percent,
            'reward_ratio': reward_ratio
        }
        
        super().__init__(name="MA Crossover + RSI", parameters=parameters)
    
    def calculate_indicators(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Calcula indicadores técnicos
        
        Args:
            data: DataFrame con datos OHLC
            
        Returns:
            DataFrame con indicadores añadidos
        """
        df = data.copy()
        
        # Medias móviles exponenciales
        df['ema_fast'] = self.calculate_ema(
            df['close'], 
            self.parameters['fast_period']
        )
        df['ema_slow'] = self.calculate_ema(
            df['close'], 
            self.parameters['slow_period']
        )
        
        # RSI
        df['rsi'] = self.calculate_rsi(
            df['close'], 
            self.parameters['rsi_period']
        )
        
        # ATR para stop loss
        df['atr'] = self.calculate_atr(
            df, 
            self.parameters['atr_period']
        )
        
        # Detectar cruces
        df['ema_diff'] = df['ema_fast'] - df['ema_slow']
        df['ema_cross'] = np.sign(df['ema_diff'].diff())
        
        return df
    
    def generate_signals(self, data: pd.DataFrame) -> pd.Series:
        """
        Genera señales de trading
        
        Args:
            data: DataFrame con datos e indicadores
            
        Returns:
            Series con señales (1: BUY, -1: SELL, 0: HOLD)
        """
        signals = pd.Series(0, index=data.index)
        
        # Parámetros
        rsi_ob = self.parameters['rsi_overbought']
        rsi_os = self.parameters['rsi_oversold']
        
        # Señales de compra
        buy_condition = (
            (data['ema_cross'] == 1) &  # Cruce alcista
            (data['rsi'] > 50) &  # RSI en zona alcista
            (data['rsi'] < rsi_ob)  # No sobrecomprado
        )
        
        # Señales de venta
        sell_condition = (
            (data['ema_cross'] == -1) &  # Cruce bajista
            (data['rsi'] < 50) &  # RSI en zona bajista
            (data['rsi'] > rsi_os)  # No sobrevendido
        )
        
        signals[buy_condition] = 1
        signals[sell_condition] = -1
        
        return signals
    
    def manage_risk(
        self,
        data: pd.DataFrame,
        signal: TradeSignal,
        balance: float
    ) -> TradeSignal:
        """
        Gestiona el riesgo de la operación
        
        Args:
            data: DataFrame con datos históricos
            signal: Señal de trading inicial
            balance: Balance actual de la cuenta
            
        Returns:
            Señal con gestión de riesgo aplicada
        """
        # Obtener última barra
        last_bar = data.iloc[-1]
        current_price = signal.price
        
        # Calcular ATR si no existe en los datos
        if 'atr' not in last_bar or pd.isna(last_bar['atr']):
            atr_series = self.calculate_atr(data, self.parameters['atr_period'])
            atr = atr_series.iloc[-1]
        else:
            atr = last_bar['atr']
        
        # Calcular Stop Loss basado en ATR
        atr_multiplier = self.parameters['atr_multiplier']
        
        if signal.signal_type == SignalType.BUY:
            stop_loss = current_price - (atr * atr_multiplier)
            take_profit = current_price + (atr * atr_multiplier * 
                                          self.parameters['reward_ratio'])
        else:  # SELL
            stop_loss = current_price + (atr * atr_multiplier)
            take_profit = current_price - (atr * atr_multiplier * 
                                          self.parameters['reward_ratio'])
        
        # Calcular tamaño de posición
        risk_percent = self.parameters['risk_percent']
        point_value = 1.0  # Ajustar según el instrumento
        
        volume = self.calculate_position_size(
            balance=balance,
            risk_percent=risk_percent,
            entry_price=current_price,
            stop_loss=stop_loss,
            point_value=point_value
        )
        
        # Actualizar señal
        signal.stop_loss = stop_loss
        signal.take_profit = take_profit
        signal.volume = volume
        signal.comment = f"{self.name} | ATR: {atr:.5f}"
        
        return signal


class RSIMomentumStrategy(TradingStrategy):
    """
    Estrategia basada en momentum del RSI
    
    Señales:
    - BUY: RSI sale de sobreventa (cruza 30 hacia arriba)
    - SELL: RSI sale de sobrecompra (cruza 70 hacia abajo)
    """
    
    def __init__(
        self,
        rsi_period: int = 14,
        rsi_overbought: float = 70,
        rsi_oversold: float = 30,
        atr_period: int = 14,
        atr_sl_multiplier: float = 1.5,
        atr_tp_multiplier: float = 3.0,
        risk_percent: float = 0.02
    ):
        """Inicializa estrategia RSI Momentum"""
        parameters = {
            'rsi_period': rsi_period,
            'rsi_overbought': rsi_overbought,
            'rsi_oversold': rsi_oversold,
            'atr_period': atr_period,
            'atr_sl_multiplier': atr_sl_multiplier,
            'atr_tp_multiplier': atr_tp_multiplier,
            'risk_percent': risk_percent
        }
        
        super().__init__(name="RSI Momentum", parameters=parameters)
    
    def calculate_indicators(self, data: pd.DataFrame) -> pd.DataFrame:
        """Calcula indicadores"""
        df = data.copy()
        
        # RSI
        df['rsi'] = self.calculate_rsi(df['close'], self.parameters['rsi_period'])
        
        # ATR
        df['atr'] = self.calculate_atr(df, self.parameters['atr_period'])
        
        # Niveles RSI
        df['rsi_prev'] = df['rsi'].shift(1)
        
        return df
    
    def generate_signals(self, data: pd.DataFrame) -> pd.Series:
        """Genera señales basadas en RSI"""
        signals = pd.Series(0, index=data.index)
        
        rsi_ob = self.parameters['rsi_overbought']
        rsi_os = self.parameters['rsi_oversold']
        
        # Compra: RSI cruza 30 hacia arriba
        buy_condition = (
            (data['rsi_prev'] < rsi_os) &
            (data['rsi'] >= rsi_os)
        )
        
        # Venta: RSI cruza 70 hacia abajo
        sell_condition = (
            (data['rsi_prev'] > rsi_ob) &
            (data['rsi'] <= rsi_ob)
        )
        
        signals[buy_condition] = 1
        signals[sell_condition] = -1
        
        return signals
    
    def manage_risk(
        self,
        data: pd.DataFrame,
        signal: TradeSignal,
        balance: float
    ) -> TradeSignal:
        """Gestiona riesgo con ATR"""
        last_bar = data.iloc[-1]
        current_price = signal.price
        
        # Calcular ATR si no existe
        if 'atr' not in last_bar or pd.isna(last_bar['atr']):
            atr_series = self.calculate_atr(data, self.parameters['atr_period'])
            atr = atr_series.iloc[-1]
        else:
            atr = last_bar['atr']
        
        sl_mult = self.parameters['atr_sl_multiplier']
        tp_mult = self.parameters['atr_tp_multiplier']
        
        if signal.signal_type == SignalType.BUY:
            signal.stop_loss = current_price - (atr * sl_mult)
            signal.take_profit = current_price + (atr * tp_mult)
        else:
            signal.stop_loss = current_price + (atr * sl_mult)
            signal.take_profit = current_price - (atr * tp_mult)
        
        # Calcular volumen
        signal.volume = self.calculate_position_size(
            balance=balance,
            risk_percent=self.parameters['risk_percent'],
            entry_price=current_price,
            stop_loss=signal.stop_loss,
            point_value=1.0
        )
        
        # Get RSI value safely
        rsi_value = last_bar.get('rsi', 50.0)
        signal.comment = f"{self.name} | RSI: {rsi_value:.1f}"
        
        return signal


class BollingerBreakout(TradingStrategy):
    """
    Estrategia de ruptura de Bandas de Bollinger
    
    Señales:
    - BUY: Precio rompe banda superior
    - SELL: Precio rompe banda inferior
    """
    
    def __init__(
        self,
        bb_period: int = 20,
        bb_std: float = 2.0,
        atr_period: int = 14,
        risk_percent: float = 0.015
    ):
        """Inicializa estrategia Bollinger Breakout"""
        parameters = {
            'bb_period': bb_period,
            'bb_std': bb_std,
            'atr_period': atr_period,
            'risk_percent': risk_percent
        }
        
        super().__init__(name="Bollinger Breakout", parameters=parameters)
    
    def calculate_indicators(self, data: pd.DataFrame) -> pd.DataFrame:
        """Calcula Bandas de Bollinger y ATR"""
        df = data.copy()
        
        # Bandas de Bollinger
        upper, middle, lower = self.calculate_bollinger_bands(
            df['close'],
            self.parameters['bb_period'],
            self.parameters['bb_std']
        )
        
        df['bb_upper'] = upper
        df['bb_middle'] = middle
        df['bb_lower'] = lower
        
        # ATR
        df['atr'] = self.calculate_atr(df, self.parameters['atr_period'])
        
        # Precio anterior
        df['close_prev'] = df['close'].shift(1)
        
        return df
    
    def generate_signals(self, data: pd.DataFrame) -> pd.Series:
        """Genera señales de breakout"""
        signals = pd.Series(0, index=data.index)
        
        # Compra: Precio rompe banda superior
        buy_condition = (
            (data['close_prev'] <= data['bb_upper']) &
            (data['close'] > data['bb_upper'])
        )
        
        # Venta: Precio rompe banda inferior
        sell_condition = (
            (data['close_prev'] >= data['bb_lower']) &
            (data['close'] < data['bb_lower'])
        )
        
        signals[buy_condition] = 1
        signals[sell_condition] = -1
        
        return signals
    
    def manage_risk(
        self,
        data: pd.DataFrame,
        signal: TradeSignal,
        balance: float
    ) -> TradeSignal:
        """Gestiona riesgo"""
        last_bar = data.iloc[-1]
        current_price = signal.price
        
        # Calcular ATR si no existe
        if 'atr' not in last_bar or pd.isna(last_bar['atr']):
            atr_series = self.calculate_atr(data, self.parameters['atr_period'])
            atr = atr_series.iloc[-1]
        else:
            atr = last_bar['atr']
        
        if signal.signal_type == SignalType.BUY:
            # SL en la banda media
            signal.stop_loss = last_bar.get('bb_middle', current_price * 0.99)
            signal.take_profit = current_price + (atr * 3)
        else:
            signal.stop_loss = last_bar.get('bb_middle', current_price * 1.01)
            signal.take_profit = current_price - (atr * 3)
        
        signal.volume = self.calculate_position_size(
            balance=balance,
            risk_percent=self.parameters['risk_percent'],
            entry_price=current_price,
            stop_loss=signal.stop_loss,
            point_value=1.0
        )
        
        return signal
