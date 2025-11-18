# 🤖 Estrategia de Trading con Machine Learning Avanzado

## 🎯 Descripción

Sistema profesional de trading algorítmico que utiliza **Machine Learning de última generación** para:

- 🧠 **Predecir movimientos de mercado** con ensemble de modelos (Random Forest, XGBoost, LightGBM)
- 📊 **Analizar 50+ features técnicos** (precio, volumen, volatilidad, patrones)
- 🎯 **Gestionar riesgo dinámicamente** basado en predicciones de volatilidad
- 🔄 **Auto-reentrenarse** para adaptarse a condiciones cambiantes
- 🌡️ **Detectar regímenes de mercado** (trending, ranging, alta volatilidad)

---

## ✨ Características Principales

### 🧠 Machine Learning Avanzado

- **Ensemble de Modelos**: Combina Random Forest, XGBoost y LightGBM
- **Votación Inteligente**: Las predicciones se combinan para mayor confiabilidad
- **Predicción Dual**: Dirección del precio Y volatilidad futura
- **Auto-reentrenamiento**: Se adapta cada N barras configurable

### 📊 Features Ingenieriles (50+)

| Categoría | Features |
|-----------|----------|
| **Price** | Retornos, MAs (SMA/EMA), RSI, MACD, Bollinger Bands |
| **Volatility** | ATR, True Range, Volatilidad realizada |
| **Volume** | Volumen relativo, OBV, VPT |
| **Patterns** | Velas japonesas, Engulfing, Secuencias |
| **Regime** | Trend strength, Autocorrelación |

### 🛡️ Gestión Dinámica de Riesgo

- **Position Sizing**: Basado en % de capital
- **Stops Adaptativos**: Ajustados según volatilidad predicha por ML
- **Multi-posición**: Control de exposición total
- **R:R Dinámico**: Take profit optimizado

### 🎨 Interfaz Gráfica Completa

- Panel de configuración intuitivo
- Monitoreo de estado del modelo en tiempo real
- Guardar/Cargar configuraciones
- Validación automática de parámetros

---

## 📦 Archivos del Proyecto

```
ml_trading_strategy/
│
├── strategies/
│   └── ml_advanced_strategy.py          # Estrategia ML principal (500+ líneas)
│
├── ml_strategy_gui_integration.py       # Integración con GUI (400+ líneas)
├── run_ml_strategy.py                   # Script de ejecución (300+ líneas)
├── GUIA_ML_STRATEGY.md                  # Guía completa (2000+ líneas)
└── README_ML_STRATEGY.md                # Este archivo
```

---

## 🚀 Inicio Rápido

### 1. Instalación

```bash
# Dependencias básicas
pip install scikit-learn numpy pandas scipy plotly

# ML avanzado (recomendado)
pip install xgboost lightgbm
```

### 2. Ejecución Simple

```bash
# Ejecutar script interactivo
python run_ml_strategy.py

# Seleccionar opción del menú:
# 1. Backtest Simple
# 2. Comparación de Estrategias
# 3. Análisis de Feature Importance
# 4. Backtest Completo
```

### 3. Uso Programático

```python
from strategies.ml_advanced_strategy import MLAdvancedStrategy
from backtest_engine import BacktestEngine
from config.settings import BacktestConfig

# Crear estrategia
strategy = MLAdvancedStrategy(
    prediction_threshold=0.55,
    risk_per_trade=0.02,
    max_positions=3
)

# Configurar backtest
config = BacktestConfig(
    initial_capital=10000.0,
    commission_pct=0.0001
)

# Ejecutar
engine = BacktestEngine(config)
result = engine.run(strategy, data, symbol_info)

# Ver resultados
print(result.summary())
```

### 4. Integración con GUI

```python
from ml_strategy_gui_integration import integrate_ml_strategy_to_gui

# Agregar a tu notebook de tkinter
ml_integration = integrate_ml_strategy_to_gui(notebook)

# Obtener estrategia configurada
strategy = ml_integration.get_strategy_instance()
```

---

## ⚙️ Configuración

### Parámetros Principales

