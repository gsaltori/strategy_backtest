"""
Estrategia de Patrón de Dos Velas Bajistas
Timeframe: H4
Tipo: Solo compras (LONG)

Patrón:
1. Primera vela: Bajista
2. Segunda vela: Bajista (consecutiva)
3. Tercera vela: Alcista con cuerpo superior al de la segunda vela bajista
4. Entrada: Cierre de la vela alcista
5. Stop Loss: Mínimo de la segunda vela bajista
6. Take Profit: Risk/Reward 1:2

Ejemplo:
    Vela 1: BAJISTA (close < open)
    Vela 2: BAJISTA (close < open) <- SL en el low de esta vela
    Vela 3: ALCISTA (close > open) <- Entrada en el close de esta vela
            Body(Vela3) > Body(Vela2)
"""

import pandas as pd
import numpy as np
from typing import List
import logging

# Intentar importar desde diferentes ubicaciones
try:
    from strategies.base_strategy import TradingStrategy, Signal
except ImportError:
    try:
        from base_strategy import TradingStrategy, Signal
    except ImportError:
        import sys
        import os
        # Añadir el directorio padre al path
        sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        from base_strategy import TradingStrategy, Signal

logger = logging.getLogger(__name__)


class TwoBearishPatternStrategy(TradingStrategy):
    """
    Estrategia basada en patrón de reversión alcista
    
    Condiciones de entrada (BUY):
    1. Primera vela bajista (close < open)
    2. Segunda vela bajista consecutiva (close < open)
    3. Tercera vela alcista (close > open) con cuerpo mayor a la segunda vela bajista
    
    Gestión de riesgo:
    - Entrada: Cierre de la vela alcista
    - Stop Loss: Mínimo de la segunda vela bajista
    - Take Profit: Risk/Reward ratio 1:2
    """
    
    def __init__(
        self,
        risk_reward_ratio: float = 2.0,
        risk_per_trade: float = 0.02,
        min_body_ratio: float = 1.0,  # Cuerpo alcista debe ser >= este ratio vs segunda bajista
        use_trailing_stop: bool = False,
        trailing_stop_pct: float = 0.02
    ):
        """
        Inicializa la estrategia
        
        Args:
            risk_reward_ratio: Ratio Risk/Reward (2.0 = 1:2)
            risk_per_trade: Porcentaje de riesgo por operación (0.02 = 2%)
            min_body_ratio: Ratio mínimo cuerpo alcista/segunda bajista (1.0 = igual o mayor)
            use_trailing_stop: Si usar trailing stop
            trailing_stop_pct: Porcentaje del trailing stop
        """
        parameters = {
            'risk_reward_ratio': risk_reward_ratio,
            'min_body_ratio': min_body_ratio
        }
        
        super().__init__(
            name="Two Bearish Pattern",
            parameters=parameters,
            risk_per_trade=risk_per_trade,
            use_trailing_stop=use_trailing_stop,
            trailing_stop_pct=trailing_stop_pct
        )
        
        logger.info(f"Estrategia inicializada - RR: 1:{risk_reward_ratio}, "
                   f"Min Body Ratio: {min_body_ratio}")
    
    def calculate_indicators(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Calcula indicadores necesarios para detectar el patrón
        
        Args:
            data: DataFrame con datos OHLC
            
        Returns:
            DataFrame con indicadores añadidos
        """
        df = data.copy()
        
        # Calcular tamaño del cuerpo de cada vela
        df['body'] = abs(df['close'] - df['open'])
        
        # Identificar tipo de vela (1 = alcista, -1 = bajista, 0 = doji)
        df['candle_type'] = np.where(
            df['close'] > df['open'], 1,  # Alcista
            np.where(df['close'] < df['open'], -1, 0)  # Bajista o Doji
        )
        
        # Guardar indicadores para uso posterior
        self.indicators['body'] = df['body']
        self.indicators['candle_type'] = df['candle_type']
        
        return df
    
    def _check_pattern(self, data: pd.DataFrame, idx: int) -> bool:
        """
        Verifica si se cumple el patrón en el índice dado
        
        Patrón:
        idx-2: Primera vela bajista (bearish)
        idx-1: Segunda vela bajista (bearish)
        idx: Vela alcista (bullish) - vela actual
        
        Args:
            data: DataFrame con datos
            idx: Índice a verificar
            
        Returns:
            True si se cumple el patrón
        """
        # Necesitamos al menos 3 velas
        if idx < 2:
            return False
        
        # Obtener las tres velas
        current = data.iloc[idx]      # Vela alcista
        prev1 = data.iloc[idx - 1]    # Segunda vela bajista
        prev2 = data.iloc[idx - 2]    # Primera vela bajista
        
        # Condición 1: prev2 debe ser bajista
        if prev2['candle_type'] != -1:
            return False
        
        # Condición 2: prev1 debe ser bajista
        if prev1['candle_type'] != -1:
            return False
        
        # Condición 3: current debe ser alcista
        if current['candle_type'] != 1:
            return False
        
        # Condición 4: Cuerpo de vela alcista >= cuerpo de segunda vela bajista
        min_ratio = self.parameters.get('min_body_ratio', 1.0)
        body_alcista = current['body']
        body_segunda_bajista = prev1['body']
        
        if body_segunda_bajista == 0:  # Evitar división por cero
            return False
            
        body_ratio = body_alcista / body_segunda_bajista
        
        if body_ratio < min_ratio:
            return False
        
        return True
    
    def generate_signals(self, data: pd.DataFrame) -> List[Signal]:
        """
        Genera señales de trading basadas en el patrón
        
        Args:
            data: DataFrame con datos e indicadores
            
        Returns:
            Lista de señales generadas
        """
        signals = []
        
        # Recorrer datos buscando el patrón
        for i in range(2, len(data)):
            if self._check_pattern(data, i):
                # Obtener las velas relevantes
                bullish_candle = data.iloc[i]      # Vela alcista actual
                second_bearish = data.iloc[i - 1]  # Segunda vela bajista
                first_bearish = data.iloc[i - 2]   # Primera vela bajista
                
                # Precio de entrada: cierre de la vela alcista
                entry_price = bullish_candle['close']
                
                # Stop Loss: mínimo de la segunda vela bajista
                stop_loss = second_bearish['low']
                
                # Calcular distancia del riesgo
                risk = entry_price - stop_loss
                
                # Validar que el stop loss sea válido
                if risk <= 0:
                    logger.warning(f"Patrón detectado en {bullish_candle.name} pero "
                                 f"SL inválido (risk={risk})")
                    continue
                
                # Take Profit: ratio 1:2
                rr_ratio = self.parameters.get('risk_reward_ratio', 2.0)
                reward = risk * rr_ratio
                take_profit = entry_price + reward
                
                # Crear señal
                signal = Signal(
                    timestamp=bullish_candle.name,
                    signal_type='BUY',
                    price=entry_price,
                    stop_loss=stop_loss,
                    take_profit=take_profit,
                    metadata={
                        'pattern': 'two_bearish_reversal',
                        'bullish_body': bullish_candle['body'],
                        'second_bearish_body': second_bearish['body'],
                        'first_bearish_body': first_bearish['body'],
                        'body_ratio': bullish_candle['body'] / second_bearish['body'],
                        'risk': risk,
                        'reward': reward,
                        'rr_ratio': rr_ratio
                    }
                )
                
                signals.append(signal)
                
                logger.info(f"Señal BUY generada: {signal}")
                logger.info(f"  Entry: {entry_price:.5f}")
                logger.info(f"  SL: {stop_loss:.5f} (Risk: {risk:.5f})")
                logger.info(f"  TP: {take_profit:.5f} (Reward: {reward:.5f})")
                logger.info(f"  Body Ratio: {signal.metadata['body_ratio']:.2f}")
        
        return signals
    
    def get_parameter_ranges(self) -> dict:
        """
        Define rangos para optimización de parámetros
        
        Returns:
            Diccionario con rangos {param: (min, max, step)}
        """
        return {
            'risk_reward_ratio': (1.5, 3.0, 0.5),
            'min_body_ratio': (0.5, 2.0, 0.25),
            'risk_per_trade': (0.01, 0.03, 0.005)
        }
    
    def __str__(self):
        """Representación en string de la estrategia"""
        return (f"TwoBearishPatternStrategy("
                f"RR={self.parameters['risk_reward_ratio']}:1, "
                f"MinBodyRatio={self.parameters['min_body_ratio']}, "
                f"Risk={self.risk_per_trade*100}%)")


# Ejemplo de uso
if __name__ == "__main__":
    """
    Ejemplo de cómo usar la estrategia
    """
    import MetaTrader5 as mt5
    from datetime import datetime, timedelta
    
    # Configurar logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Inicializar MT5
    if not mt5.initialize():
        print("Error al inicializar MT5")
        exit()
    
    try:
        # Obtener datos H4
        symbol = "EURUSD"
        timeframe = mt5.TIMEFRAME_H4
        
        # Últimos 500 candles
        rates = mt5.copy_rates_from_pos(symbol, timeframe, 0, 500)
        
        if rates is None:
            print(f"Error al obtener datos de {symbol}")
            exit()
        
        # Convertir a DataFrame
        df = pd.DataFrame(rates)
        df['time'] = pd.to_datetime(df['time'], unit='s')
        df.set_index('time', inplace=True)
        
        print(f"\nDatos obtenidos: {len(df)} velas H4 de {symbol}")
        print(f"Desde: {df.index[0]}")
        print(f"Hasta: {df.index[-1]}")
        
        # Crear y ejecutar estrategia
        strategy = TwoBearishPatternStrategy(
            risk_reward_ratio=2.0,
            risk_per_trade=0.02,
            min_body_ratio=1.0
        )
        
        print(f"\nEjecutando estrategia: {strategy}")
        
        # Ejecutar estrategia
        data_with_indicators, signals = strategy.run(df)
        
        print(f"\n{'='*60}")
        print(f"RESULTADOS")
        print(f"{'='*60}")
        print(f"Total de señales generadas: {len(signals)}")
        
        if signals:
            print(f"\nÚltimas 5 señales:")
            for signal in signals[-5:]:
                print(f"\n{signal}")
                print(f"  Ratio Cuerpo Alcista/Bajista: "
                      f"{signal.metadata['body_ratio']:.2f}")
                risk = signal.metadata['risk']
                reward = signal.metadata['reward']
                print(f"  Risk: {risk:.5f} | Reward: {reward:.5f} | "
                      f"RR: 1:{reward/risk:.1f}")
        
    finally:
        mt5.shutdown()