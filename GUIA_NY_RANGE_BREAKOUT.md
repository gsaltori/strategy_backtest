# 📖 GUÍA COMPLETA: NY RANGE BREAKOUT PARA XAUUSD

## 📋 Descripción de la Estrategia

### Concepto
La estrategia **NY Range Breakout** opera en el mercado de oro (XAUUSD) aprovechando los breakouts que ocurren después del rango de consolidación de Nueva York.

### Lógica de Trading

1. **Identificación del Rango** (21:50 - 22:15 hora NY)
   - Se calcula el máximo y mínimo del precio en este período
   - Considera automáticamente el cambio horario de verano/invierno
   - El rango debe ser de al menos 5 pips para ser válido

2. **Señales de Trading** (después de 22:15 hora NY)
   - **COMPRA**: Si el precio rompe por encima del máximo del rango
   - **VENTA**: Si el precio rompe por debajo del mínimo del rango

3. **Gestión de Riesgo**
   - **Stop Loss**: 34 pips (3.40 USD para XAUUSD)
   - **Take Profit**: 83 pips (8.30 USD para XAUUSD)
   - **Máximo**: 1 operación por día

### Parámetros de la Estrategia

| Parámetro | Valor por Defecto | Descripción |
|-----------|-------------------|-------------|
| `range_start_hour` | 21 | Hora de inicio del rango NY |
| `range_start_minute` | 50 | Minuto de inicio del rango |
| `range_end_hour` | 22 | Hora de fin del rango NY |
| `range_end_minute` | 15 | Minuto de fin del rango |
| `stop_loss_pips` | 34.0 | Stop loss en pips |
| `take_profit_pips` | 83.0 | Take profit en pips |
| `timezone` | 'America/New_York' | Zona horaria de referencia |
| `pip_value` | 0.10 | Valor de 1 pip para XAUUSD |
| `min_range_pips` | 5.0 | Rango mínimo válido en pips |
| `max_trades_per_day` | 1 | Máximo de trades por día |

---

## 🚀 Instalación y Configuración

### 1. Requisitos Previos

```bash
# Python 3.8 o superior
python --version

# Instalar dependencias
pip install -r requirements.txt
```

### 2. Dependencias Principales

```
pandas>=2.1.4
numpy>=1.26.2
pytz>=2023.3
plotly>=5.18.0
scikit-learn>=1.3.2  # Para optimización ML
scipy>=1.11.4
MetaTrader5>=5.0.4518  # Opcional, solo para datos reales
```

### 3. Estructura de Archivos

```
strategy_backtest/
├── ny_range_breakout_strategy.py    # Código de la estrategia
├── run_ny_range_backtest.py         # Script de ejecución
├── data_manager.py                  # Gestor de datos MT5
├── backtest_engine.py               # Motor de backtesting
├── ml_optimizer.py                  # Optimizador ML
├── config/
│   └── settings.py                  # Configuraciones
├── analysis/
│   ├── performance.py               # Análisis de rendimiento
│   └── reporting.py                 # Generación de reportes
└── strategies/
    └── base_strategy.py             # Clase base
```

---

## 📊 Cómo Ejecutar el Backtest

### Opción 1: Backtest Simple (Datos de Muestra)

```bash
python run_ny_range_backtest.py
# Selecciona opción: 1
```

Este modo:
- ✅ No requiere MetaTrader 5
- ✅ Usa datos sintéticos realistas de XAUUSD
- ✅ Ideal para probar la estrategia rápidamente
- ✅ Genera reportes HTML con gráficos

**Archivos Generados:**
- `ny_range_backtest_report.html` - Reporte completo
- `ny_range_backtest_charts.html` - Gráficos interactivos

### Opción 2: Backtest con Datos Reales (MT5)

```bash
python run_ny_range_backtest.py
# Selecciona opción: 2
```

Este modo:
- ⚠️ Requiere MetaTrader 5 instalado
- ✅ Usa datos reales de XAUUSD
- ✅ Mayor precisión en resultados
- ✅ Incluye spreads reales

**Requisitos:**
1. Tener MT5 instalado y abierto
2. Cuenta demo o real configurada
3. Símbolo XAUUSD disponible

### Uso Programático

