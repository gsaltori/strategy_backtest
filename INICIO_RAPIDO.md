# ⚡ INICIO RÁPIDO - Estrategia ML de Trading

## 🚀 Configuración en 5 Minutos

### Paso 1: Instalar Dependencias (2 min)

```bash
# Core ML (OBLIGATORIO)
pip install scikit-learn numpy pandas scipy

# ML Avanzado (RECOMENDADO para mejor rendimiento)
pip install xgboost lightgbm

# Visualización
pip install plotly
```

### Paso 2: Copiar Archivos a tu Proyecto (1 min)

```
tu_proyecto/
├── strategies/
│   └── ml_advanced_strategy.py          ← COPIAR
│
├── ml_strategy_gui_integration.py       ← COPIAR
├── run_ml_strategy.py                   ← COPIAR
└── docs/
    ├── GUIA_ML_STRATEGY.md              ← COPIAR (opcional)
    └── README_ML_STRATEGY.md            ← COPIAR (opcional)
```

### Paso 3: Primera Ejecución (2 min)

```bash
# Ejecutar script de prueba
python run_ml_strategy.py

# En el menú, selecciona:
# [1] Backtest Simple
```

**¡Eso es todo!** Ya tienes la estrategia ML funcionando. 🎉

---

## 📋 Ejemplo de Uso Básico

```python
from strategies.ml_advanced_strategy import MLAdvancedStrategy
from backtest_engine import BacktestEngine
from config.settings import BacktestConfig

# 1. Crear estrategia (usa valores por defecto)
strategy = MLAdvancedStrategy()

# 2. Configurar backtest
config = BacktestConfig(
    initial_capital=10000.0,
    commission_pct=0.0001
)

# 3. Ejecutar (asumiendo que ya tienes 'data' y 'symbol_info')
engine = BacktestEngine(config)
result = engine.run(strategy, data, symbol_info)

# 4. Ver resultados
print(result.summary())
```

---

## 🎨 Integración con GUI

```python
# En tu archivo gui_backtest.py

from ml_strategy_gui_integration import integrate_ml_strategy_to_gui

# Dentro de tu clase GUI, después de crear el notebook:
class BacktestGUI:
    def __init__(self, root):
        # ... tu código existente ...
        
        # Agregar pestaña de ML Strategy
        self.ml_integration = integrate_ml_strategy_to_gui(self.notebook)
```

---

## ⚙️ Configuraciones Rápidas

### 🟢 Conservadora (Bajo Riesgo)
```python
strategy = MLAdvancedStrategy(
    prediction_threshold=0.70,
    risk_per_trade=0.01,
    max_positions=2
)
```

### 🟡 Balanceada (Recomendada)
```python
strategy = MLAdvancedStrategy()  # Usa defaults
```

### 🔴 Agresiva (Alto Riesgo)
```python
strategy = MLAdvancedStrategy(
    prediction_threshold=0.50,
    risk_per_trade=0.03,
    max_positions=5
)
```

---

## 📊 Menú del Script Interactivo

Cuando ejecutes `python run_ml_strategy.py`:

```
1. Backtest Simple
   → Prueba rápida con datos de muestra
   
2. Comparación de Estrategias
   → Compara 3 configuraciones diferentes
   
3. Análisis de Feature Importance
   → Ve qué features son más importantes
   
4. Backtest Completo
   → Ejecuta todo: backtest + comparación + análisis
```

---

## 🔧 Verificar Instalación

```bash
# Test 1: Verificar imports
python -c "from strategies.ml_advanced_strategy import MLAdvancedStrategy; print('✅ Estrategia OK')"

# Test 2: Verificar ML libraries
python -c "import sklearn; import xgboost; import lightgbm; print('✅ ML OK')"

# Test 3: Ejecutar backtest de prueba
python run_ml_strategy.py
```

---

## ❓ Problemas Comunes

### Error: "No module named 'xgboost'"
```bash
# Solución:
pip install xgboost lightgbm
```

### Error: "Insuficientes muestras para entrenar"
```python
# Solución: Usar más datos o reducir min_train_samples
strategy = MLAdvancedStrategy(min_train_samples=200)
```

### Pocas señales generadas
```python
# Solución: Reducir threshold
strategy = MLAdvancedStrategy(prediction_threshold=0.50)
```

---

## 📚 Documentación

- **Inicio Rápido**: Este archivo
- **README Completo**: `README_ML_STRATEGY.md`
- **Guía Detallada**: `GUIA_ML_STRATEGY.md` (2000+ líneas)
- **Código Comentado**: Todos los archivos .py

---

## 🎯 Próximos Pasos Recomendados

1. ✅ Ejecutar `run_ml_strategy.py` (opción 1)
2. 📊 Revisar resultados generados
3. 🎨 Integrar con tu GUI
4. ⚙️ Experimentar con parámetros
5. 📚 Leer documentación completa
6. 🚀 Optimizar para tu caso de uso

---

## 💡 Tips Rápidos

- **Mínimo de datos**: 500 barras (1 año recomendado)
- **Threshold óptimo**: 0.55 - 0.60
- **Riesgo recomendado**: 1-2% por trade
- **Reentrenar cada**: 100-200 barras
- **Modelos**: Se entrenan automáticamente

---

## 🆘 ¿Necesitas Ayuda?

1. **Primero**: Lee `RESUMEN_EJECUTIVO.md`
2. **Luego**: Consulta `GUIA_ML_STRATEGY.md`
3. **Problema específico**: Busca en sección Troubleshooting
4. **Ejemplos**: Revisa `run_ml_strategy.py`

---

<div align="center">

## ✨ ¡Listo para Empezar! ✨

**Ejecuta**: `python run_ml_strategy.py`

**Y elige opción**: `1` (Backtest Simple)

---

**¡Feliz Trading con ML! 🚀📈**

</div>
