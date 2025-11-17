"""
Script de Diagnóstico
Verifica datos MT5 y detección de rangos NY

Uso: python diagnostico_ny_range.py
"""

import sys
from datetime import datetime, timedelta
import pandas as pd
import pytz
from data_manager import MT5DataManager
from config.settings import MT5Config
from strategies.ny_range_breakout_strategy import NYRangeBreakout


def diagnosticar_datos_mt5():
    """Diagnóstico de datos MT5"""
    print("\n" + "="*70)
    print("🔍 DIAGNÓSTICO - Datos MT5 y Horarios NY")
    print("="*70)
    
    # Conectar a MT5
    print("\n📊 Conectando a MT5...")
    config = MT5Config()
    data_manager = MT5DataManager(config)
    
    if not data_manager.connect():
        print("❌ No se pudo conectar a MT5")
        return
    
    try:
        # Validar símbolo
        print("\n🔍 Validando XAUUSD...")
        if not data_manager.validate_symbol("XAUUSD"):
            print("❌ XAUUSD no disponible")
            return
        
        # Obtener información del símbolo
        symbol_info = data_manager.get_symbol_info("XAUUSD")
        
        print(f"✅ XAUUSD disponible")
        if symbol_info:
            print(f"   Spread: {symbol_info.get('spread', 'N/A')}")
            print(f"   Digits: {symbol_info.get('digits', 'N/A')}")
            print(f"   Contract Size: {symbol_info.get('trade_contract_size', 'N/A')}")
            print(f"   Bid: {symbol_info.get('bid', 'N/A'):.2f}")
            print(f"   Ask: {symbol_info.get('ask', 'N/A'):.2f}")
        
        # Descargar datos recientes
        print("\n📥 Descargando últimos 3 días de datos (M5)...")
        data = data_manager.get_historical_data(
            symbol="XAUUSD",
            timeframe="M5",
            start_date=datetime.now() - timedelta(days=3),
            count=1000
        )
        
        print(f"✅ Datos descargados: {len(data)} barras")
        print(f"   Período: {data.index[0]} a {data.index[-1]}")
        print(f"   Timezone: {data.index.tz if hasattr(data.index, 'tz') else 'Sin timezone'}")
        
        # Analizar horarios
        print("\n🕐 ANÁLISIS DE HORARIOS:")
        print("-" * 70)
        
        # Zona horaria NY
        ny_tz = pytz.timezone('America/New_York')
        
        # Mostrar algunas barras con conversión a NY
        print("\n📅 Muestra de barras (últimas 10):")
        for i in range(max(0, len(data)-10), len(data)):
            bar = data.iloc[i]
            timestamp = data.index[i]
            
            # Convertir a NY
            if timestamp.tz is None:
                timestamp_utc = timestamp.tz_localize('UTC')
            else:
                timestamp_utc = timestamp
            
            ny_time = timestamp_utc.tz_convert(ny_tz)
            
            print(f"  {timestamp} UTC → {ny_time.strftime('%Y-%m-%d %H:%M:%S %Z')}")
        
        # Crear estrategia
        print("\n🎯 Creando estrategia...")
        strategy = NYRangeBreakout(
            range_start_hour=21,
            range_start_minute=50,
            range_end_hour=22,
            range_end_minute=15,
            stop_loss_pips=34.0,
            take_profit_pips=83.0,
            pip_value=0.10,
            min_range_pips=5.0
        )
        
        print("✅ Estrategia creada")
        print(f"   Buscando rangos: 21:50 - 22:15 NY")
        
        # Calcular indicadores
        print("\n⚙️ Calculando indicadores (detectando rangos)...")
        data_with_indicators = strategy.calculate_indicators(data)
        
        # Verificar rangos encontrados
        print(f"\n📊 RANGOS DETECTADOS:")
        print(f"   Total de rangos: {len(strategy.daily_ranges)}")
        
        if len(strategy.daily_ranges) == 0:
            print("\n⚠️ NO SE ENCONTRARON RANGOS")
            print("\n💡 Posibles causas:")
            print("   1. Los datos no cubren el horario 21:50-22:15 NY")
            print("   2. El timeframe M5 no tiene suficiente granularidad")
            print("   3. Problema con la conversión de timezone")
            
            # Verificar qué horas tenemos
            print("\n🔍 Verificando horas disponibles en datos:")
            data_ny = data.copy()
            data_ny['ny_hour'] = data_ny.index.map(lambda x: 
                x.tz_localize('UTC').tz_convert(ny_tz).hour if x.tz is None 
                else x.tz_convert(ny_tz).hour
            )
            
            horas_unicas = sorted(data_ny['ny_hour'].unique())
            print(f"   Horas NY en datos: {horas_unicas}")
            
            if 21 not in horas_unicas and 22 not in horas_unicas:
                print("\n❌ Los datos NO contienen las horas 21 y 22 NY")
                print("   Necesitas datos que cubran esas horas")
            
        else:
            print(f"\n✅ {len(strategy.daily_ranges)} rangos encontrados")
            print("\n📋 Detalle de rangos:")
            for date, range_info in list(strategy.daily_ranges.items())[:5]:
                print(f"   {date}:")
                print(f"      High: {range_info['high']:.2f}")
                print(f"      Low: {range_info['low']:.2f}")
                print(f"      Pips: {range_info.get('range_pips', 0):.1f}")
        
        # Generar señales
        print("\n🎯 Generando señales...")
        signals = strategy.generate_signals(data_with_indicators)
        
        print(f"\n📊 SEÑALES GENERADAS: {len(signals)}")
        
        if len(signals) == 0:
            print("\n⚠️ NO SE GENERARON SEÑALES")
            print("\n💡 Posibles causas:")
            print("   1. No hubo breakouts en el período analizado")
            print("   2. Los rangos fueron muy pequeños (< min_range_pips)")
            print("   3. Ya se ejecutó el máximo de trades por día")
        else:
            print(f"\n✅ {len(signals)} señales generadas")
            print("\n📋 Detalle de señales:")
            for i, signal in enumerate(signals[:3], 1):
                print(f"\n   Señal {i}:")
                print(f"      Tipo: {signal.signal_type}")
                print(f"      Fecha: {signal.timestamp}")
                print(f"      Precio: {signal.price:.2f}")
                print(f"      SL: {signal.stop_loss:.2f}")
                print(f"      TP: {signal.take_profit:.2f}")
                print(f"      Size: {signal.position_size}")
                print(f"      Rango: {signal.metadata.get('range_pips', 0):.1f} pips")
        
        # Análisis de barras
        bars_in_range = data_with_indicators['in_range'].sum()
        bars_after_range = data_with_indicators['after_range'].sum()
        
        print(f"\n📊 ANÁLISIS DE BARRAS:")
        print(f"   Total de barras: {len(data_with_indicators)}")
        print(f"   Barras en rango (21:50-22:15 NY): {bars_in_range}")
        print(f"   Barras después del rango: {bars_after_range}")
        
        print("\n" + "="*70)
        print("✅ DIAGNÓSTICO COMPLETADO")
        print("="*70)
        
    finally:
        data_manager.disconnect()
        print("\n👋 Desconectado de MT5")


if __name__ == "__main__":
    try:
        diagnosticar_datos_mt5()
    except Exception as e:
        print(f"\n❌ Error durante el diagnóstico: {e}")
        import traceback
        traceback.print_exc()