```python
from datetime import datetime, timedelta
from ny_range_breakout_strategy import NYRangeBreakout
from backtest_engine import BacktestEngine
from config.settings import BacktestConfig

# Crear estrategia
strategy = NYRangeBreakout(
    range_start_hour=21,
    range_start_minute=50,
    range_end_hour=22,
    range_end_minute=15,
    stop_loss_pips=34.0,
    take_profit_pips=83.0,
    max_trades_per_day=1
)

# Configurar backtest
config = BacktestConfig(
    initial_capital=10000.0,
    commission_pct=0.0001,
    slippage_pct=0.0005,
    use_spread=True
)

# Cargar datos (ejemplo con datos de muestra)
data = generate_sample_xauusd_data(days=365)

symbol_info = {
    'point': 0.01,
    'digits': 2,
    'trade_contract_size': 100.0
}

# Ejecutar backtest
engine = BacktestEngine(config)
result = engine.run(strategy, data, symbol_info)

# Ver resultados
print(result.summary())
```

---

## 🤖 Optimización con Machine Learning

### ¿Qué es la Optimización ML?

La optimización ML utiliza algoritmos inteligentes para encontrar automáticamente los mejores parámetros de la estrategia. En lugar de probar todas las combinaciones (fuerza bruta), usa:

1. **Optimización Bayesiana**: Aprende de cada prueba para buscar más eficientemente
2. **Random Forest**: Predice qué combinaciones serán prometedoras
3. **Validación Cruzada**: Evita overfitting usando múltiples períodos

### Ejecutar Optimización ML

```bash
python run_ny_range_backtest.py
# Selecciona opción: 3 (datos de muestra) o 4 (datos MT5)
```

**Parámetros que se Optimizan:**
- `stop_loss_pips`: 20-50 pips
- `take_profit_pips`: 50-150 pips
- `min_range_pips`: 3-15 pips
- `range_start_minute`: 45-55 minutos
- `range_end_minute`: 10-20 minutos

**Salida Generada:**
- Mejores parámetros encontrados
- Score de entrenamiento y validación
- Ratio de overfitting
- Importancia de cada parámetro
- `ny_range_optimization_results.csv` - Todas las iteraciones

### Uso Programático

```python
from ml_optimizer import MLStrategyOptimizer
from ny_range_breakout_strategy import NYRangeBreakout

# Crear optimizador
optimizer = MLStrategyOptimizer(
    strategy_class=NYRangeBreakout,
    data=data,
    symbol_info=symbol_info,
    target_metric='sharpe_ratio',  # Métrica a maximizar
    n_iterations=50,               # Iteraciones de búsqueda
    cv_splits=5,                   # Validación cruzada
    validation_pct=0.3             # 30% datos out-of-sample
)

# Ejecutar optimización
result = optimizer.bayesian_optimization()

# Ver mejores parámetros
print("Mejores parámetros:")
for param, value in result.best_params.items():
    print(f"  {param}: {value}")

# Crear estrategia optimizada
optimized_strategy = NYRangeBreakout(**result.best_params)
```

### Interpretación de Resultados

**Métricas Clave:**

1. **Train Score**: Rendimiento en datos de entrenamiento
2. **Validation Score**: Rendimiento en datos no vistos
3. **Overfitting Ratio**: Train / Validation
   - Ideal: 1.0 - 1.2 (mínimo overfitting)
   - Aceptable: 1.2 - 1.5
   - Problema: > 1.5 (mucho overfitting)

4. **Feature Importance**: Sensibilidad a cada parámetro
   - Mayor valor = más impacto en resultados
   - Ayuda a identificar parámetros críticos

**Ejemplo de Output:**

```
🏆 MEJORES PARÁMETROS ENCONTRADOS:
   stop_loss_pips: 28.50
   take_profit_pips: 95.20
   min_range_pips: 7.30
   range_start_minute: 48.00
   range_end_minute: 17.00

📈 MÉTRICAS:
   Mejor Score (train): 1.8540
   Score (validation): 1.6320
   Ratio Overfitting: 1.14  ← Excelente!
   Iteraciones: 50

🔍 IMPORTANCIA DE PARÁMETROS:
   take_profit_pips: 0.4520    ← Más importante
   stop_loss_pips: 0.3210
   min_range_pips: 0.1850
   range_start_minute: 0.0420  ← Menos importante
```

---

## 🔄 Walk-Forward Analysis

