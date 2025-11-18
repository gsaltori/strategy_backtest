# 🤖 Guía Completa: Estrategia de Trading con Machine Learning Avanzado

## 📋 Tabla de Contenidos

1. [Introducción](#introducción)
2. [Características Principales](#características-principales)
3. [Instalación y Requisitos](#instalación-y-requisitos)
4. [Uso Básico](#uso-básico)
5. [Parámetros y Configuración](#parámetros-y-configuración)
6. [Características Técnicas ML](#características-técnicas-ml)
7. [Integración con GUI](#integración-con-gui)
8. [Optimización y Mejores Prácticas](#optimización-y-mejores-prácticas)
9. [Troubleshooting](#troubleshooting)
10. [Ejemplos Avanzados](#ejemplos-avanzados)

---

## 🎯 Introducción

La **MLAdvancedStrategy** es una estrategia de trading profesional que utiliza Machine Learning de última generación para predecir movimientos de mercado y gestionar el riesgo de manera dinámica.

### ¿Qué la hace especial?

- 🧠 **Ensemble de modelos ML**: Random Forest, XGBoost y LightGBM
- 📊 **50+ features ingenieriles**: Price, volume, volatility y patterns
- 🎯 **Predicción dual**: Dirección del precio Y volatilidad futura
- 🛡️ **Gestión dinámica de riesgo**: Stops adaptativos basados en ML
- 🔄 **Auto-reentrenamiento**: Se adapta a condiciones cambiantes
- 🌡️ **Detección de regímenes**: Identifica mercados trending vs ranging

---

## 🌟 Características Principales

### 1. **Ensemble de Modelos ML**

La estrategia combina múltiples algoritmos:

```python
- Random Forest: Siempre disponible, robusto
- XGBoost: Opcional, alta precisión
- LightGBM: Opcional, muy rápido
```

**Votación por mayoría**: Las predicciones se combinan para mayor confiabilidad.

### 2. **Features Ingenieriles (50+)**

#### Price Features
- Retornos en múltiples timeframes (1, 3, 5, 10, 20 periodos)
- Medias móviles (SMA, EMA) en 5, 10, 20, 50, 100, 200 periodos
- RSI en múltiples periodos (7, 14, 21)
- MACD completo (línea, señal, histograma)
- Bollinger Bands y posición relativa

#### Volatility Features
- ATR en múltiples periodos
- Volatilidad realizada (rolling)
- True Range normalizado
- Rango alto-bajo relativo

#### Volume Features
- Volumen relativo vs promedio
- OBV (On-Balance Volume)
- Volume-Price Trend

#### Pattern Features
- Velas japonesas (doji, engulfing)
- Secuencias alcistas/bajistas
- Body vs shadows ratios

#### Market Regime Features
- Trend strength
- Regime volatility
- Autocorrelación (mean reversion vs momentum)

### 3. **Predicción Dual**

```
┌─────────────────────────────────────┐
│   MODELO DE DIRECCIÓN               │
│   Input: 50+ features               │
│   Output: BUY / SELL / NEUTRAL      │
│   Confidence: 0-1                   │
└─────────────────────────────────────┘
              │
              ▼
┌─────────────────────────────────────┐
│   MODELO DE VOLATILIDAD             │
│   Input: 50+ features               │
│   Output: Volatilidad futura        │
│   Uso: Ajustar stops dinámicamente  │
└─────────────────────────────────────┘
```

### 4. **Gestión Dinámica de Riesgo**

- **Stops adaptativos**: Se ajustan según volatilidad predicha
- **Position sizing**: Basado en riesgo por operación
- **Multi-posición**: Control de exposición total
- **R:R dinámico**: Take profit ajustado a condiciones

### 5. **Detección de Regímenes**

La estrategia identifica 4 tipos de mercado:

```python
'trending_up'    → Solo operaciones LONG
'trending_down'  → Solo operaciones SHORT
'ranging'        → Ambas direcciones (range trading)
'high_vol'       → No operar (protección)
```

---

## 🔧 Instalación y Requisitos

### Requisitos del Sistema

```bash
Python 3.8+
Memoria RAM: 8GB mínimo (16GB recomendado)
Espacio en disco: 500MB para datos y modelos
```

### Dependencias

```bash
# Core ML
scikit-learn>=1.3.0
numpy>=1.24.0
pandas>=2.0.0

# ML Opcional (para mejor rendimiento)
xgboost>=2.0.0        # Opcional pero recomendado
lightgbm>=4.0.0       # Opcional pero recomendado

# Trading y análisis
scipy>=1.11.0
plotly>=5.18.0
```

### Instalación

```bash
# 1. Instalar dependencias básicas
pip install scikit-learn numpy pandas scipy plotly

# 2. Instalar ML avanzado (recomendado)
pip install xgboost lightgbm

# 3. Verificar instalación
python -c "from strategies.ml_advanced_strategy import MLAdvancedStrategy; print('✅ OK')"
```

---

## 🚀 Uso Básico

### Ejemplo 1: Backtest Simple

```python
from strategies.ml_advanced_strategy import MLAdvancedStrategy
from backtest_engine import BacktestEngine
from config.settings import BacktestConfig
import pandas as pd

# 1. Cargar datos (ejemplo con datos sintéticos)
data = generate_sample_data(days=365)  # 1 año de datos

# 2. Crear estrategia con parámetros por defecto
strategy = MLAdvancedStrategy()

# 3. Configurar backtest
config = BacktestConfig(
    initial_capital=10000.0,
    commission_pct=0.0001,
    slippage_pct=0.0005
)

symbol_info = {
    'point': 0.01,
    'digits': 2,
    'trade_contract_size': 100.0
}

# 4. Ejecutar backtest
engine = BacktestEngine(config)
result = engine.run(strategy, data, symbol_info)

# 5. Ver resultados
print(result.summary())
```

### Ejemplo 2: Usando el Script de Ejecución

```bash
# Ejecutar el script interactivo
python run_ml_strategy.py

# Menú de opciones:
# 1. Backtest Simple
# 2. Comparación de Estrategias
# 3. Análisis de Feature Importance
# 4. Backtest Completo con Reportes
```

### Ejemplo 3: Desde la GUI

```python
# 1. Abrir la GUI de backtesting
python gui_backtest.py

# 2. Ir a la pestaña "🤖 ML Strategy"

# 3. Configurar parámetros:
#    - Lookback Period: 60
#    - Prediction Threshold: 0.55
#    - Risk per Trade: 2%

# 4. Cargar datos y ejecutar backtest
```

---

## ⚙️ Parámetros y Configuración

### Parámetros de ML

| Parámetro | Descripción | Rango | Default |
|-----------|-------------|-------|---------|
| `lookback_period` | Ventana de observación para features | 20-200 | 60 |
| `min_train_samples` | Mínimo de muestras para entrenar | 200-2000 | 500 |
| `retrain_frequency` | Reentrenar cada N barras | 50-500 | 100 |
| `prediction_threshold` | Confianza mínima para operar | 0.5-0.95 | 0.55 |

**Recomendaciones:**
- **Mercados volátiles**: Aumentar `lookback_period` a 80-100
- **Datos limitados**: Reducir `min_train_samples` a 300
- **Adaptación rápida**: Reducir `retrain_frequency` a 50-75
- **Mayor precisión**: Aumentar `prediction_threshold` a 0.65-0.70

### Parámetros de Features

| Parámetro | Descripción | Default |
|-----------|-------------|---------|
| `use_price_features` | Usar features de precio | True |
| `use_volume_features` | Usar features de volumen | True |
| `use_volatility_features` | Usar features de volatilidad | True |
| `use_pattern_features` | Usar features de patrones | True |

**Nota**: Se recomienda usar todas las features para mejor rendimiento.

### Parámetros de Gestión de Riesgo

| Parámetro | Descripción | Rango | Default |
|-----------|-------------|-------|---------|
| `risk_per_trade` | Riesgo por operación (% capital) | 0.01-0.10 | 0.02 |
| `max_positions` | Máximo de posiciones simultáneas | 1-10 | 3 |
| `use_dynamic_stops` | Usar stops dinámicos ML | True/False | True |
| `atr_multiplier` | Multiplicador de ATR para SL/TP | 1.0-5.0 | 2.0 |

**Configuraciones Recomendadas:**

```python
# Configuración CONSERVADORA
strategy = MLAdvancedStrategy(
    prediction_threshold=0.70,
    risk_per_trade=0.01,
    max_positions=2,
    atr_multiplier=2.5
)

# Configuración BALANCEADA (default)
strategy = MLAdvancedStrategy(
    prediction_threshold=0.55,
    risk_per_trade=0.02,
    max_positions=3,
    atr_multiplier=2.0
)

# Configuración AGRESIVA
strategy = MLAdvancedStrategy(
    prediction_threshold=0.50,
    risk_per_trade=0.03,
    max_positions=5,
    atr_multiplier=1.5
)
```

### Parámetros de Filtros

| Parámetro | Descripción | Uso |
|-----------|-------------|-----|
| `min_volatility` | Volatilidad mínima para operar | Evitar mercados muy tranquilos |
| `max_volatility` | Volatilidad máxima para operar | Evitar mercados muy caóticos |
| `min_volume_ratio` | Ratio de volumen mínimo | Asegurar liquidez |
| `detect_regime` | Activar detección de régimen | Filtrar por tendencia |
| `regime_window` | Ventana para análisis de régimen | Sensibilidad a cambios |

---

## 🧠 Características Técnicas ML

### Arquitectura del Sistema

```
DATA INPUT (OHLCV)
       │
       ▼
FEATURE ENGINEERING
   ├─ Price Features (20+)
   ├─ Volatility Features (10+)
   ├─ Volume Features (5+)
   ├─ Pattern Features (10+)
   └─ Regime Features (5+)
       │
       ▼
PREPROCESSING
   ├─ Handle NaN values
   ├─ StandardScaler normalization
   └─ Feature selection
       │
       ▼
MODEL ENSEMBLE
   ├─ Random Forest (100 trees)
   ├─ XGBoost (100 estimators)
   └─ LightGBM (100 estimators)
       │
       ▼
PREDICTION
   ├─ Direction: BUY/SELL/NEUTRAL
   ├─ Confidence: 0-1
   └─ Volatility: Future std dev
       │
       ▼
FILTERING
   ├─ Confidence threshold
   ├─ Volatility range
   ├─ Volume filter
   └─ Regime filter
       │
       ▼
RISK MANAGEMENT
   ├─ Dynamic position sizing
   ├─ Adaptive stops (ML-based)
   └─ R:R optimization
       │
       ▼
SIGNAL OUTPUT
```

### Proceso de Entrenamiento

1. **Preparación de datos**
   - Calcular 50+ features
   - Crear targets (dirección y volatilidad futura)
   - Limpiar NaN y outliers

2. **Split temporal**
   - Training: 70% de datos más antiguos
   - No se usa validación cruzada tradicional
   - Walk-forward approach

3. **Entrenamiento de modelos**
   ```python
   # Random Forest
   - n_estimators: 100
   - max_depth: 10
   - min_samples_split: 20
   - min_samples_leaf: 10
   
   # XGBoost (si disponible)
   - n_estimators: 100
   - max_depth: 6
   - learning_rate: 0.1
   
   # LightGBM (si disponible)
   - n_estimators: 100
   - max_depth: 6
   - learning_rate: 0.1
   ```

4. **Validación**
   - Verificar suficientes muestras (>500)
   - Comprobar balanceo de clases
   - Validar no overfitting

5. **Predicción en vivo**
   - Escalar features con scaler entrenado
   - Obtener predicciones de todos los modelos
   - Votación por mayoría
   - Calcular confianza promedio

### Reentrenamiento Automático

```python
# El modelo se reentrena cada 'retrain_frequency' barras

# Ejemplo con retrain_frequency=100:
Bar 1-99:    Predicciones con modelo inicial
Bar 100:     REENTRENAR con datos 1-100
Bar 101-199: Predicciones con modelo actualizado
Bar 200:     REENTRENAR con datos 1-200
...y así sucesivamente
```

**Ventajas:**
- ✅ Adaptación a cambios de mercado
- ✅ Incorpora información más reciente
- ✅ Mantiene modelo actualizado

**Consideraciones:**
- ⚠️ Puede aumentar tiempo de ejecución
- ⚠️ Necesita suficientes datos históricos
- ⚠️ Requiere validación anti-overfitting

---

## 🖥️ Integración con GUI

La estrategia ML incluye una interfaz gráfica completa que se integra con la GUI de backtesting existente.

### Componentes de la GUI

```
┌─────────────────────────────────────────────┐
│  🤖 ML STRATEGY TAB                         │
├─────────────────────────────────────────────┤
│                                             │
│  📊 Parámetros de ML                        │
│  ├─ Lookback Period: [60]                   │
│  ├─ Prediction Threshold: [0.55]            │
│  ├─ Retrain Frequency: [100]                │
│  └─ Min Train Samples: [500]                │
│                                             │
│  ✅ Features a Utilizar                     │
│  [✓] Price Features                         │
│  [✓] Volume Features                        │
│  [✓] Volatility Features                    │
│  [✓] Pattern Features                       │
│                                             │
│  🛡️ Gestión de Riesgo                       │
│  ├─ Risk per Trade: [2%]                    │
│  ├─ Max Positions: [3]                      │
│  ├─ ATR Multiplier: [2.0]                   │
│  └─ [✓] Use Dynamic Stops                   │
│                                             │
│  🔍 Filtros de Trading                      │
│  ├─ Min Volatility: [0.0005]                │
│  ├─ Max Volatility: [0.05]                  │
│  ├─ Min Volume Ratio: [0.5]                 │
│  └─ [✓] Detect Regime                       │
│                                             │
│  📈 Estado del Modelo                       │
│  ├─ Estado: ✅ Entrenado                    │
│  ├─ Precisión: 67.3%                        │
│  ├─ Régimen Actual: Trending Up             │
│  └─ Predicciones: 42                        │
│                                             │
│  [💾 Guardar Config] [📂 Cargar] [🔄 Reset] │
└─────────────────────────────────────────────┘
```

### Uso de la GUI

```python
# En tu aplicación principal de GUI:

import tkinter as tk
from tkinter import ttk
from ml_strategy_gui_integration import integrate_ml_strategy_to_gui

# Crear ventana principal
root = tk.Tk()
root.title("Trading Backtest System")

# Crear notebook
notebook = ttk.Notebook(root)
notebook.pack(fill='both', expand=True)

# Integrar estrategia ML
ml_integration = integrate_ml_strategy_to_gui(notebook)

# ... resto de tu aplicación ...

root.mainloop()
```

### Funciones de la GUI

1. **Configuración de Parámetros**
   - Interfaz intuitiva con spinboxes y checkboxes
   - Valores por defecto sensatos
   - Validación de rangos

2. **Guardar/Cargar Configuración**
   ```python
   # Los parámetros se guardan en JSON
   {
       "lookback_period": 60,
       "prediction_threshold": 0.55,
       "risk_per_trade": 0.02,
       ...
   }
   ```

3. **Monitoreo en Tiempo Real**
   - Estado de entrenamiento
   - Precisión del modelo
   - Régimen actual del mercado
   - Contador de predicciones

4. **Validación Automática**
   - Verifica rangos válidos
   - Detecta configuraciones inválidas
   - Muestra mensajes de error claros

---

## 🎯 Optimización y Mejores Prácticas

### 1. Optimización de Parámetros

#### Grid Search Manual

```python
# Probar diferentes configuraciones
configs = [
    {'prediction_threshold': 0.50, 'risk_per_trade': 0.01},
    {'prediction_threshold': 0.55, 'risk_per_trade': 0.02},
    {'prediction_threshold': 0.60, 'risk_per_trade': 0.02},
    {'prediction_threshold': 0.65, 'risk_per_trade': 0.03},
]

results = []
for config in configs:
    strategy = MLAdvancedStrategy(**config)
    result = engine.run(strategy, data, symbol_info)
    results.append({
        'config': config,
        'sharpe': result.get_performance_metrics()['sharpe_ratio'],
        'return': result.total_return
    })

# Encontrar mejor configuración
best = max(results, key=lambda x: x['sharpe'])
print(f"Mejor config: {best['config']}")
```

#### Walk-Forward Optimization

```python
from ml_optimizer import MLStrategyOptimizer

# Crear optimizador
optimizer = MLStrategyOptimizer(
    strategy_class=MLAdvancedStrategy,
    data=data,
    symbol_info=symbol_info,
    target_metric='sharpe_ratio',
    n_iterations=50
)

# Ejecutar optimización bayesiana
result = optimizer.bayesian_optimization()

print(f"Mejores parámetros: {result.best_params}")
print(f"Mejor Sharpe: {result.best_score}")
```

### 2. Mejores Prácticas

#### Entrenamiento

✅ **DO:**
- Usar al menos 500 barras de datos
- Reentrenar periódicamente (cada 100-200 barras)
- Validar en datos out-of-sample
- Monitorear accuracy del modelo

❌ **DON'T:**
- Entrenar con menos de 200 muestras
- Usar threshold muy bajo (<0.50)
- Ignorar el régimen de mercado
- Operar sin suficientes datos históricos

#### Gestión de Riesgo

✅ **DO:**
- Limitar riesgo a 1-3% por operación
- Usar stops dinámicos basados en volatilidad
- Controlar número máximo de posiciones
- Revisar drawdown regularmente

❌ **DON'T:**
- Arriesgar más del 5% por trade
- Usar stops fijos en mercados volátiles
- Permitir exposición ilimitada
- Ignorar correlación entre posiciones

#### Features

✅ **DO:**
- Usar todas las categorías de features
- Verificar importancia de features
- Eliminar features redundantes
- Normalizar/escalar features

❌ **DON'T:**
- Usar solo price features
- Incluir features con muchos NaN
- Ignorar features de volumen
- Olvidar feature engineering

### 3. Monitoreo de Rendimiento

```python
# Métricas clave a monitorear:

1. Accuracy del modelo (>60% es bueno)
2. Win rate de trades (>50% es bueno)
3. Sharpe ratio (>1.5 es excelente)
4. Max drawdown (<20% es aceptable)
5. Profit factor (>1.5 es bueno)
6. Frecuencia de reentrenamiento
7. Distribución de predicciones
8. Régimen de mercado predominante
```

### 4. Detección de Overfitting

```python
# Señales de overfitting:

❌ Accuracy en training > 90%
❌ Accuracy en testing < 55%
❌ Diferencia train-test > 20%
❌ Muchos parámetros vs pocos datos
❌ Performance deteriora out-of-sample

# Soluciones:

✅ Aumentar min_samples_leaf
✅ Reducir max_depth de árboles
✅ Usar más datos de entrenamiento
✅ Aumentar prediction_threshold
✅ Simplificar modelo
```

---

## 🔧 Troubleshooting

### Problema 1: "Insuficientes muestras para entrenar"

**Síntoma:**
```
WARNING: Insuficientes muestras para entrenar: 250
```

**Solución:**
```python
# Opción 1: Reducir min_train_samples
strategy = MLAdvancedStrategy(
    min_train_samples=200  # Reducir de 500 a 200
)

# Opción 2: Cargar más datos históricos
data = load_data(days=730)  # 2 años en lugar de 1
```

### Problema 2: "XGBoost no disponible"

**Síntoma:**
```
WARNING: XGBoost no disponible. Se usará solo Random Forest.
```

**Solución:**
```bash
# Instalar XGBoost
pip install xgboost

# Si falla, instalar con conda
conda install -c conda-forge xgboost
```

### Problema 3: Modelo no genera señales

**Síntoma:**
```
Total de señales generadas: 0
```

**Posibles causas y soluciones:**

1. **Threshold muy alto**
   ```python
   # Reducir prediction_threshold
   strategy = MLAdvancedStrategy(
       prediction_threshold=0.50  # Más permisivo
   )
   ```

2. **Filtros muy estrictos**
   ```python
   # Relajar filtros
   strategy = MLAdvancedStrategy(
       min_volatility=0.0001,  # Reducir
       max_volatility=0.10,     # Aumentar
       min_volume_ratio=0.3     # Reducir
   )
   ```

3. **Régimen de mercado inadecuado**
   ```python
   # Desactivar detección de régimen
   strategy = MLAdvancedStrategy(
       detect_regime=False
   )
   ```

### Problema 4: Memory Error

**Síntoma:**
```
MemoryError: Unable to allocate array
```

**Solución:**
```python
# Reducir número de features
strategy = MLAdvancedStrategy(
    use_pattern_features=False,  # Desactivar algunos
    lookback_period=40           # Reducir ventana
)

# O reducir cantidad de datos
data = data.iloc[-5000:]  # Solo últimas 5000 barras
```

### Problema 5: Rendimiento muy lento

**Causas comunes:**

1. **Reentrenamiento muy frecuente**
   ```python
   # Aumentar retrain_frequency
   strategy = MLAdvancedStrategy(
       retrain_frequency=200  # En lugar de 100
   )
   ```

2. **Demasiados estimators**
   - Editar código fuente y reducir `n_estimators` de 100 a 50

3. **Demasiados datos**
   ```python
   # Usar datos más recientes
   data = data.iloc[-10000:]
   ```

---

## 🚀 Ejemplos Avanzados

### Ejemplo 1: Backtest Multi-Símbolo

```python
symbols = ['XAUUSD', 'EURUSD', 'GBPUSD']
results = {}

for symbol in symbols:
    print(f"\n=== Backtesting {symbol} ===")
    
    # Cargar datos del símbolo
    data = load_symbol_data(symbol)
    
    # Crear estrategia
    strategy = MLAdvancedStrategy()
    
    # Ejecutar backtest
    result = engine.run(strategy, data, symbol_info[symbol])
    results[symbol] = result
    
    print(result.summary())

# Comparar resultados
for symbol, result in results.items():
    print(f"{symbol}: Sharpe={result.sharpe:.2f}, Return={result.total_return*100:.1f}%")
```

### Ejemplo 2: Optimización de Hiperparámetros

```python
from sklearn.model_selection import ParameterGrid

# Definir grid de parámetros
param_grid = {
    'prediction_threshold': [0.50, 0.55, 0.60, 0.65],
    'risk_per_trade': [0.01, 0.02, 0.03],
    'atr_multiplier': [1.5, 2.0, 2.5]
}

# Generar todas las combinaciones
grid = ParameterGrid(param_grid)

best_result = None
best_params = None
best_sharpe = -999

for params in grid:
    # Crear y probar estrategia
    strategy = MLAdvancedStrategy(**params)
    result = engine.run(strategy, data, symbol_info)
    
    sharpe = result.get_performance_metrics()['sharpe_ratio']
    
    if sharpe > best_sharpe:
        best_sharpe = sharpe
        best_params = params
        best_result = result
    
    print(f"Params: {params} → Sharpe: {sharpe:.3f}")

print(f"\n🏆 Mejores parámetros:")
print(f"Sharpe: {best_sharpe:.3f}")
print(f"Params: {best_params}")
```

### Ejemplo 3: Análisis de Features en Profundidad

```python
# Entrenar modelo
strategy = MLAdvancedStrategy()
data_with_indicators = strategy.calculate_indicators(data)
strategy.train_models(data_with_indicators)

# Obtener importancia de features
X, feature_names = strategy._create_feature_matrix(data_with_indicators)

# Analizar cada modelo
for model_name, model in strategy.direction_model:
    if hasattr(model, 'feature_importances_'):
        importance = model.feature_importances_
        
        # Top 10 features
        top_indices = importance.argsort()[-10:][::-1]
        
        print(f"\n{model_name} - Top 10 Features:")
        for i in top_indices:
            print(f"  {feature_names[i]}: {importance[i]:.4f}")

# Graficar importancia
import plotly.graph_objects as go

fig = go.Figure(data=[
    go.Bar(x=feature_names[:20], y=importance[:20])
])
fig.update_layout(title='Feature Importance', xaxis_tickangle=-45)
fig.show()
```

### Ejemplo 4: Estrategia Adaptativa por Régimen

```python
class AdaptiveMLStrategy(MLAdvancedStrategy):
    """
    Estrategia que ajusta parámetros según el régimen detectado
    """
    
    def generate_signals(self, data):
        # Detectar régimen
        regime = self.detect_market_regime(data)
        
        # Ajustar parámetros según régimen
        if regime == 'trending_up':
            self.prediction_threshold = 0.50  # Más agresivo
            self.risk_per_trade = 0.03
        elif regime == 'trending_down':
            self.prediction_threshold = 0.50
            self.risk_per_trade = 0.03
        elif regime == 'ranging':
            self.prediction_threshold = 0.60  # Más conservador
            self.risk_per_trade = 0.02
        else:  # high_vol
            self.prediction_threshold = 0.70  # Muy conservador
            self.risk_per_trade = 0.01
        
        # Generar señales normalmente
        return super().generate_signals(data)

# Usar estrategia adaptativa
strategy = AdaptiveMLStrategy()
result = engine.run(strategy, data, symbol_info)
```

### Ejemplo 5: Ensemble con Votación Ponderada

```python
# Modificar el método predict_direction para votación ponderada

def predict_direction_weighted(self, features):
    """Predicción con pesos según accuracy histórico"""
    
    # Pesos basados en performance (ejemplo)
    model_weights = {
        'rf': 0.4,
        'xgb': 0.35,
        'lgb': 0.25
    }
    
    predictions = []
    confidences = []
    
    for name, model in self.direction_model:
        pred = model.predict(features_scaled)[0]
        proba = model.predict_proba(features_scaled)[0]
        conf = max(proba)
        
        # Aplicar peso
        weight = model_weights.get(name, 0.33)
        predictions.append(pred * weight)
        confidences.append(conf * weight)
    
    # Predicción final ponderada
    final_pred = int(np.sign(sum(predictions)))
    final_conf = sum(confidences)
    
    return final_pred, final_conf
```

---

## 📊 Métricas de Evaluación

### Métricas del Modelo ML

```python
# Accuracy: Porcentaje de predicciones correctas
accuracy = correct_predictions / total_predictions

# Precision: De las predicciones positivas, cuántas fueron correctas
precision = true_positives / (true_positives + false_positives)

# Recall: De los casos positivos reales, cuántos detectamos
recall = true_positives / (true_positives + false_negatives)

# F1-Score: Media armónica de precision y recall
f1 = 2 * (precision * recall) / (precision + recall)
```

### Métricas de Trading

```python
# Win Rate
win_rate = winning_trades / total_trades

# Profit Factor
profit_factor = gross_profit / gross_loss

# Sharpe Ratio
sharpe = (mean_return - risk_free_rate) / std_return

# Max Drawdown
max_dd = (peak_equity - trough_equity) / peak_equity

# Calmar Ratio
calmar = annual_return / max_drawdown
```

---

## 🎓 Conclusión

La **MLAdvancedStrategy** es una herramienta profesional de trading que combina:

✨ **Machine Learning de última generación**
📊 **Análisis técnico exhaustivo**
🛡️ **Gestión de riesgo inteligente**
🔄 **Adaptación continua al mercado**

### Próximos Pasos

1. ✅ Ejecutar backtests con datos históricos
2. 📊 Analizar métricas y feature importance
3. ⚙️ Optimizar parámetros para tu mercado
4. 🧪 Validar en cuenta demo
5. 📈 Monitorear rendimiento en vivo

### Recursos Adicionales

- 📚 Documentación de scikit-learn: https://scikit-learn.org
- 🔬 Papers sobre trading ML: Arxiv.org
- 💬 Comunidad de trading algorítmico
- 📖 Libros recomendados sobre trading cuantitativo

---

**⚠️ DISCLAIMER**: Esta estrategia es para fines educativos y de investigación. El trading conlleva riesgo de pérdida. Prueba extensivamente en demo antes de usar capital real. No es asesoría financiera.

---

**Versión**: 1.0.0  
**Última actualización**: 2024  
**Autor**: Sistema de Trading Avanzado  

¡Feliz trading! 🚀📈
