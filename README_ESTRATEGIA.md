# 🎯 Estrategia NY Range Breakout para XAUUSD

## 📦 Archivos Generados

Este paquete contiene una estrategia completa de trading con backtesting y optimización ML:

### 📄 Archivos Principales

1. **`ny_range_breakout_strategy.py`** ⭐
   - Implementación completa de la estrategia
   - Clase `NYRangeBreakout` lista para usar
   - Manejo automático de horarios NY (DST)
   - Gestión de riesgo integrada (SL/TP)

2. **`run_ny_range_backtest.py`** 🚀
   - Script de ejecución principal con menú interactivo
   - Backtest simple y con optimización ML
   - Walk-Forward Analysis
   - Generación automática de reportes

3. **`ejemplo_simple.py`** 🎓
   - Ejemplo minimalista para comenzar
   - Código comentado paso a paso
   - No requiere MT5
   - Ideal para aprendizaje

4. **`GUIA_NY_RANGE_BREAKOUT.md`** 📖
   - Documentación completa
   - Explicación de la estrategia
   - Instrucciones de uso
   - Troubleshooting
   - Mejores prácticas

---

## 🚀 Inicio Rápido (3 pasos)

### 1️⃣ Copiar archivos al proyecto

```bash
# Copiar los archivos al directorio del proyecto
cp ny_range_breakout_strategy.py /path/to/strategy_backtest/strategies/
cp run_ny_range_backtest.py /path/to/strategy_backtest/
cp ejemplo_simple.py /path/to/strategy_backtest/
```

### 2️⃣ Instalar dependencias (si no están instaladas)

```bash
pip install pandas numpy pytz plotly scikit-learn scipy
```

### 3️⃣ Ejecutar

**Opción A: Ejemplo Simple (Recomendado para empezar)**
```bash
python ejemplo_simple.py
```

**Opción B: Sistema Completo**
```bash
python run_ny_range_backtest.py
# Selecciona opción del menú
```

---

## 📋 Descripción de la Estrategia

### Lógica de Trading

```
┌─────────────────────────────────────────┐
│  21:50 - 22:15 NY (Rango)               │
│  ┌─────────────────────────────┐        │
│  │  Calcular:                  │        │
│  │  • Máximo del período       │        │
│  │  • Mínimo del período       │        │
│  └─────────────────────────────┘        │
└─────────────────────────────────────────┘
              ▼
┌─────────────────────────────────────────┐
│  Después de 22:15 NY                    │
│  ┌─────────────────────────────┐        │
│  │  Si precio > Máximo:        │        │
│  │    ➜ COMPRA                 │        │
│  │    SL: -34 pips             │        │
│  │    TP: +83 pips             │        │
│  └─────────────────────────────┘        │
│  ┌─────────────────────────────┐        │
│  │  Si precio < Mínimo:        │        │
│  │    ➜ VENTA                  │        │
│  │    SL: +34 pips             │        │
│  │    TP: -83 pips             │        │
│  └─────────────────────────────┘        │
└─────────────────────────────────────────┘
```

### Parámetros

| Parámetro | Valor | Descripción |
|-----------|-------|-------------|
| Símbolo | XAUUSD | Oro vs Dólar |
| Timeframe | M5 | 5 minutos |
| Horario Rango | 21:50-22:15 NY | Período de consolidación |
| Stop Loss | 34 pips | 3.40 USD |
| Take Profit | 83 pips | 8.30 USD |
| Max Trades/Día | 1 | Límite de operaciones |
| Rango Mínimo | 5 pips | Filtro de validez |

---

## 📊 Ejemplos de Uso

### Ejemplo 1: Backtest Simple

```python
from ny_range_breakout_strategy import NYRangeBreakout
from backtest_engine import BacktestEngine
from config.settings import BacktestConfig

# Crear estrategia
strategy = NYRangeBreakout(
    stop_loss_pips=34.0,
    take_profit_pips=83.0
)

# Configurar backtest
config = BacktestConfig(
    initial_capital=10000.0,
    commission_pct=0.0001
)

# Ejecutar (asumiendo que tienes 'data' y 'symbol_info')
engine = BacktestEngine(config)
result = engine.run(strategy, data, symbol_info)

print(result.summary())
```

### Ejemplo 2: Optimización ML

```python
from ml_optimizer import MLStrategyOptimizer
from ny_range_breakout_strategy import NYRangeBreakout

# Crear optimizador
optimizer = MLStrategyOptimizer(
    strategy_class=NYRangeBreakout,
    data=data,
    symbol_info=symbol_info,
    target_metric='sharpe_ratio',
    n_iterations=50
)

# Optimizar
result = optimizer.bayesian_optimization()

# Ver mejores parámetros
print("Mejores parámetros:")
for param, value in result.best_params.items():
    print(f"  {param}: {value}")
```