### ¿Qué es Walk-Forward?

Es la validación más robusta para estrategias de trading:

1. **Divide** los datos en ventanas móviles
2. **Optimiza** parámetros en cada ventana de entrenamiento
3. **Prueba** los parámetros optimizados en período siguiente
4. **Re-optimiza** periódicamente con datos nuevos

Esto simula cómo funcionaría la estrategia en trading real, donde los parámetros se ajustan con el tiempo.

### Ejecutar Walk-Forward

```bash
python run_ny_range_backtest.py
# Selecciona opción: 5 (datos de muestra) o 6 (datos MT5)
```

**Configuración Típica:**
- Ventana de entrenamiento: 3 meses
- Ventana de prueba: 1 mes
- Re-optimización: cada 1 mes
- Período total recomendado: 2+ años

### Uso Programático

```python
from ml_optimizer import MLStrategyOptimizer

optimizer = MLStrategyOptimizer(
    strategy_class=NYRangeBreakout,
    data=data,  # Datos de 2+ años
    symbol_info=symbol_info,
    target_metric='sharpe_ratio',
    n_iterations=30,  # Menos iteraciones por ventana
    cv_splits=3
)

# Ejecutar WF
wf_result = optimizer.walk_forward_optimization(
    train_period_months=3,  # Entrenar con 3 meses
    test_period_months=1,   # Probar en 1 mes
    step_months=1           # Avanzar 1 mes cada vez
)

# Ver resultados
print(f"Ventanas analizadas: {len(wf_result['windows'])}")
print(f"Sharpe promedio (in-sample): {wf_result['avg_train_score']:.4f}")
print(f"Sharpe promedio (out-sample): {wf_result['avg_test_score']:.4f}")
print(f"Degradación: {wf_result['degradation_ratio']:.2f}")
print(f"Consistencia: {wf_result['consistency']:.2f}")
```

### Interpretación de Resultados

**Métricas Clave:**

1. **Average Train Score**: Rendimiento promedio en entrenamiento
2. **Average Test Score**: Rendimiento promedio en prueba (más importante)
3. **Degradation Ratio**: Test / Train
   - Ideal: 0.8 - 1.0 (mínima degradación)
   - Aceptable: 0.6 - 0.8
   - Problema: < 0.6 (mucha degradación)

4. **Consistency**: Porcentaje de ventanas con resultados positivos
   - Excelente: > 70%
   - Bueno: 60-70%
   - Regular: 50-60%
   - Malo: < 50%

**Archivo Generado:**
- `ny_range_walkforward_results.csv` - Detalle de cada ventana

---

## 📊 Análisis de Resultados

### Métricas Principales

| Métrica | Descripción | Valor Ideal |
|---------|-------------|-------------|
| **Total Return %** | Retorno total del período | > 20% anual |
| **Win Rate** | % de trades ganadores | > 50% |
| **Profit Factor** | Ganancias / Pérdidas | > 1.5 |
| **Sharpe Ratio** | Retorno ajustado por riesgo | > 1.0 |
| **Max Drawdown** | Caída máxima | < 20% |
| **Expectancy** | Ganancia esperada por trade | > 0 |
| **Total Trades** | Número de operaciones | 50-200/año |

### Reportes HTML

Los reportes generados incluyen:

1. **Resumen Ejecutivo**
   - Métricas principales
   - Rendimiento general
   - Estadísticas de riesgo

2. **Gráficos Interactivos**
   - Equity curve (curva de capital)
   - Drawdown chart
   - Distribución de P&L
   - Price chart con señales
   - Análisis temporal por hora/día/mes

3. **Tabla de Trades**
   - Detalle de cada operación
   - Filtros y ordenamiento
   - Análisis de rachas

4. **Análisis de Riesgo**
   - Máximo drawdown
   - Value at Risk (VaR)
   - Recovery time
   - Risk/Reward ratio

### Cómo Interpretar la Equity Curve

```
📈 Curva Ideal:
   ╱╱╱╱╱╱╱  ← Crecimiento constante
  ╱

❌ Curva Problemática:
   ╱╲╱╲     ← Volatilidad excesiva
  ╱  ╲╱
```

**Señales de Alerta:**
- Drawdowns frecuentes > 15%
- Períodos largos sin recuperación
- Crecimiento inconsistente
- Dependencia de pocas operaciones grandes

