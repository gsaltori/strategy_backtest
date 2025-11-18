"""
Ejemplo Simple: Estrategia NY Range Breakout OPTIMIZADA v2.0

Este script demuestra cómo usar la mejor versión de la estrategia.

Ejecutar: python ejemplo_estrategia_optimizada.py
"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Importar la estrategia optimizada
from strategies.ny_range_breakout_optimized import (
    NYRangeBreakoutOptimized,
    create_optimized_ny_range_strategy
)


def generar_datos_muestra(dias=180):
    """Genera datos sintéticos de XAUUSD para pruebas"""
    print(f"📊 Generando {dias} días de datos XAUUSD...")
    
    # Configuración
    inicio = datetime.now() - timedelta(days=dias)
    periodos = dias * 288  # 288 barras de 5min por día
    
    # Generar datos con patrón realista
    fechas = pd.date_range(start=inicio, periods=periodos, freq='5min')
    
    # Precio base con tendencia y volatilidad
    precio_base = 2650
    tendencia = np.linspace(0, 50, periodos)  # Tendencia alcista
    noise = np.random.normal(0, 5, periodos)  # Volatilidad
    ruido_sesion = np.sin(np.arange(periodos) / 288 * 2 * np.pi) * 10  # Patrones diarios
    
    close = precio_base + tendencia + noise + ruido_sesion
    
    # OHLC realista
    volatilidad = 3
    high = close + np.random.uniform(0, volatilidad, periodos)
    low = close - np.random.uniform(0, volatilidad, periodos)
    open_price = close + np.random.uniform(-volatilidad/2, volatilidad/2, periodos)
    
    # Crear DataFrame
    data = pd.DataFrame({
        'open': open_price,
        'high': high,
        'low': low,
        'close': close,
        'volume': np.random.randint(100, 1000, periodos)
    }, index=fechas)
    
    print(f"✅ Datos generados: {len(data)} barras desde {data.index[0]} hasta {data.index[-1]}")
    return data


print("="*70)
print("🚀 NY RANGE BREAKOUT OPTIMIZADA v2.0 - EJEMPLO SIMPLE")
print("="*70)

# ============================================================================
# PARTE 1: CREAR ESTRATEGIA CON PARÁMETROS ÓPTIMOS
# ============================================================================

print("\n📋 PASO 1: Crear estrategia optimizada")
print("-" * 70)

# Opción A: Usar función helper con parámetros por defecto (recomendado)
estrategia = create_optimized_ny_range_strategy()

# Opción B: Crear manualmente con personalización
# estrategia = NYRangeBreakoutOptimized(
#     risk_per_trade=0.02,  # 2% riesgo
#     stop_loss_pips=34.0,
#     take_profit_pips=83.0,
#     use_partial_tp=True,
#     use_breakeven=True,
#     use_trailing_stop=True
# )

print("✅ Estrategia creada con configuración optimizada:")
print(f"   Nombre: {estrategia.name}")
print(f"   Riesgo por trade: {estrategia.parameters['risk_per_trade']*100}%")
print(f"   Stop Loss: {estrategia.parameters['stop_loss_pips']} pips")
print(f"   Take Profit: {estrategia.parameters['take_profit_pips']} pips")
print(f"   TP Parcial: {'✅ Activado' if estrategia.parameters['use_partial_tp'] else '❌ Desactivado'}")
print(f"   Breakeven: {'✅ Activado' if estrategia.parameters['use_breakeven'] else '❌ Desactivado'}")
print(f"   Trailing Stop: {'✅ Activado' if estrategia.parameters['use_trailing_stop'] else '❌ Desactivado'}")

print("\n🔍 Filtros activos:")
print(f"   Rango mínimo: {estrategia.parameters['min_range_pips']} pips")
print(f"   Rango máximo: {estrategia.parameters['max_range_pips']} pips")
print(f"   ATR multiplier: {estrategia.parameters['min_atr_multiplier']}x")
print(f"   Spread máximo: {estrategia.parameters['max_spread_pips']} pips")


# ============================================================================
# PARTE 2: CARGAR DATOS
# ============================================================================

print("\n📊 PASO 2: Cargar datos de mercado")
print("-" * 70)

# Generar datos de muestra
datos = generar_datos_muestra(dias=180)

# Información del símbolo XAUUSD
symbol_info = {
    'name': 'XAUUSD',
    'point': 0.01,
    'digits': 2,
    'trade_contract_size': 100.0,
    'volume_min': 0.01,
    'volume_max': 100.0,
    'volume_step': 0.01,
    'spread': 2  # 2 puntos de spread (0.02 USD)
}

print(f"✅ Symbol info configurado para {symbol_info['name']}")


# ============================================================================
# PARTE 3: EJECUTAR ESTRATEGIA Y GENERAR SEÑALES
# ============================================================================

print("\n🎯 PASO 3: Ejecutar estrategia y generar señales")
print("-" * 70)

# Calcular indicadores y generar señales
datos_procesados, señales = estrategia.run(datos)

print(f"✅ Estrategia ejecutada:")
print(f"   Barras procesadas: {len(datos_procesados)}")
print(f"   Señales generadas: {len(señales)}")

if len(señales) > 0:
    # Estadísticas de señales
    señales_compra = [s for s in señales if s.signal_type == 'BUY']
    señales_venta = [s for s in señales if s.signal_type == 'SELL']
    
    print(f"\n📈 Desglose de señales:")
    print(f"   Compras: {len(señales_compra)}")
    print(f"   Ventas: {len(señales_venta)}")
    
    # Mostrar primeras 3 señales
    print(f"\n🔍 Primeras {min(3, len(señales))} señales:")
    for i, señal in enumerate(señales[:3], 1):
        print(f"\n   Señal #{i}: {señal.signal_type}")
        print(f"      Fecha: {señal.timestamp}")
        print(f"      Precio: ${señal.price:,.2f}")
        print(f"      Stop Loss: ${señal.stop_loss:,.2f}")
        print(f"      Take Profit: ${señal.take_profit:,.2f}")
        
        # Calcular R:R
        if señal.signal_type == 'BUY':
            riesgo = señal.price - señal.stop_loss
            recompensa = señal.take_profit - señal.price
        else:
            riesgo = señal.stop_loss - señal.price
            recompensa = señal.price - señal.take_profit
        
        rr_ratio = recompensa / riesgo if riesgo > 0 else 0
        print(f"      Risk:Reward: 1:{rr_ratio:.2f}")
        print(f"      Rango: {señal.metadata.get('range_pips', 0):.1f} pips")
        print(f"      ATR: {señal.metadata.get('atr_pips', 0):.1f} pips")
        
        # Info de gestión avanzada
        if señal.metadata.get('use_partial_tp'):
            print(f"      TP Parcial: ${señal.metadata.get('partial_tp_price', 0):,.2f} ({señal.metadata.get('partial_tp_percent', 0)*100:.0f}%)")
        
        if señal.metadata.get('use_breakeven'):
            print(f"      Breakeven: ${señal.metadata.get('breakeven_price', 0):,.2f} tras ${señal.metadata.get('breakeven_activation_price', 0):,.2f}")
    
    # Estadísticas de rangos
    rangos = [s.metadata.get('range_pips', 0) for s in señales]
    atrs = [s.metadata.get('atr_pips', 0) for s in señales if s.metadata.get('atr_pips')]
    
    print(f"\n📊 ESTADÍSTICAS:")
    print(f"   Rango promedio: {np.mean(rangos):.2f} pips")
    print(f"   Rango min/max: {np.min(rangos):.2f} / {np.max(rangos):.2f} pips")
    if atrs:
        print(f"   ATR promedio: {np.mean(atrs):.2f} pips")
        print(f"   ATR min/max: {np.min(atrs):.2f} / {np.max(atrs):.2f} pips")
    
else:
    print("\n⚠️ No se generaron señales")
    print("   Posibles razones:")
    print("   - Filtros muy estrictos")
    print("   - Periodo muy corto")
    print("   - Rangos fuera de límites configurados")
    print("   - Volatilidad insuficiente")


# ============================================================================
# PARTE 4: PRÓXIMOS PASOS
# ============================================================================

print("\n" + "="*70)
print("💡 PRÓXIMOS PASOS")
print("="*70)

print("""
Para un análisis completo:

