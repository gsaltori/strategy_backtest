"""
Estrategia: NY Range Breakout para XAUUSD

Descripción:
- Calcula el máximo y mínimo del XAUUSD en el rango de 21:50 a 22:15 hora NY
- Considera automáticamente el cambio de horario (verano/invierno)
- Si el precio rompe el máximo del rango: abre COMPRA
- Si el precio rompe el mínimo del rango: abre VENTA
- SL fijo: 34 pips (3.40 USD para XAUUSD)
- TP fijo: 83 pips (8.30 USD para XAUUSD)

Autor: Sistema de Backtesting
Fecha: 2024
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional
from datetime import datetime, time, timedelta
import pytz
from strategies.base_strategy import TradingStrategy, Signal
import logging

logger = logging.getLogger(__name__)


class NYRangeBreakout(TradingStrategy):
    """
    Estrategia de Breakout del Rango de Nueva York para XAUUSD
    
    Lógica:
    1. Identifica el rango de NY (21:50-22:15 hora NY)
    2. Calcula máximo y mínimo del rango
    3. Espera breakout después de 22:15
    4. Abre posición en dirección del breakout
    5. SL: 34 pips, TP: 83 pips
    
    Parámetros:
    - range_start_hour: Hora de inicio del rango (default: 21)
    - range_start_minute: Minuto de inicio del rango (default: 50)
    - range_end_hour: Hora de fin del rango (default: 22)
    - range_end_minute: Minuto de fin del rango (default: 15)
    - stop_loss_pips: Stop loss en pips (default: 34)
    - take_profit_pips: Take profit en pips (default: 83)
    - timezone: Zona horaria de referencia (default: 'America/New_York')
    """
    
    def __init__(
        self,
        range_start_hour: int = 21,
        range_start_minute: int = 50,
        range_end_hour: int = 22,
        range_end_minute: int = 15,
        stop_loss_pips: float = 34.0,
        take_profit_pips: float = 83.0,
        timezone: str = 'America/New_York',
        pip_value: float = 0.10,  # Para XAUUSD, 1 pip = 0.10
        min_range_pips: float = 5.0,  # Rango mínimo para validez
        max_trades_per_day: int = 1,  # Máximo 1 trade por día
        **kwargs
    ):
        """
        Inicializa la estrategia NY Range Breakout
        
        Args:
            range_start_hour: Hora de inicio del rango NY (21)
            range_start_minute: Minuto de inicio (50)
            range_end_hour: Hora de fin del rango (22)
            range_end_minute: Minuto de fin (15)
            stop_loss_pips: Stop loss en pips (34)
            take_profit_pips: Take profit en pips (83)
            timezone: Zona horaria ('America/New_York')
            pip_value: Valor de 1 pip para el símbolo (0.10 para XAUUSD)
            min_range_pips: Rango mínimo en pips para ser válido
            max_trades_per_day: Máximo de trades por día
        """
        parameters = {
            'range_start_hour': range_start_hour,
            'range_start_minute': range_start_minute,
            'range_end_hour': range_end_hour,
            'range_end_minute': range_end_minute,
            'stop_loss_pips': stop_loss_pips,
            'take_profit_pips': take_profit_pips,
            'timezone': timezone,
            'pip_value': pip_value,
            'min_range_pips': min_range_pips,
            'max_trades_per_day': max_trades_per_day,
        }
        
        super().__init__(
            name='NY_Range_Breakout_XAUUSD',
            parameters=parameters,
            **kwargs
        )
        
        # Zona horaria
        self.tz = pytz.timezone(timezone)
        
        # Estado interno
        self.daily_ranges = {}  # {date: {'high': float, 'low': float, 'range_pips': float}}
        self.trades_today = {}  # {date: int} - contador de trades por día
        
        logger.info(f"NYRangeBreakout initialized: Range {range_start_hour}:{range_start_minute:02d} - {range_end_hour}:{range_end_minute:02d} NY")
        logger.info(f"SL: {stop_loss_pips} pips, TP: {take_profit_pips} pips")
    
    def _get_ny_time(self, timestamp: pd.Timestamp) -> datetime:
        """
        Convierte timestamp UTC a hora de Nueva York
        Maneja automáticamente DST (horario de verano)
        
        Args:
            timestamp: Timestamp en UTC o timezone-naive
            
        Returns:
            Datetime en timezone de NY
        """
        # Si el timestamp no tiene timezone, asumimos UTC
        if timestamp.tz is None:
            timestamp = timestamp.tz_localize('UTC')
        
        # Convertir a NY timezone
        ny_time = timestamp.tz_convert(self.tz)
        return ny_time
    
    def _is_in_range_period(self, ny_time: datetime) -> bool:
        """
        Verifica si un timestamp está dentro del período de rango
        
        Args:
            ny_time: Datetime en timezone NY
            
        Returns:
            True si está en el período de rango
        """
        start_time = time(
            self.parameters['range_start_hour'],
            self.parameters['range_start_minute']
        )
        end_time = time(
            self.parameters['range_end_hour'],
            self.parameters['range_end_minute']
        )
        
        current_time = ny_time.time()
        
        return start_time <= current_time <= end_time
    
    def _is_after_range_period(self, ny_time: datetime) -> bool:
        """
        Verifica si un timestamp está después del período de rango
        
        Args:
            ny_time: Datetime en timezone NY
            
        Returns:
            True si está después del rango
        """
        end_time = time(
            self.parameters['range_end_hour'],
            self.parameters['range_end_minute']
        )
        
        return ny_time.time() > end_time
    
    def calculate_indicators(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Calcula los rangos de NY para cada día
        
        Args:
            data: DataFrame con datos OHLC
            
        Returns:
            DataFrame con indicadores agregados
        """
        df = data.copy()
        
        # Inicializar columnas
        df['ny_time'] = None
        df['in_range'] = False
        df['range_high'] = np.nan
        df['range_low'] = np.nan
        df['range_pips'] = np.nan
        df['after_range'] = False
        
        logger.info(f"Processing {len(df)} bars for NY range calculation")
        logger.info(f"Data period: {df.index[0]} to {df.index[-1]}")
        
        # Contador de barras en rango
        bars_in_range = 0
        
        # Procesar cada barra
        for idx in df.index:
            # Convertir a hora NY
            ny_time = self._get_ny_time(idx)
            df.at[idx, 'ny_time'] = ny_time
            
            # Verificar si está en período de rango
            in_range = self._is_in_range_period(ny_time)
            df.at[idx, 'in_range'] = in_range
            
            if in_range:
                bars_in_range += 1
            
            # Verificar si está después del rango
            after_range = self._is_after_range_period(ny_time)
            df.at[idx, 'after_range'] = after_range
            
            # Calcular rango del día
            date_key = ny_time.date()
            
            if in_range:
                # Actualizar rango del día
                if date_key not in self.daily_ranges:
                    self.daily_ranges[date_key] = {
                        'high': df.at[idx, 'high'],
                        'low': df.at[idx, 'low']
                    }
                    logger.debug(f"New range started for {date_key}: {df.at[idx, 'low']:.2f} - {df.at[idx, 'high']:.2f}")
                else:
                    self.daily_ranges[date_key]['high'] = max(
                        self.daily_ranges[date_key]['high'],
                        df.at[idx, 'high']
                    )
                    self.daily_ranges[date_key]['low'] = min(
                        self.daily_ranges[date_key]['low'],
                        df.at[idx, 'low']
                    )
            
            # Agregar rango al DataFrame
            if date_key in self.daily_ranges:
                df.at[idx, 'range_high'] = self.daily_ranges[date_key]['high']
                df.at[idx, 'range_low'] = self.daily_ranges[date_key]['low']
                
                # Calcular tamaño del rango en pips
                range_pips = (
                    self.daily_ranges[date_key]['high'] - 
                    self.daily_ranges[date_key]['low']
                ) / self.parameters['pip_value']
                df.at[idx, 'range_pips'] = range_pips
                self.daily_ranges[date_key]['range_pips'] = range_pips
        
        # Rellenar valores hacia adelante para usar el rango del día
        df['range_high'] = df['range_high'].fillna(method='ffill')
        df['range_low'] = df['range_low'].fillna(method='ffill')
        df['range_pips'] = df['range_pips'].fillna(method='ffill')
        
        logger.info(f"Calculated {len(self.daily_ranges)} NY ranges")
        logger.info(f"Bars in range period: {bars_in_range}")
        
        if len(self.daily_ranges) > 0:
            # Mostrar algunos ejemplos
            sample_dates = list(self.daily_ranges.keys())[:3]
            logger.info("Sample ranges:")
            for date in sample_dates:
                r = self.daily_ranges[date]
                logger.info(f"  {date}: {r['low']:.2f} - {r['high']:.2f} ({r.get('range_pips', 0):.1f} pips)")
        else:
            logger.warning("⚠️ No ranges found! Check if data contains NY time period")
            logger.warning(f"   Looking for: {self.parameters['range_start_hour']}:{self.parameters['range_start_minute']:02d} - {self.parameters['range_end_hour']}:{self.parameters['range_end_minute']:02d} NY time")
        
        return df
    
    def generate_signals(self, data: pd.DataFrame) -> List[Signal]:
        """
        Genera señales de trading basadas en breakouts del rango NY
        
        Args:
            data: DataFrame con indicadores
            
        Returns:
            Lista de señales generadas
        """
        signals = []
        
        # Necesitamos al menos 2 barras
        for i in range(1, len(data)):
            current = data.iloc[i]
            previous = data.iloc[i-1]
            
            # Verificar que tenemos un rango válido
            if pd.isna(current['range_high']) or pd.isna(current['range_low']):
                continue
            
            # Solo operar después del período de rango
            if not current['after_range']:
                continue
            
            # Verificar que el rango es suficientemente grande
            if current['range_pips'] < self.parameters['min_range_pips']:
                continue
            
            # Obtener fecha del día
            ny_time = current['ny_time']
            date_key = ny_time.date()
            
            # Verificar límite de trades por día
            trades_today = self.trades_today.get(date_key, 0)
            if trades_today >= self.parameters['max_trades_per_day']:
                continue
            
            # SEÑAL DE COMPRA: Breakout alcista
            # El precio rompe por encima del máximo del rango
            if (previous['high'] <= current['range_high'] and 
                current['high'] > current['range_high']):
                
                # Precio de entrada (breakout)
                entry_price = current['range_high']
                
                # Stop Loss: 34 pips abajo
                stop_loss = entry_price - (self.parameters['stop_loss_pips'] * self.parameters['pip_value'])
                
                # Take Profit: 83 pips arriba
                take_profit = entry_price + (self.parameters['take_profit_pips'] * self.parameters['pip_value'])
                
                # Calcular tamaño de posición con gestión de riesgo adecuada
                # Para XAUUSD: usar 0.01 lotes (1 micro lote) como tamaño fijo por defecto
                position_size = 0.01
                
                signal = Signal(
                    timestamp=current.name,
                    signal_type='BUY',
                    price=entry_price,
                    stop_loss=stop_loss,
                    take_profit=take_profit,
                    position_size=position_size,  # Tamaño fijo
                    metadata={
                        'strategy': 'NY_Range_Breakout',
                        'range_high': current['range_high'],
                        'range_low': current['range_low'],
                        'range_pips': current['range_pips'],
                        'ny_date': str(date_key),
                        'breakout_type': 'BULLISH'
                    }
                )
                
                signals.append(signal)
                
                # Actualizar contador de trades
                self.trades_today[date_key] = trades_today + 1
                
                logger.info(f"BUY signal generated at {current.name}")
                logger.info(f"  Entry: {entry_price:.2f}, SL: {stop_loss:.2f}, TP: {take_profit:.2f}")
                logger.info(f"  Range: {current['range_low']:.2f} - {current['range_high']:.2f} ({current['range_pips']:.1f} pips)")
            
            # SEÑAL DE VENTA: Breakout bajista
            # El precio rompe por debajo del mínimo del rango
            elif (previous['low'] >= current['range_low'] and 
                  current['low'] < current['range_low']):
                
                # Precio de entrada (breakout)
                entry_price = current['range_low']
                
                # Stop Loss: 34 pips arriba
                stop_loss = entry_price + (self.parameters['stop_loss_pips'] * self.parameters['pip_value'])
                
                # Take Profit: 83 pips abajo
                take_profit = entry_price - (self.parameters['take_profit_pips'] * self.parameters['pip_value'])
                
                # Calcular tamaño de posición con gestión de riesgo adecuada
                # Para XAUUSD: usar 0.01 lotes (1 micro lote) como tamaño fijo por defecto
                position_size = 0.01
                
                signal = Signal(
                    timestamp=current.name,
                    signal_type='SELL',
                    price=entry_price,
                    stop_loss=stop_loss,
                    take_profit=take_profit,
                    position_size=position_size,  # Tamaño fijo
                    metadata={
                        'strategy': 'NY_Range_Breakout',
                        'range_high': current['range_high'],
                        'range_low': current['range_low'],
                        'range_pips': current['range_pips'],
                        'ny_date': str(date_key),
                        'breakout_type': 'BEARISH'
                    }
                )
                
                signals.append(signal)
                
                # Actualizar contador de trades
                self.trades_today[date_key] = trades_today + 1
                
                logger.info(f"SELL signal generated at {current.name}")
                logger.info(f"  Entry: {entry_price:.2f}, SL: {stop_loss:.2f}, TP: {take_profit:.2f}")
                logger.info(f"  Range: {current['range_low']:.2f} - {current['range_high']:.2f} ({current['range_pips']:.1f} pips)")
        
        logger.info(f"Generated {len(signals)} total signals")
        return signals
    
    def get_parameter_ranges(self) -> Dict[str, Tuple]:
        """
        Define los rangos de parámetros para optimización ML
        
        Returns:
            Diccionario con rangos {param_name: (min, max, step)}
        """
        return {
            'stop_loss_pips': (20, 50, 2),
            'take_profit_pips': (50, 150, 5),
            'min_range_pips': (3, 15, 1),
            'range_start_minute': (45, 55, 5),  # Variar inicio del rango
            'range_end_minute': (10, 20, 5),    # Variar fin del rango
        }
    
    def manage_risk(
        self,
        signal: Signal,
        current_price: float,
        account_balance: float
    ) -> Signal:
        """
        Sobrescribe manage_risk para mantener el position_size fijo
        
        La estrategia ya define SL, TP y position_size en generate_signals,
        así que solo retornamos la señal sin modificar
        
        Args:
            signal: Señal original
            current_price: Precio actual (no usado)
            account_balance: Balance de cuenta (no usado)
            
        Returns:
            Señal sin modificaciones
        """
        # NO recalcular position_size - ya está definido correctamente
        # La señal ya tiene SL, TP y position_size configurados
        return signal
    
    def reset(self) -> None:
        """Reinicia el estado de la estrategia"""
        super().reset()
        self.daily_ranges = {}
        self.trades_today = {}
        logger.info("NYRangeBreakout strategy reset")


# Función helper para crear la estrategia con parámetros por defecto
def create_ny_range_breakout_strategy(**kwargs) -> NYRangeBreakout:
    """
    Crea una instancia de la estrategia con parámetros personalizados
    
    Args:
        **kwargs: Parámetros para personalizar la estrategia
        
    Returns:
        Instancia de NYRangeBreakout configurada
        
    Ejemplo:
        >>> strategy = create_ny_range_breakout_strategy(
        ...     stop_loss_pips=30,
        ...     take_profit_pips=90
        ... )
    """
    return NYRangeBreakout(**kwargs)