---

## ⚙️ Personalización de la Estrategia

### Modificar Parámetros

```python
# Estrategia más conservadora
conservative_strategy = NYRangeBreakout(
    stop_loss_pips=25.0,      # SL más ajustado
    take_profit_pips=100.0,   # TP más grande
    min_range_pips=8.0,       # Rangos más grandes
    max_trades_per_day=1
)

# Estrategia más agresiva
aggressive_strategy = NYRangeBreakout(
    stop_loss_pips=40.0,      # SL más amplio
    take_profit_pips=70.0,    # TP más cercano
    min_range_pips=3.0,       # Rangos más pequeños
    max_trades_per_day=2      # Permitir 2 trades/día
)

# Ajustar horario del rango
custom_range_strategy = NYRangeBreakout(
    range_start_hour=21,
    range_start_minute=45,    # Empezar 5 min antes
    range_end_hour=22,
    range_end_minute=20,      # Terminar 5 min después
    stop_loss_pips=34.0,
    take_profit_pips=83.0
)
```

### Añadir Filtros Adicionales

Puedes extender la estrategia añadiendo filtros en el método `generate_signals`:

```python
class NYRangeBreakoutFiltered(NYRangeBreakout):
    """Versión con filtros adicionales"""
    
    def generate_signals(self, data: pd.DataFrame) -> List[Signal]:
        # Obtener señales base
        signals = super().generate_signals(data)
        
        # Filtrar señales
        filtered_signals = []
        
        for signal in signals:
            # Ejemplo: Solo operar si el rango es > 10 pips
            if signal.metadata.get('range_pips', 0) > 10:
                filtered_signals.append(signal)
        
        return filtered_signals
```

---

## 🛠️ Troubleshooting

### Error: "Module not found"

```bash
# Instalar dependencias faltantes
pip install -r requirements.txt

# O específicamente
pip install pandas numpy pytz plotly scikit-learn scipy
```

### Error: "MT5 initialization failed"

**Soluciones:**
1. Asegúrate de que MT5 esté abierto
2. Verifica que tengas una cuenta configurada
3. Usa datos de muestra (opción 1 o 3)

```python
# Alternativa: usar datos de muestra
data = generate_sample_xauusd_data(days=365)
```

### Error: "Timezone not found"

```bash
# Instalar pytz
pip install pytz

# Verificar timezones disponibles
python -c "import pytz; print(pytz.all_timezones)"
```

### Optimización ML muy lenta

**Soluciones:**
1. Reducir `n_iterations`:
```python
optimizer = MLStrategyOptimizer(
    strategy_class=NYRangeBreakout,
    data=data,
    symbol_info=symbol_info,
    n_iterations=20  # Reducir de 50 a 20
)
```

2. Usar menos datos:
```python
data = generate_sample_xauusd_data(days=180)  # 6 meses en vez de 1 año
```

3. Reducir CV splits:
```python
optimizer = MLStrategyOptimizer(
    strategy_class=NYRangeBreakout,
    data=data,
    symbol_info=symbol_info,
    cv_splits=3  # En vez de 5
)
```

---

## 📚 Mejores Prácticas

### 1. Validación Robusta

✅ **HACER:**
- Usar Walk-Forward Analysis
- Validar en múltiples períodos
- Verificar consistencia temporal
- Probar con diferentes mercados

❌ **NO HACER:**
- Optimizar en todo el conjunto de datos
- Ignorar períodos de bajo rendimiento
- Confiar solo en in-sample metrics

### 2. Gestión de Riesgo

✅ **HACER:**
- Mantener drawdown < 20%
- Diversificar estrategias
- Usar tamaños de posición razonables
- Establecer límites de pérdida diaria

❌ **NO HACER:**
- Aumentar apalancamiento después de pérdidas
- Operar sin stop loss
- Ignorar el tamaño de posición

### 3. Optimización de Parámetros

✅ **HACER:**
- Usar optimización ML (Bayesiana)
- Validar con out-of-sample data
- Verificar estabilidad de parámetros
- Re-optimizar periódicamente

❌ **NO HACER:**
- Sobre-optimizar (curve fitting)
- Usar solo optimización grid search
- Ignorar el overfitting ratio
- Optimizar demasiados parámetros