### Ejemplo 3: Walk-Forward Analysis

```python
from ml_optimizer import MLStrategyOptimizer

optimizer = MLStrategyOptimizer(
    strategy_class=NYRangeBreakout,
    data=data,  # 2+ años de datos
    symbol_info=symbol_info,
    target_metric='sharpe_ratio'
)

# Walk-Forward
wf_result = optimizer.walk_forward_optimization(
    train_period_months=3,
    test_period_months=1,
    step_months=1
)

print(f"Sharpe promedio: {wf_result['avg_test_score']:.4f}")
print(f"Consistencia: {wf_result['consistency']:.2%}")
```

---

## 🔧 Integración con el Proyecto

### Estructura Recomendada

```
strategy_backtest/
├── strategies/
│   ├── __init__.py
│   ├── base_strategy.py
│   ├── moving_average_crossover.py
│   └── ny_range_breakout_strategy.py  ← Copiar aquí
│
├── run_ny_range_backtest.py           ← Copiar aquí
├── ejemplo_simple.py                  ← Copiar aquí
├── data_manager.py
├── backtest_engine.py
├── ml_optimizer.py
└── ...
```

### Importar la Estrategia

```python
# Desde cualquier script en el proyecto
from strategies.ny_range_breakout_strategy import NYRangeBreakout

# O si está en la raíz
from ny_range_breakout_strategy import NYRangeBreakout
```

---

## 📈 Métricas de Rendimiento

El sistema genera múltiples métricas para evaluar la estrategia:

### Métricas de Retorno
- ✅ Total Return %
- ✅ Annual Return %
- ✅ CAGR
- ✅ Total Profit/Loss

### Métricas de Riesgo
- ✅ Max Drawdown
- ✅ Sharpe Ratio
- ✅ Sortino Ratio
- ✅ Calmar Ratio
- ✅ Value at Risk (VaR)

### Métricas de Trades
- ✅ Total Trades
- ✅ Win Rate
- ✅ Profit Factor
- ✅ Expectancy
- ✅ Avg Win / Avg Loss
- ✅ Best / Worst Trade

### Análisis Temporal
- ✅ Rendimiento por mes
- ✅ Rendimiento por día de la semana
- ✅ Rendimiento por hora del día

---

## 🎨 Reportes Generados

Los scripts generan reportes HTML interactivos:

### 1. Reporte Principal (`ny_range_backtest_report.html`)
- Resumen ejecutivo
- Tabla de métricas
- Lista detallada de trades
- Estadísticas de rachas

### 2. Gráficos (`ny_range_backtest_charts.html`)
- Equity curve (curva de capital)
- Drawdown chart
- Distribución de P&L
- Price chart con señales
- Análisis temporal (heatmaps)
- Gráficos de riesgo

### 3. Optimización (`ny_range_optimization_results.csv`)
- Todas las combinaciones probadas
- Scores de cada iteración
- Historia de optimización

---

## ⚙️ Personalización

### Ajustar Parámetros

```python
# Estrategia conservadora
conservative = NYRangeBreakout(
    stop_loss_pips=25,      # SL más ajustado
    take_profit_pips=100,   # TP más lejano
    min_range_pips=8        # Solo rangos grandes
)

# Estrategia agresiva
aggressive = NYRangeBreakout(
    stop_loss_pips=40,      # SL más amplio
    take_profit_pips=70,    # TP más cercano
    min_range_pips=3,       # Rangos pequeños OK
    max_trades_per_day=2    # 2 trades permitidos
)
```

### Cambiar Horario del Rango

```python
# Rango más temprano
early_range = NYRangeBreakout(
    range_start_hour=21,
    range_start_minute=30,   # 21:30 inicio
    range_end_hour=22,
    range_end_minute=0       # 22:00 fin
)

# Rango más largo
longer_range = NYRangeBreakout(
    range_start_hour=21,
    range_start_minute=45,
    range_end_hour=22,
    range_end_minute=30      # 45 minutos de rango
)
```

### Añadir Filtros Personalizados

```python
class NYRangeCustom(NYRangeBreakout):
    """Versión personalizada con filtros adicionales"""
    
    def generate_signals(self, data):
        signals = super().generate_signals(data)
        
        # Filtrar por volatilidad, volumen, etc.
        filtered = []
        for signal in signals:
            if signal.metadata['range_pips'] > 10:  # Ejemplo
                filtered.append(signal)
        
        return filtered
```

---

## 🛠️ Requisitos Técnicos

### Dependencias Python