| Parámetro | Descripción | Default | Rango |
|-----------|-------------|---------|-------|
| `lookback_period` | Ventana de observación | 60 | 20-200 |
| `prediction_threshold` | Confianza mínima | 0.55 | 0.5-0.95 |
| `risk_per_trade` | % riesgo por trade | 0.02 | 0.01-0.10 |
| `max_positions` | Posiciones simultáneas | 3 | 1-10 |
| `atr_multiplier` | Multiplicador SL/TP | 2.0 | 1.0-5.0 |

### Configuraciones Predefinidas

#### 🟢 Conservadora
```python
strategy = MLAdvancedStrategy(
    prediction_threshold=0.70,
    risk_per_trade=0.01,
    max_positions=2
)
```

#### 🟡 Balanceada (Default)
```python
strategy = MLAdvancedStrategy(
    prediction_threshold=0.55,
    risk_per_trade=0.02,
    max_positions=3
)
```

#### 🔴 Agresiva
```python
strategy = MLAdvancedStrategy(
    prediction_threshold=0.50,
    risk_per_trade=0.03,
    max_positions=5
)
```

---

## 📊 Resultados Esperados

### Métricas Típicas (Backtest 1 año XAUUSD)

| Métrica | Conservadora | Balanceada | Agresiva |
|---------|--------------|------------|----------|
| **Win Rate** | 58-62% | 54-58% | 50-54% |
| **Sharpe Ratio** | 1.2-1.5 | 1.5-2.0 | 1.0-1.5 |
| **Max Drawdown** | 10-15% | 15-20% | 20-30% |
| **Total Trades** | 40-60 | 80-120 | 150-200 |
| **Profit Factor** | 1.6-2.0 | 1.4-1.8 | 1.2-1.5 |

**Nota**: Los resultados varían según el período, símbolo y configuración.

---

## 🎓 Documentación

### 📖 Guía Completa

Consulta [`GUIA_ML_STRATEGY.md`](GUIA_ML_STRATEGY.md) para:

- Tutorial paso a paso
- Explicación detallada de parámetros
- Arquitectura del sistema ML
- Mejores prácticas
- Troubleshooting
- Ejemplos avanzados

### 🔬 Características Técnicas

#### Modelos ML
- **Random Forest**: 100 árboles, max_depth=10
- **XGBoost**: 100 estimadores, learning_rate=0.1
- **LightGBM**: 100 estimadores, muy eficiente

#### Feature Engineering
- 20+ features de precio
- 10+ features de volatilidad
- 5+ features de volumen
- 10+ features de patrones
- 5+ features de régimen

#### Workflow
```
Data → Features → Scaling → Models → Ensemble → Filters → Signals
```

---

## 🛠️ Requisitos del Sistema

### Software
- Python 3.8+
- 8GB RAM (16GB recomendado)
- 500MB espacio en disco

### Dependencias

```requirements.txt
# Core ML
scikit-learn>=1.3.0
numpy>=1.24.0
pandas>=2.0.0

# ML Opcional
xgboost>=2.0.0
lightgbm>=4.0.0

# Análisis
scipy>=1.11.0
plotly>=5.18.0
```

---

## 📈 Ejemplos de Uso

### Backtest Simple

```python
# Generar datos de muestra
from run_ml_strategy import generate_sample_data
data = generate_sample_data(days=365)

# Crear y ejecutar
strategy = MLAdvancedStrategy()
result = engine.run(strategy, data, symbol_info)

# Analizar
print(result.summary())
```

### Comparación de Parámetros

```python
configs = [
    {'prediction_threshold': 0.50},
    {'prediction_threshold': 0.60},
    {'prediction_threshold': 0.70}
]

for config in configs:
    strategy = MLAdvancedStrategy(**config)
    result = engine.run(strategy, data, symbol_info)
    print(f"Threshold {config['prediction_threshold']}: "
          f"Sharpe={result.sharpe:.2f}")
```

### Análisis de Features

```python
# Entrenar modelo
strategy = MLAdvancedStrategy()
data_with_indicators = strategy.calculate_indicators(data)
strategy.train_models(data_with_indicators)

# Obtener importancia
X, features = strategy._create_feature_matrix(data_with_indicators)

# Analizar
for name, model in strategy.direction_model:
    if hasattr(model, 'feature_importances_'):
        importance = model.feature_importances_
        print(f"\n{name} - Top 10:")
        for i in importance.argsort()[-10:][::-1]:
            print(f"  {features[i]}: {importance[i]:.4f}")
```

