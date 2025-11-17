# 📁 ESTRUCTURA DE DIRECTORIOS DEL PROYECTO

## Estructura Completa

```
strategy_backtest/                          # Directorio raíz del proyecto
│
├── 📄 DOCUMENTACIÓN (Raíz)
│   ├── START_HERE.md                      # 🚀 EMPIEZA AQUÍ - Guía de inicio inmediato
│   ├── INDEX.md                           # 📚 Índice completo de toda la documentación
│   ├── QUICKSTART.md                      # ⚡ Guía rápida de inicio (5 min)
│   ├── README.md                          # 📖 Documentación completa del sistema
│   ├── INSTALLATION.md                    # 🔧 Guía de instalación detallada
│   ├── BEST_PRACTICES.md                  # 🎯 Mejores prácticas y consejos
│   ├── PROJECT_SUMMARY.txt                # 📊 Resumen ejecutivo del proyecto
│   └── requirements.txt                   # 📦 Dependencias de Python
│
├── 🐍 MÓDULOS PRINCIPALES (Raíz)
│   ├── __init__.py                        # Inicializador del paquete principal
│   ├── data_manager.py                    # Gestor de conexión y datos MT5
│   ├── backtest_engine.py                 # Motor de backtesting
│   └── example_usage.py                   # Ejemplos de uso del sistema
│
├── ⚙️ config/                              # CONFIGURACIÓN DEL SISTEMA
│   ├── __init__.py                        # Inicializador del módulo config
│   └── settings.py                        # Configuraciones globales
│                                           # - MT5Config
│                                           # - BacktestConfig
│                                           # - StrategyConfig
│                                           # - OptimizationConfig
│
├── 🧠 strategies/                          # ESTRATEGIAS DE TRADING
│   ├── __init__.py                        # Inicializador del módulo strategies
│   ├── base_strategy.py                   # Clase base abstracta para estrategias
│   │                                       # - TradingStrategy (clase abstracta)
│   │                                       # - Signal (dataclass)
│   │                                       # - Position (dataclass)
│   │
│   ├── moving_average_crossover.py        # Estrategia: Cruce de Medias Móviles + RSI
│   │                                       # - MovingAverageCrossover (clase)
│   │
│   └── example_strategy.py                # Plantilla para crear nuevas estrategias
│
└── 📊 analysis/                            # ANÁLISIS Y REPORTES
    ├── __init__.py                        # Inicializador del módulo analysis
    ├── performance.py                     # Análisis de rendimiento avanzado
    │                                       # - PerformanceAnalyzer (clase)
    │                                       # - 20+ métricas avanzadas
    │
    └── reporting.py                       # Generación de reportes y visualizaciones
                                            # - ReportGenerator (clase)
                                            # - Gráficos interactivos
                                            # - Reportes HTML


📁 ARCHIVOS GENERADOS (Creados al ejecutar)
├── backtest_report_sample.html            # Reporte HTML completo con métricas
├── backtest_charts.html                   # Dashboard de gráficos interactivos
├── optimization_results.csv               # Resultados de optimización de parámetros
└── backtest.log                           # Archivo de logs (si se configura)
```

---

## Estructura Detallada por Módulo

### 📂 Nivel Raíz (Root)

```
strategy_backtest/
├── START_HERE.md              # Primer archivo a leer - Inicio en 3 pasos
├── INDEX.md                   # Índice completo del proyecto
├── QUICKSTART.md              # Guía rápida para principiantes
├── README.md                  # Documentación técnica completa
├── INSTALLATION.md            # Instrucciones de instalación detalladas
├── BEST_PRACTICES.md          # Guía de mejores prácticas de trading
├── PROJECT_SUMMARY.txt        # Resumen ejecutivo del proyecto
├── requirements.txt           # Lista de dependencias Python
├── __init__.py                # Hace que strategy_backtest sea un paquete
├── data_manager.py            # ~450 líneas - Gestión de datos MT5
├── backtest_engine.py         # ~600 líneas - Motor de backtesting
└── example_usage.py           # ~400 líneas - Ejemplos de uso
```

### 📂 config/ - Configuración

```
config/
├── __init__.py                # Exporta clases de configuración
└── settings.py                # ~150 líneas
    │
    ├── Clases de configuración:
    │   ├── MT5Config              # Configuración de MetaTrader 5
    │   ├── BacktestConfig         # Configuración del backtesting
    │   ├── StrategyConfig         # Configuración de estrategias
    │   └── OptimizationConfig     # Configuración de optimización
    │
    ├── Constantes:
    │   └── TIMEFRAMES             # Diccionario de timeframes MT5
    │
    └── Funciones:
        ├── get_config()           # Obtener configuración
        └── update_config()        # Actualizar configuración
```