```
pandas>=2.1.4          # Manipulación de datos
numpy>=1.26.2          # Operaciones numéricas
pytz>=2023.3           # Manejo de zonas horarias
plotly>=5.18.0         # Gráficos interactivos
scikit-learn>=1.3.2    # Machine Learning
scipy>=1.11.4          # Optimización científica
```

### Opcional (para datos reales)

```
MetaTrader5>=5.0.4518  # Conexión con MT5
```

### Instalación

```bash
pip install pandas numpy pytz plotly scikit-learn scipy
```

---

## 📚 Documentación Adicional

### Archivos Incluidos

- **`GUIA_NY_RANGE_BREAKOUT.md`**: Guía completa con todo el detalle
  - Descripción exhaustiva
  - Instrucciones paso a paso
  - Troubleshooting
  - FAQs
  - Mejores prácticas

### Documentación del Proyecto Base

- `README.md`: Documentación del sistema completo
- `QUICKSTART.md`: Inicio rápido
- `BEST_PRACTICES.md`: Mejores prácticas generales
- `INSTALLATION.md`: Guía de instalación

---

## 🎓 Flujo de Trabajo Recomendado

### Para Principiantes

```
1. Ejecutar ejemplo_simple.py
   ↓
2. Entender las señales generadas
   ↓
3. Ejecutar backtest simple (opción 1)
   ↓
4. Revisar reportes HTML
   ↓
5. Experimentar con parámetros
```

### Para Usuarios Avanzados

```
1. Backtest con datos de muestra
   ↓
2. Optimización ML (encontrar mejores parámetros)
   ↓
3. Validar con Walk-Forward Analysis
   ↓
4. Backtest con datos MT5 reales
   ↓
5. Ajuste fino de parámetros
   ↓
6. Pruebas en cuenta demo
```

---

## 🔍 Preguntas Frecuentes

### ¿Necesito MetaTrader 5?

**No es obligatorio.** Puedes usar datos de muestra generados sintéticamente. MT5 solo es necesario si quieres usar datos históricos reales.

### ¿En qué timeframe funciona?

Diseñada para **M5 (5 minutos)**, pero puedes experimentar con:
- M1 (1 minuto): Más granular
- M15 (15 minutos): Más suave

### ¿Funciona 24/7?

No. La estrategia solo busca señales después del período de rango NY (después de 22:15 hora NY). Típicamente genera 0-1 señales por día.

### ¿Puedo usar en otros símbolos?

Está optimizada para XAUUSD, pero puedes adaptarla ajustando `pip_value` para otros símbolos.

### ¿Cuántos datos necesito?

- **Mínimo**: 3-6 meses
- **Recomendado**: 1 año
- **Óptimo (para WF)**: 2+ años

---

## ⚠️ Advertencias Importantes

### Riesgos del Trading

- 📛 El trading conlleva riesgo significativo de pérdida
- 📛 Resultados pasados NO garantizan rendimiento futuro
- 📛 Nunca operes con dinero que no puedas perder
- 📛 Este sistema es EDUCACIONAL, no asesoría financiera
- 📛 Prueba extensivamente en demo antes de usar dinero real

### Limitaciones del Backtesting

- ⚠️ No captura todos los aspectos del mercado real
- ⚠️ Puede haber diferencias en slippage/comisiones
- ⚠️ No considera eventos de mercado extremos
- ⚠️ Requiere validación con datos out-of-sample

---

## ✅ Checklist de Implementación

Antes de usar la estrategia:

- [ ] Archivos copiados al proyecto
- [ ] Dependencias instaladas
- [ ] Ejemplo simple ejecutado exitosamente
- [ ] Backtest simple completado
- [ ] Reportes HTML revisados
- [ ] Parámetros personalizados probados
- [ ] Optimización ML ejecutada
- [ ] Walk-Forward realizado
- [ ] Resultados documentados
- [ ] Validación en múltiples períodos
- [ ] Pruebas en cuenta demo (si vas a trading real)

---

## 📞 Soporte

### Documentación
- Lee `GUIA_NY_RANGE_BREAKOUT.md` para información detallada
- Consulta los archivos del proyecto base (README.md, BEST_PRACTICES.md)

### Recursos
- [Documentación MT5 Python](https://www.mql5.com/en/docs/python_metatrader5)
- [Pandas Docs](https://pandas.pydata.org/docs/)
- [Scikit-learn](https://scikit-learn.org/)

---

## 🎉 ¡A Trabajar!

```bash
# Opción rápida
python ejemplo_simple.py

# Opción completa
python run_ny_range_backtest.py
```

**¡Feliz backtesting y que tengas éxito en tu análisis! 📈🚀**

---

*Creado para el proyecto Strategy Backtest System*  
*Versión: 1.0.0*  
*Fecha: 2024*