### 4. Análisis de Resultados

✅ **HACER:**
- Revisar todos los trades individuales
- Analizar patrones de pérdidas
- Verificar distribución de P&L
- Estudiar correlación temporal

❌ **NO HACER:**
- Fijarse solo en retorno total
- Ignorar el drawdown
- Subestimar la importancia del Sharpe
- Omitir análisis de rachas

---

## 🎓 Preguntas Frecuentes

### P: ¿Puedo usar esta estrategia en trading real?

**R:** Esta estrategia está diseñada para backtesting educacional. Antes de usarla en real:
1. Prueba extensivamente en cuenta demo
2. Verifica resultados con Walk-Forward
3. Entiende completamente los riesgos
4. Considera contratar asesoría profesional

### P: ¿Por qué usar el rango 21:50-22:15 NY?

**R:** Este período captura:
- Final de sesión europea
- Inicio de sesión americana
- Alta liquidez en XAUUSD
- Formación de rangos consistentes
- Breakouts con momentum

Puedes experimentar con otros horarios usando optimización ML.

### P: ¿Qué timeframe usar?

**R:** Recomendado: **5 minutos** (M5)
- Captura bien el rango de 25 minutos
- Suficientes barras para análisis
- No demasiado ruidoso

También funciona con:
- 1 minuto (M1): Más señales, más ruido
- 15 minutos (M15): Menos señales, más suave

### P: ¿Cuántos datos necesito para backtest confiable?

**R:** Mínimo recomendado:
- **Backtest simple**: 6-12 meses
- **Optimización ML**: 1 año
- **Walk-Forward**: 2+ años

Más datos = resultados más robustos

### P: ¿La estrategia funciona en otros símbolos?

**R:** Diseñada específicamente para XAUUSD, pero puedes adaptarla:

```python
# Para otros símbolos, ajusta pip_value
strategy_eurusd = NYRangeBreakout(
    pip_value=0.0001,  # Para pares de divisas
    stop_loss_pips=20,
    take_profit_pips=40
)

strategy_usdjpy = NYRangeBreakout(
    pip_value=0.01,    # Para USDJPY
    stop_loss_pips=25,
    take_profit_pips=50
)
```

### P: ¿Cómo manejar el cambio horario?

**R:** La estrategia lo maneja automáticamente usando `pytz`:
- Detecta DST (Daylight Saving Time)
- Convierte UTC a hora NY correctamente
- No requiere ajustes manuales

---

## 📞 Soporte y Recursos

### Documentación del Proyecto
- `START_HERE.md` - Inicio rápido
- `README.md` - Documentación completa
- `BEST_PRACTICES.md` - Mejores prácticas
- `TROUBLESHOOTING.md` - Solución de problemas

### Recursos Externos
- [Documentación MetaTrader 5 Python](https://www.mql5.com/en/docs/python_metatrader5)
- [Pandas Documentation](https://pandas.pydata.org/docs/)
- [Scikit-learn ML](https://scikit-learn.org/stable/)
- [Investopedia Trading](https://www.investopedia.com/trading-4427765)

---

## ⚠️ Disclaimer

**IMPORTANTE:** 

- Este sistema es para propósitos educacionales y de backtesting únicamente
- Resultados pasados NO garantizan rendimiento futuro
- El trading conlleva riesgo significativo de pérdida
- Nunca inviertas dinero que no puedas permitirte perder
- Busca asesoría financiera profesional antes de operar con dinero real
- Los autores no se responsabilizan por pérdidas en trading real

---

## ✅ Checklist de Inicio

- [ ] Python 3.8+ instalado
- [ ] Dependencias instaladas (`pip install -r requirements.txt`)
- [ ] Archivos de estrategia descargados
- [ ] Primer backtest ejecutado exitosamente
- [ ] Reportes HTML revisados
- [ ] Optimización ML probada
- [ ] Walk-Forward Analysis ejecutado
- [ ] Parámetros personalizados definidos
- [ ] Resultados documentados
- [ ] Estrategia validada en múltiples períodos

---

## 🎉 ¡Listo para Empezar!

```bash
# Ejecuta el sistema
python run_ny_range_backtest.py

# Selecciona opción 7 para análisis completo
# O elige opciones individuales según necesites
```

**¡Feliz backtesting! 📈🚀**