### 📂 strategies/ - Estrategias de Trading

```
strategies/
├── __init__.py                     # Exporta clases de estrategias
│
├── base_strategy.py                # ~350 líneas - Clase base
│   │
│   ├── Dataclasses:
│   │   ├── Signal                 # Representa una señal de trading
│   │   └── Position               # Representa una posición abierta
│   │
│   └── Clase abstracta:
│       └── TradingStrategy        # Base para todas las estrategias
│           │
│           ├── Métodos abstractos (OBLIGATORIOS):
│           │   ├── calculate_indicators()    # Calcular indicadores
│           │   └── generate_signals()        # Generar señales
│           │
│           └── Métodos implementados:
│               ├── manage_risk()             # Gestión de riesgo
│               ├── check_exit_conditions()   # Condiciones de salida
│               ├── run()                     # Ejecutar estrategia
│               ├── get_parameter_ranges()    # Rangos para optimización
│               ├── update_parameters()       # Actualizar parámetros
│               └── reset()                   # Reiniciar estado
│
├── moving_average_crossover.py     # ~200 líneas - Estrategia de ejemplo
│   │
│   └── Clase:
│       └── MovingAverageCrossover # Estrategia de cruce de MAs + RSI
│           │
│           ├── Indicadores:
│           │   ├── EMA/SMA (configurable)
│           │   ├── RSI
│           │   └── ATR
│           │
│           └── Señales:
│               ├── BUY: MA rápida cruza arriba + RSI < 70
│               └── SELL: MA rápida cruza abajo + RSI > 30
│
└── example_strategy.py             # Plantilla para nuevas estrategias
```

### 📂 analysis/ - Análisis y Reportes

```
analysis/
├── __init__.py                     # Exporta clases de análisis
│
├── performance.py                  # ~400 líneas - Análisis de rendimiento
│   │
│   └── Clase:
│       └── PerformanceAnalyzer    # Análisis avanzado de métricas
│           │
│           ├── Métricas básicas:
│           │   ├── Win Rate, Profit Factor
│           │   ├── Average Win/Loss
│           │   └── Expectancy
│           │
│           ├── Métricas avanzadas:
│           │   ├── Sharpe Ratio, Sortino Ratio
│           │   ├── Omega Ratio, Calmar Ratio
│           │   ├── Kelly Criterion
│           │   ├── Ulcer Index, Serenity Index
│           │   ├── Tail Ratio
│           │   └── MAE/MFE analysis
│           │
│           └── Análisis temporal:
│               ├── Por hora del día
│               ├── Por día de la semana
│               └── Por mes
│
└── reporting.py                    # ~500 líneas - Reportes y visualización
    │
    └── Clase:
        └── ReportGenerator        # Generación de reportes
            │
            ├── Gráficos:
            │   ├── Price & Signals (Candlestick + señales)
            │   ├── Equity Curve (Curva de capital)
            │   ├── Drawdown (Caídas de capital)
            │   ├── P&L Distribution (Distribución de ganancias)
            │   ├── Cumulative Returns (Retornos acumulados)
            │   ├── Monthly Returns (Retornos mensuales)
            │   ├── Win/Loss Analysis (Análisis ganar/perder)
            │   └── Trade Duration (Duración de trades)
            │
            ├── Tablas:
            │   ├── Metrics Table (Tabla de métricas)
            │   └── Trades Table (Tabla de trades)
            │
            └── Reportes:
                ├── HTML Report (Reporte HTML completo)
                ├── Summary Text (Resumen textual)
                └── Full Report (Gráficos + tablas + resumen)
```

---

## Archivos por Categoría

### 📄 Documentación (7 archivos)
1. `START_HERE.md` - Inicio inmediato
2. `INDEX.md` - Índice completo
3. `QUICKSTART.md` - Guía rápida
4. `README.md` - Documentación completa
5. `INSTALLATION.md` - Instalación
6. `BEST_PRACTICES.md` - Mejores prácticas
7. `PROJECT_SUMMARY.txt` - Resumen del proyecto