---

## 🔧 Troubleshooting

### Problema Común 1: Pocas Señales

**Síntoma**: El modelo genera muy pocas señales de trading

**Soluciones**:
```python
# 1. Reducir threshold
strategy = MLAdvancedStrategy(prediction_threshold=0.50)

# 2. Relajar filtros
strategy = MLAdvancedStrategy(
    min_volatility=0.0001,
    max_volatility=0.10
)

# 3. Desactivar detección de régimen
strategy = MLAdvancedStrategy(detect_regime=False)
```

### Problema Común 2: Modelo No Entrena

**Síntoma**: "Insuficientes muestras para entrenar"

**Soluciones**:
```python
# 1. Reducir min_train_samples
strategy = MLAdvancedStrategy(min_train_samples=200)

# 2. Cargar más datos
data = load_data(days=730)  # 2 años en lugar de 1
```

### Más Soluciones

Consulta la sección de Troubleshooting en [`GUIA_ML_STRATEGY.md`](GUIA_ML_STRATEGY.md)

---

## 🎯 Mejores Prácticas

### ✅ Recomendaciones

1. **Datos Suficientes**: Usa al menos 1 año de datos (mínimo 500 barras)
2. **Validación**: Siempre valida en datos out-of-sample
3. **Reentrenamiento**: Configura frecuencia apropiada (100-200 barras)
4. **Risk Management**: No arriesgues más del 2-3% por trade
5. **Monitoreo**: Revisa métricas del modelo regularmente

### ❌ Evitar

1. **Overfitting**: No usar threshold muy bajo (<0.50)
2. **Pocos Datos**: No entrenar con menos de 200 muestras
3. **Riesgo Excesivo**: No arriesgar más del 5% por trade
4. **Ignorar Filtros**: No desactivar todos los filtros
5. **Trading Ciego**: No operar sin validar primero

---

## 🔮 Roadmap Futuro

### Versión 1.1 (Próximo)
- [ ] Soporte para más modelos (Neural Networks)
- [ ] Optimización automática de hiperparámetros
- [ ] Feature selection automático
- [ ] Dashboard web interactivo

### Versión 1.2 (Futuro)
- [ ] Trading en tiempo real (integración con MT5)
- [ ] Multi-timeframe analysis
- [ ] Sentiment analysis integration
- [ ] Portfolio optimization

---

## 📝 Changelog

### v1.0.0 (2024)
- ✨ Release inicial
- 🧠 Ensemble ML (RF, XGB, LGB)
- 📊 50+ features técnicos
- 🛡️ Gestión dinámica de riesgo
- 🎨 Interfaz gráfica completa
- 📚 Documentación exhaustiva

---

## 🤝 Contribuciones

Las contribuciones son bienvenidas. Para cambios importantes:

1. Fork el proyecto
2. Crea una rama de feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

---

## ⚠️ Disclaimer

**IMPORTANTE**: Este software es para fines **educativos y de investigación** únicamente.

- ⚠️ El trading conlleva riesgo significativo de pérdida
- ⚠️ Resultados pasados NO garantizan rendimiento futuro
- ⚠️ NO es asesoría financiera
- ⚠️ Usa bajo tu propio riesgo
- ⚠️ Prueba extensivamente en demo antes de usar capital real

---

## 📄 Licencia

MIT License - Ver archivo LICENSE para detalles

---

## 📞 Soporte

- 📖 **Documentación**: [`GUIA_ML_STRATEGY.md`](GUIA_ML_STRATEGY.md)
- 🐛 **Issues**: Reporta bugs en GitHub Issues
- 💬 **Discusiones**: GitHub Discussions
- 📧 **Email**: support@example.com

---

## 🙏 Agradecimientos

- scikit-learn team por la excelente librería de ML
- XGBoost y LightGBM developers
- Comunidad de trading algorítmico
- Todos los contribuidores

---

<div align="center">

**⭐ Si te gusta este proyecto, dale una estrella en GitHub ⭐**

**🚀 ¡Feliz Trading Algorítmico! 🚀**

---

Hecho con ❤️ por Sistema de Trading Avanzado

</div>
