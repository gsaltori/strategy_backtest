"""
Estrategia de ejemplo: Cruce de Medias Móviles con RSI
"""
import pandas as pd
import numpy as np
from typing import Dict, List, Tuple
from strategies.base_strategy import TradingStrategy, Signal


class MovingAverageCrossover(TradingStrategy):
    """
    Estrategia de cruce de medias móviles con filtro RSI
    
    Señales:
    - BUY: Cuando MA rápida cruza por encima de MA lenta y RSI < 70
    - SELL: Cuando MA rápida cruza por debajo de MA lenta y RSI > 30
    
    Parámetros:
    - fast_period: Período de la media móvil rápida
    - slow_period: Período de la media móvil lenta
    - ma_type: Tipo de media móvil ('SMA' o 'EMA')
    - rsi_period: Período del RSI
    - rsi_overbought: Nivel de sobrecompra del RSI
    - rsi_oversold: Nivel de sobreventa del RSI
    """
    
    def __init__(
        self,
        fast_period: int = 10,
        slow_period: int = 30,
        ma_type: str = 'EMA',
        rsi_period: int = 14,
        rsi_overbought: float = 70,
        rsi_oversold: float = 30,
        atr_period: int = 14,
        atr_stop_multiplier: float = 2.0,
        risk_reward_ratio: float = 2.5,
        **kwargs
    ):
        """
        Inicializa la estrategia
        
        Args:
            fast_period: Período MA rápida
            slow_period: Período MA lenta
            ma_type: 'SMA' o 'EMA'
            rsi_period: Período RSI
            rsi_overbought: Nivel sobrecompra
            rsi_oversold: Nivel sobreventa
            atr_period: Período ATR
            atr_stop_multiplier: Multiplicador para stop loss
            risk_reward_ratio: Ratio riesgo/recompensa
        """
        parameters = {
            'fast_period': fast_period,
            'slow_period': slow_period,
            'ma_type': ma_type,
            'rsi_period': rsi_period,
            'rsi_overbought': rsi_overbought,
            'rsi_oversold': rsi_oversold,
            'atr_period': atr_period,
            'atr_stop_multiplier': atr_stop_multiplier,
            'risk_reward_ratio': risk_reward_ratio,
        }
        
        super().__init__(
            name='MA_Crossover_RSI',
            parameters=parameters,
            **kwargs
        )
    
    def calculate_indicators(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Calcula indicadores técnicos
        
        Args:
            data: DataFrame con OHLC
            
        Returns:
            DataFrame con indicadores
        """
        df = data.copy()
        
        # Medias móviles
        if self.parameters['ma_type'] == 'SMA':
            df['fast_ma'] = df['close'].rolling(window=self.parameters['fast_period']).mean()
            df['slow_ma'] = df['close'].rolling(window=self.parameters['slow_period']).mean()
        else:  # EMA
            df['fast_ma'] = df['close'].ewm(span=self.parameters['fast_period'], adjust=False).mean()
            df['slow_ma'] = df['close'].ewm(span=self.parameters['slow_period'], adjust=False).mean()
        
        # RSI
        df['rsi'] = self._calculate_rsi(df['close'], self.parameters['rsi_period'])
        
        # ATR para stop loss
        df['atr'] = self._calculate_atr(df, self.parameters['atr_period'])
        
        # Guardar indicadores en el estado
        self.indicators['fast_ma'] = df['fast_ma']
        self.indicators['slow_ma'] = df['slow_ma']
        self.indicators['RSI'] = df['rsi']
        self.indicators['ATR'] = df['atr']
        
        return df
    
    def generate_signals(self, data: pd.DataFrame) -> List[Signal]:
        """
        Genera señales de trading
        
        Args:
            data: DataFrame con indicadores
            
        Returns:
            Lista de señales
        """
        signals = []
        
        # Necesitamos al menos 2 barras para detectar cruces
        for i in range(1, len(data)):
            current = data.iloc[i]
            previous = data.iloc[i-1]
            
            # Verificar que los indicadores estén disponibles
            if pd.isna(current['fast_ma']) or pd.isna(current['slow_ma']) or pd.isna(current['rsi']):
                continue
            
            # Detectar cruce alcista (BUY)
            if (previous['fast_ma'] <= previous['slow_ma'] and 
                current['fast_ma'] > current['slow_ma'] and
                current['rsi'] < self.parameters['rsi_overbought']):
                
                # Calcular stop loss y take profit
                atr = current['atr'] if not pd.isna(current['atr']) else current['close'] * 0.02
                stop_loss = current['close'] - (atr * self.parameters['atr_stop_multiplier'])
                risk = current['close'] - stop_loss
                take_profit = current['close'] + (risk * self.parameters['risk_reward_ratio'])
                
                signal = Signal(
                    timestamp=current.name,
                    signal_type='BUY',
                    price=current['close'],
                    stop_loss=stop_loss,
                    take_profit=take_profit,
                    metadata={
                        'fast_ma': current['fast_ma'],
                        'slow_ma': current['slow_ma'],
                        'rsi': current['rsi'],
                        'atr': atr
                    }
                )
                signals.append(signal)
            
            # Detectar cruce bajista (SELL)
            elif (previous['fast_ma'] >= previous['slow_ma'] and 
                  current['fast_ma'] < current['slow_ma'] and
                  current['rsi'] > self.parameters['rsi_oversold']):
                
                # Calcular stop loss y take profit
                atr = current['atr'] if not pd.isna(current['atr']) else current['close'] * 0.02
                stop_loss = current['close'] + (atr * self.parameters['atr_stop_multiplier'])
                risk = stop_loss - current['close']
                take_profit = current['close'] - (risk * self.parameters['risk_reward_ratio'])
                
                signal = Signal(
                    timestamp=current.name,
                    signal_type='SELL',
                    price=current['close'],
                    stop_loss=stop_loss,
                    take_profit=take_profit,
                    metadata={
                        'fast_ma': current['fast_ma'],
                        'slow_ma': current['slow_ma'],
                        'rsi': current['rsi'],
                        'atr': atr
                    }
                )
                signals.append(signal)
        
        return signals
    
    def _calculate_rsi(self, prices: pd.Series, period: int = 14) -> pd.Series:
        """
        Calcula el RSI (Relative Strength Index)
        
        Args:
            prices: Serie de precios
            period: Período del RSI
            
        Returns:
            Serie con valores RSI
        """
        delta = prices.diff()
        
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        
        return rsi
    
    def _calculate_atr(self, data: pd.DataFrame, period: int = 14) -> pd.Series:
        """
        Calcula el ATR (Average True Range)
        
        Args:
            data: DataFrame con OHLC
            period: Período del ATR
            
        Returns:
            Serie con valores ATR
        """
        high = data['high']
        low = data['low']
        close = data['close']
        
        tr1 = high - low
        tr2 = abs(high - close.shift())
        tr3 = abs(low - close.shift())
        
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        atr = tr.rolling(window=period).mean()
        
        return atr
    
    def get_parameter_ranges(self) -> Dict[str, Tuple]:
        """
        Define rangos de parámetros para optimización
        
        Returns:
            Diccionario con rangos {param: (min, max, step)}
        """
        return {
            'fast_period': (5, 20, 1),
            'slow_period': (20, 50, 2),
            'rsi_period': (10, 20, 2),
            'rsi_overbought': (60, 80, 5),
            'rsi_oversold': (20, 40, 5),
            'atr_stop_multiplier': (1.5, 3.0, 0.25),
            'risk_reward_ratio': (1.5, 3.5, 0.25),
        }