### 🐍 Código Python (10 archivos)
1. `__init__.py` - Paquete principal
2. `data_manager.py` - Gestión de datos MT5
3. `backtest_engine.py` - Motor de backtesting
4. `example_usage.py` - Ejemplos de uso
5. `config/__init__.py` - Paquete config
6. `config/settings.py` - Configuraciones
7. `strategies/__init__.py` - Paquete strategies
8. `strategies/base_strategy.py` - Clase base
9. `strategies/moving_average_crossover.py` - Estrategia ejemplo
10. `analysis/__init__.py` - Paquete analysis
11. `analysis/performance.py` - Análisis
12. `analysis/reporting.py` - Reportes

### ⚙️ Configuración (1 archivo)
1. `requirements.txt` - Dependencias

---

## Flujo de Datos del Sistema

```
┌─────────────────────┐
│   MetaTrader 5      │  o  Datos de muestra
│   (Opcional)        │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│   data_manager.py   │ ← Descarga y valida datos históricos
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│   Estrategia        │ ← Calcula indicadores y genera señales
│   (strategies/)     │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  backtest_engine.py │ ← Simula trading y ejecuta órdenes
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  analysis/          │ ← Calcula métricas y genera reportes
│  - performance.py   │
│  - reporting.py     │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  Reportes HTML      │ ← Visualización y análisis
│  Gráficos           │
│  Tablas             │
└─────────────────────┘
```

---

## Instrucciones de Creación

### Paso 1: Crear la estructura de directorios

```bash
mkdir -p strategy_backtest/config
mkdir -p strategy_backtest/strategies
mkdir -p strategy_backtest/analysis
cd strategy_backtest
```

### Paso 2: Crear archivos vacíos (estructura básica)

```bash
# Raíz
touch __init__.py
touch requirements.txt
touch data_manager.py
touch backtest_engine.py
touch example_usage.py

# Documentación
touch START_HERE.md
touch INDEX.md
touch QUICKSTART.md
touch README.md
touch INSTALLATION.md
touch BEST_PRACTICES.md
touch PROJECT_SUMMARY.txt

# Config
touch config/__init__.py
touch config/settings.py

# Strategies
touch strategies/__init__.py
touch strategies/base_strategy.py
touch strategies/moving_average_crossover.py
touch strategies/example_strategy.py

# Analysis
touch analysis/__init__.py
touch analysis/performance.py
touch analysis/reporting.py
```

### Paso 3: Verificar la estructura

```bash
# En Linux/Mac
tree -L 2

# En Windows
dir /s /b
```

---

## Tamaños Aproximados

```
Total del proyecto: ~290 KB

Por tipo:
- Código Python:       ~2,700 líneas  (~100 KB)
- Documentación:       ~2,500 líneas  (~120 KB)
- Configuración:       ~50 líneas     (~2 KB)

Por módulo:
- data_manager.py:     ~450 líneas
- backtest_engine.py:  ~600 líneas
- base_strategy.py:    ~350 líneas
- performance.py:      ~400 líneas
- reporting.py:        ~500 líneas
- example_usage.py:    ~400 líneas
```

---

## Archivos Críticos (No eliminar)

✅ **Esenciales para funcionamiento:**
- `__init__.py` (en cada carpeta)
- `data_manager.py`
- `backtest_engine.py`
- `config/settings.py`
- `strategies/base_strategy.py`
- `requirements.txt`

✅ **Esenciales para empezar:**
- `START_HERE.md`
- `example_usage.py`
- `strategies/moving_average_crossover.py`

---

## Archivos Opcionales (Pueden eliminarse)

⚠️ **Pueden eliminarse sin afectar funcionalidad:**
- Cualquier archivo `.md` (documentación)
- `PROJECT_SUMMARY.txt`
- `strategies/example_strategy.py` (es solo plantilla)

⚠️ **Se regeneran automáticamente:**
- Carpetas `__pycache__/`
- Archivos `.pyc`

---

## Resumen Visual Simplificado

```
strategy_backtest/
│
├── 📚 Documentación (7 archivos .md)
│
├── 🔧 Código Principal (3 archivos .py)
│   ├── data_manager.py
│   ├── backtest_engine.py
│   └── example_usage.py
│
├── ⚙️ config/
│   └── settings.py
│
├── 🧠 strategies/
│   ├── base_strategy.py
│   └── moving_average_crossover.py
│
└── 📊 analysis/
    ├── performance.py
    └── reporting.py
```

---

**Total: 4 carpetas | 31 archivos | ~290 KB**
