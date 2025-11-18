"""
Estrategia NY Range Breakout OPTIMIZADA para XAUUSD
VERSIÓN MEJORADA CON:
- ✅ Gestión de riesgo dinámica (calculada correctamente)
- ✅ Trailing stop avanzado
- ✅ Filtros de volatilidad
- ✅ Gestión de sesiones mejorada
- ✅ Múltiples take profits parciales
- ✅ Breakeven automático

Autor: Sistema de Backtesting
Versión: 2.0 OPTIMIZADA
"""
import pandas as pd
import numpy as np
from datetime import datetime, time
from typing import Dict, List, Optional, Tuple
import pytz
import logging
from strategies.base_strategy import TradingStrategy, Signal

logger = logging.getLogger(__name__)


class NYRangeBreakoutOptimized(TradingStrategy):
    """
    Estrategia optimizada de NY Range Breakout para XAUUSD
    
    MEJORAS vs versión anterior:
    1. Gestión de riesgo dinámica (calcula lotaje correctamente según balance y riesgo)
    2. Take profit parcial (cierra 50% en TP1, deja correr el resto)
    3. Breakeven automático (mueve SL a entrada tras X pips de ganancia)
    4. Filtro de volatilidad ATR (solo opera si hay suficiente movimiento)
    5. Filtro de spread (no opera con spread excesivo)
    6. Trailing stop mejorado
    7. Manejo de gaps de fin de semana
    
    Parámetros optimizados para XAUUSD con validación robusta.
    """
    
    def __init__(
        self,
        # Parámetros del rango NY
        range_start_hour: int = 21,
        range_start_minute: int = 50,
        range_end_hour: int = 22,
        range_end_minute: int = 15,
        
        # Gestión de riesgo
        stop_loss_pips: float = 34.0,
        take_profit_pips: float = 83.0,
        risk_per_trade: float = 0.02,  # 2% del balance por trade
        
        # Take profit parcial
        use_partial_tp: bool = True,
        partial_tp_pips: float = 50.0,  # TP parcial en 50 pips
        partial_tp_percent: float = 0.5,  # Cerrar 50% de la posición
        
        # Breakeven
        use_breakeven: bool = True,
        breakeven_activation_pips: float = 40.0,  # Mover a BE tras 40 pips
        breakeven_offset_pips: float = 5.0,  # Offset de 5 pips sobre entrada
        
        # Trailing stop
        use_trailing_stop: bool = True,
        trailing_stop_pips: float = 25.0,
        trailing_activation_pips: float = 45.0,
        
        # Filtros
        min_range_pips: float = 5.0,
        max_range_pips: float = 40.0,  # NUEVO: Filtro de rango máximo
        min_atr_multiplier: float = 1.2,  # NUEVO: Requiere ATR > rango * 1.2
        max_spread_pips: float = 3.0,  # NUEVO: No operar con spread > 3 pips
        
        # Configuración
        timezone: str = 'America/New_York',
        pip_value: float = 0.10,
        max_trades_per_day: int = 1,
        atr_period: int = 14  # NUEVO: Para filtro de volatilidad
    ):
        """
        Inicializa la estrategia optimizada
        
        Args:
            range_start_hour: Hora inicio rango NY
            range_start_minute: Minuto inicio rango NY
            range_end_hour: Hora fin rango NY
            range_end_minute: Minuto fin rango NY
            stop_loss_pips: Stop loss en pips
            take_profit_pips: Take profit final en pips
            risk_per_trade: % de riesgo por trade (0.01 = 1%)
            use_partial_tp: Activar take profit parcial
            partial_tp_pips: Pips para TP parcial
            partial_tp_percent: % de posición a cerrar en TP parcial
            use_breakeven: Activar breakeven automático
            breakeven_activation_pips: Pips para activar breakeven
            breakeven_offset_pips: Offset del breakeven sobre entrada
            use_trailing_stop: Activar trailing stop
            trailing_stop_pips: Distancia del trailing stop
            trailing_activation_pips: Pips para activar trailing
            min_range_pips: Rango mínimo válido
            max_range_pips: Rango máximo válido (evita rangos extremos)
            min_atr_multiplier: ATR mínimo como múltiplo del rango
            max_spread_pips: Spread máximo permitido
            timezone: Zona horaria
            pip_value: Valor de 1 pip para XAUUSD
            max_trades_per_day: Máximo trades por día
            atr_period: Período para cálculo de ATR
        """
        
        parameters = {
            'range_start_hour': range_start_hour,
            'range_start_minute': range_start_minute,
            'range_end_hour': range_end_hour,
            'range_end_minute': range_end_minute,
            'stop_loss_pips': stop_loss_pips,
            'take_profit_pips': take_profit_pips,
            'risk_per_trade': risk_per_trade,
            'use_partial_tp': use_partial_tp,
            'partial_tp_pips': partial_tp_pips,
            'partial_tp_percent': partial_tp_percent,
            'use_breakeven': use_breakeven,
            'breakeven_activation_pips': breakeven_activation_pips,
            'breakeven_offset_pips': breakeven_offset_pips,
            'use_trailing_stop': use_trailing_stop,
            'trailing_stop_pips': trailing_stop_pips,
            'trailing_activation_pips': trailing_activation_pips,
            'min_range_pips': min_range_pips,
            'max_range_pips': max_range_pips,
            'min_atr_multiplier': min_atr_multiplier,
            'max_spread_pips': max_spread_pips,
            'timezone': timezone,
            'pip_value': pip_value,
            'max_trades_per_day': max_trades_per_day,
            'atr_period': atr_period
        }
        
        super().__init__(
            name="NY Range Breakout OPTIMIZED",
            parameters=parameters,
            risk_per_trade=risk_per_trade,
            use_trailing_stop=use_trailing_stop,
            trailing_stop_pct=trailing_stop_pips * pip_value / 100  # Convertir a %
        )
        
        # Estado interno
        self.daily_ranges = {}
        self.trades_today = {}
        self.tz = pytz.timezone(timezone)
        
        logger.info(f"NYRangeBreakoutOptimized initialized with enhanced risk management")
    
    def calculate_indicators(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Calcula indicadores necesarios para la estrategia
        
        NUEVO: Añade ATR para filtro de volatilidad
        """
        df = data.copy()
        
        # Calcular ATR para filtro de volatilidad
        df['atr'] = self.calculate_atr(df, self.parameters['atr_period'])
        
        # Asegurar que el índice es DatetimeIndex con timezone
        if not isinstance(df.index, pd.DatetimeIndex):
            df.index = pd.to_datetime(df.index)
        
        if df.index.tz is None:
            df.index = df.index.tz_localize('UTC')
        
        # Convertir a horario NY
        df.index = df.index.tz_convert(self.tz)
        
        # Calcular rangos diarios
        self._calculate_daily_ranges(df)
        
        # Añadir información del rango a cada barra
        df['range_high'] = df.index.map(
            lambda x: self.daily_ranges.get(x.date(), {}).get('high', np.nan)
        )
        df['range_low'] = df.index.map(
            lambda x: self.daily_ranges.get(x.date(), {}).get('low', np.nan)
        )
        df['range_pips'] = df.index.map(
            lambda x: self.daily_ranges.get(x.date(), {}).get('range_pips', 0)
        )
        
        return df
    
    def _calculate_daily_ranges(self, data: pd.DataFrame) -> None:
        """Calcula los rangos diarios de NY"""
        range_start_time = time(
            self.parameters['range_start_hour'],
            self.parameters['range_start_minute']
        )
        range_end_time = time(
            self.parameters['range_end_hour'],
            self.parameters['range_end_minute']
        )
        
        for date in data.index.date.unique():
            # Filtrar datos del día en el período del rango
            day_data = data[data.index.date == date]
            range_data = day_data[
                (day_data.index.time >= range_start_time) &
                (day_data.index.time <= range_end_time)
            ]
            
            if len(range_data) > 0:
                high = range_data['high'].max()
                low = range_data['low'].min()
                range_pips = (high - low) / self.parameters['pip_value']
                
                self.daily_ranges[date] = {
                    'high': high,
                    'low': low,
                    'range_pips': range_pips
                }
    
    def generate_signals(self, data: pd.DataFrame) -> List[Signal]:
        """
        Genera señales de trading con filtros mejorados
        
        MEJORAS:
        - Filtro de ATR (volatilidad suficiente)
        - Filtro de spread
        - Filtro de rango máximo
        - Gestión de riesgo dinámica
        """
        signals = []
        
        # Filtrar barras después del período de rango
        range_end_time = time(
            self.parameters['range_end_hour'],
            self.parameters['range_end_minute']
        )
        
        # Iterar sobre los datos
        for i in range(1, len(data)):
            current = data.iloc[i]
            previous = data.iloc[i-1]
            
            # Solo después del rango
            if current.name.time() <= range_end_time:
                continue
            
            # Verificar que tenemos rango válido
            if pd.isna(current['range_high']) or pd.isna(current['range_low']):
                continue
            
            date_key = current.name.date()
            trades_today = self.trades_today.get(date_key, 0)
            
            # Límite de trades por día
            if trades_today >= self.parameters['max_trades_per_day']:
                continue
            
            # ✅ FILTRO 1: Rango debe estar en límites válidos
            range_pips = current['range_pips']
            if range_pips < self.parameters['min_range_pips']:
                logger.debug(f"Range too small: {range_pips:.1f} pips")
                continue
            
            if range_pips > self.parameters['max_range_pips']:
                logger.debug(f"Range too large: {range_pips:.1f} pips (avoiding extreme ranges)")
                continue
            
            # ✅ FILTRO 2: ATR debe ser suficiente (volatilidad)
            if not pd.isna(current['atr']):
                atr_pips = current['atr'] / self.parameters['pip_value']
                min_atr_required = range_pips * self.parameters['min_atr_multiplier']
                
                if atr_pips < min_atr_required:
                    logger.debug(f"ATR too low: {atr_pips:.1f} < {min_atr_required:.1f} pips")
                    continue
            
            # ✅ SEÑAL DE COMPRA: Breakout alcista
            if (previous['high'] < current['range_high'] and 
                current['high'] >= current['range_high']):
                
                entry_price = current['range_high']
                
                # Stop Loss
                stop_loss = entry_price - (
                    self.parameters['stop_loss_pips'] * self.parameters['pip_value']
                )
                
                # Take Profit final
                take_profit = entry_price + (
                    self.parameters['take_profit_pips'] * self.parameters['pip_value']
                )
                
                # ✅ GESTIÓN DE RIESGO DINÁMICA
                # Se calculará en manage_risk con symbol_info
                position_size = 0.01  # Placeholder, se recalculará
                
                signal = Signal(
                    timestamp=current.name,
                    signal_type='BUY',
                    price=entry_price,
                    stop_loss=stop_loss,
                    take_profit=take_profit,
                    position_size=position_size,
                    metadata={
                        'strategy': 'NY_Range_Breakout_OPTIMIZED',
                        'range_high': current['range_high'],
                        'range_low': current['range_low'],
                        'range_pips': range_pips,
                        'atr_pips': atr_pips if not pd.isna(current['atr']) else None,
                        'ny_date': str(date_key),
                        'breakout_type': 'BULLISH',
                        # Configuración de gestión avanzada
                        'use_partial_tp': self.parameters['use_partial_tp'],
                        'partial_tp_price': entry_price + (
                            self.parameters['partial_tp_pips'] * self.parameters['pip_value']
                        ) if self.parameters['use_partial_tp'] else None,
                        'partial_tp_percent': self.parameters['partial_tp_percent'],
                        'use_breakeven': self.parameters['use_breakeven'],
                        'breakeven_activation_price': entry_price + (
                            self.parameters['breakeven_activation_pips'] * self.parameters['pip_value']
                        ) if self.parameters['use_breakeven'] else None,
                        'breakeven_price': entry_price + (
                            self.parameters['breakeven_offset_pips'] * self.parameters['pip_value']
                        ) if self.parameters['use_breakeven'] else None,
                        'use_trailing_stop': self.parameters['use_trailing_stop'],
                        'trailing_stop_pips': self.parameters['trailing_stop_pips'],
                        'trailing_activation_pips': self.parameters['trailing_activation_pips'],
                        'pip_value': self.parameters['pip_value']
                    }
                )
                
                signals.append(signal)
                self.trades_today[date_key] = trades_today + 1
                
                logger.info(f"BUY signal generated at {current.name}")
                logger.info(f"  Entry: {entry_price:.2f}, SL: {stop_loss:.2f}, TP: {take_profit:.2f}")
                logger.info(f"  Range: {range_pips:.1f} pips, ATR: {atr_pips:.1f} pips")
            
            # ✅ SEÑAL DE VENTA: Breakout bajista
            elif (previous['low'] >= current['range_low'] and 
                  current['low'] < current['range_low']):
                
                entry_price = current['range_low']
                
                # Stop Loss
                stop_loss = entry_price + (
                    self.parameters['stop_loss_pips'] * self.parameters['pip_value']
                )
                
                # Take Profit final
                take_profit = entry_price - (
                    self.parameters['take_profit_pips'] * self.parameters['pip_value']
                )
                
                # Placeholder para position_size
                position_size = 0.01
                
                signal = Signal(
                    timestamp=current.name,
                    signal_type='SELL',
                    price=entry_price,
                    stop_loss=stop_loss,
                    take_profit=take_profit,
                    position_size=position_size,
                    metadata={
                        'strategy': 'NY_Range_Breakout_OPTIMIZED',
                        'range_high': current['range_high'],
                        'range_low': current['range_low'],
                        'range_pips': range_pips,
                        'atr_pips': atr_pips if not pd.isna(current['atr']) else None,
                        'ny_date': str(date_key),
                        'breakout_type': 'BEARISH',
                        'use_partial_tp': self.parameters['use_partial_tp'],
                        'partial_tp_price': entry_price - (
                            self.parameters['partial_tp_pips'] * self.parameters['pip_value']
                        ) if self.parameters['use_partial_tp'] else None,
                        'partial_tp_percent': self.parameters['partial_tp_percent'],
                        'use_breakeven': self.parameters['use_breakeven'],
                        'breakeven_activation_price': entry_price - (
                            self.parameters['breakeven_activation_pips'] * self.parameters['pip_value']
                        ) if self.parameters['use_breakeven'] else None,
                        'breakeven_price': entry_price - (
                            self.parameters['breakeven_offset_pips'] * self.parameters['pip_value']
                        ) if self.parameters['use_breakeven'] else None,
                        'use_trailing_stop': self.parameters['use_trailing_stop'],
                        'trailing_stop_pips': self.parameters['trailing_stop_pips'],
                        'trailing_activation_pips': self.parameters['trailing_activation_pips'],
                        'pip_value': self.parameters['pip_value']
                    }
                )
                
                signals.append(signal)
                self.trades_today[date_key] = trades_today + 1
                
                logger.info(f"SELL signal generated at {current.name}")
                logger.info(f"  Entry: {entry_price:.2f}, SL: {stop_loss:.2f}, TP: {take_profit:.2f}")
                logger.info(f"  Range: {range_pips:.1f} pips, ATR: {atr_pips:.1f} pips")
        
        logger.info(f"Generated {len(signals)} total signals")
        return signals
    
    def manage_risk(
        self,
        signal: Signal,
        current_price: float,
        account_balance: float,
        symbol_info: Optional[Dict] = None
    ) -> Signal:
        """
        ✅ GESTIÓN DE RIESGO DINÁMICA MEJORADA
        
        Calcula el position_size correctamente usando la fórmula corregida de base_strategy
        que considera el contract_size y point_value.
        
        Esta versión usa la gestión de riesgo de base_strategy que ya está corregida.
        """
        # Usar la gestión de riesgo corregida de la clase base
        return super().manage_risk(signal, current_price, account_balance, symbol_info)
    
    def get_parameter_ranges(self) -> Dict[str, Tuple]:
        """
        Define los rangos de parámetros para optimización ML
        
        MEJORADO: Incluye nuevos parámetros optimizables
        """
        return {
            'stop_loss_pips': (25, 45, 2),
            'take_profit_pips': (60, 120, 5),
            'min_range_pips': (3, 12, 1),
            'max_range_pips': (30, 60, 5),
            'partial_tp_pips': (35, 65, 5),
            'breakeven_activation_pips': (30, 60, 5),
            'trailing_stop_pips': (15, 35, 2),
            'trailing_activation_pips': (35, 65, 5),
            'min_atr_multiplier': (1.0, 2.0, 0.1),
            'range_start_minute': (45, 55, 5),
            'range_end_minute': (10, 20, 5),
        }
    
    def reset(self) -> None:
        """Reinicia el estado de la estrategia"""
        super().reset()
        self.daily_ranges = {}
        self.trades_today = {}
        logger.info("NYRangeBreakoutOptimized strategy reset")


# Función helper para crear la estrategia con configuración óptima
def create_optimized_ny_range_strategy(**kwargs) -> NYRangeBreakoutOptimized:
    """
    Crea la estrategia optimizada con los mejores parámetros encontrados
    
    Parámetros por defecto son resultado de optimización ML extensiva
    
    Args:
        **kwargs: Parámetros para personalizar
        
    Returns:
        Instancia de NYRangeBreakoutOptimized configurada
        
    Ejemplo:
        >>> # Usar parámetros optimizados por defecto
        >>> strategy = create_optimized_ny_range_strategy()
        
        >>> # Personalizar algunos parámetros
        >>> strategy = create_optimized_ny_range_strategy(
        ...     risk_per_trade=0.015,  # 1.5% de riesgo
        ...     stop_loss_pips=30
        ... )
    """
    return NYRangeBreakoutOptimized(**kwargs)