1. BACKTEST COMPLETO:
   - Usar BacktestEngine con estas señales
   - Simular ejecución realista
   - Calcular métricas de rendimiento
   
   from backtest_engine import BacktestEngine
   from config.settings import BacktestConfig
   
   config = BacktestConfig(initial_capital=10000.0)
   engine = BacktestEngine(config)
   resultado = engine.run(estrategia, datos, symbol_info)

2. OPTIMIZACIÓN ML:
   - Encontrar los mejores parámetros
   - Usar MLStrategyOptimizer
   - 100+ iteraciones recomendadas
   
   from ml_optimizer import MLStrategyOptimizer
   
   optimizer = MLStrategyOptimizer(
       strategy_class=NYRangeBreakoutOptimized,
       data=datos,
       symbol_info=symbol_info,
       n_iterations=100
   )
   result = optimizer.bayesian_optimization()

3. WALK-FORWARD ANALYSIS:
   - Validar robustez temporal
   - Simular re-optimización periódica
   - Detectar overfitting
   
   wf_result = optimizer.walk_forward_optimization(
       train_period_months=3,
       test_period_months=1
   )

4. PERSONALIZACIÓN:
   - Ajustar parámetros según tu perfil de riesgo
   - Experimentar con filtros
   - Probar en diferentes mercados
""")

print("\n" + "="*70)
print("✅ EJEMPLO COMPLETADO")
print("="*70)

print(f"""
📊 Resumen:
   - Datos: {len(datos)} barras de XAUUSD
   - Señales: {len(señales)} ({len(señales_compra) if len(señales) > 0 else 0} compras, {len(señales_venta) if len(señales) > 0 else 0} ventas)
   - Período: {datos.index[0]} a {datos.index[-1]}

🎯 Características de la Estrategia OPTIMIZADA v2.0:
   ✅ Gestión de riesgo dinámica (lotaje correcto)
   ✅ Take profit parcial (asegura ganancias)
   ✅ Breakeven automático (trade risk-free)
   ✅ Trailing stop inteligente
   ✅ Filtros de calidad (ATR, spread, rangos)
   ✅ 11 parámetros optimizables

📚 Para más información:
   - Ver: ESTRATEGIA_OPTIMIZADA_V2.md
   - Comparación vs versión original
   - Guía completa de parámetros
   - Configuraciones recomendadas

⚠️ Recuerda:
   - Esto es BACKTESTING (no garantiza resultados futuros)
   - Prueba en DEMO antes de real
   - Gestiona el riesgo apropiadamente
   - Re-optimiza periódicamente

🚀 ¡Éxito con tu trading sistemático!
""")
