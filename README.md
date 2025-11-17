# 📊 Sistema de Backtesting para MetaTrader 5

Sistema profesional de backtesting para estrategias de trading en Python, con soporte completo para MetaTrader 5.

## 🌟 Características Principales

### 1. **Gestión de Datos MT5**
- ✅ Conexión automática a MetaTrader 5
- ✅ Descarga de datos históricos OHLC
- ✅ Soporte para múltiples timeframes (M1 a MN1)
- ✅ Validación de calidad de datos
- ✅ Procesamiento de ticks
- ✅ Resampling de datos

### 2. **Motor de Backtesting Avanzado**
- ✅ Simulación realista de ejecución
- ✅ Gestión de spread y comisiones
- ✅ Modelado de slippage
- ✅ Gestión de margen y apalancamiento
- ✅ Trailing stops automáticos
- ✅ Cálculo de MAE/MFE
- ✅ Métricas en tiempo real

### 3. **Sistema de Estrategias**
- ✅ Clase base abstracta extensible
- ✅ Gestión automática de riesgo
- ✅ Cálculo de stop loss/take profit
- ✅ Estrategia de ejemplo (MA Crossover + RSI)
- ✅ Fácil creación de estrategias personalizadas

### 4. **Métricas de Rendimiento**
#### Básicas:
- Total Trades, Win Rate, Profit Factor
- Average Win/Loss, Expectancy
- Risk/Reward Ratio

#### Avanzadas:
- Sharpe Ratio, Sortino Ratio, Omega Ratio
- Maximum Drawdown, Recovery Factor
- Calmar Ratio, Ulcer Index, Serenity Index
- Kelly Criterion
- Tail Ratio, Common Sense Ratio
- Análisis de rachas (win/loss streaks)

### 5. **Visualización y Reportes**
- 📈 Gráficos interactivos con Plotly
- 📊 Price charts con señales
- 📉 Equity curve y drawdown
- 📊 Distribución de P&L
- 📅 Análisis temporal
- 📄 Reportes HTML completos
- 📋 Tablas de métricas y trades

## 📦 Instalación

### Requisitos Previos

1. **Python 3.8+**
2. **MetaTrader 5** (opcional, solo para datos reales)

### Instalación de Dependencias

```bash
pip install -r requirements.txt
```

### Dependencias Principales:
```
MetaTrader5==5.0.4518
pandas==2.1.4
numpy==1.26.2
plotly==5.18.0
quantstats==0.0.62
scipy==1.11.4
```

## 🚀 Inicio Rápido

### Ejemplo 1: Backtest con Datos de Muestra (Sin MT5)

```python
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
from backtest_engine import BacktestEngine
from strategies.moving_average_crossover import MovingAverageCrossover
from analysis.reporting import ReportGenerator
from config.settings import BacktestConfig

# Generar datos de muestra
def generate_sample_data(days=365):
    dates = pd.date_range(end=datetime.now(), periods=days*24, freq='H')
    prices = 1.1000 * np.exp(np.cumsum(np.random.normal(0.0001, 0.01, len(dates))))
    
    data = pd.DataFrame({
        'open': prices,
        'high': prices * 1.005,
        'low': prices * 0.995,
        'close': prices * (1 + np.random.normal(0, 0.003, len(prices))),
        'tick_volume': np.random.randint(100, 1000, len(dates)),
        'spread': 2,
        'real_volume': np.random.randint(1000, 10000, len(dates))
    }, index=dates)
    
    return data

# Generar datos
data = generate_sample_data(365)

# Crear estrategia
strategy = MovingAverageCrossover(
    fast_period=10,
    slow_period=30,
    ma_type='EMA',
    rsi_period=14,
    risk_per_trade=0.02
)

# Configurar backtest
config = BacktestConfig(
    initial_capital=10000.0,
    commission_pct=0.0001,
    slippage_pct=0.0005
)

# Ejecutar backtest
engine = BacktestEngine(config)
result = engine.run(strategy, data)

# Mostrar resultados
print(result.summary())

# Generar reporte
report = ReportGenerator(result)
report.save_report_html('backtest_report.html')
```

### Ejemplo 2: Backtest con MetaTrader 5

```python
from datetime import datetime, timedelta
from data_manager import MT5DataManager
from backtest_engine import BacktestEngine
from strategies.moving_average_crossover import MovingAverageCrossover
from config.settings import MT5Config, BacktestConfig

# Conectar a MT5
data_manager = MT5DataManager(MT5Config())
if data_manager.connect():
    
    # Descargar datos
    symbol = "EURUSD"
    data = data_manager.get_historical_data(
        symbol=symbol,
        timeframe="H1",
        start_date=datetime.now() - timedelta(days=365),
        count=5000
    )
    
    # Obtener info del símbolo
    symbol_info = data_manager.get_symbol_info(symbol)
    
    # Crear estrategia
    strategy = MovingAverageCrossover(
        fast_period=10,
        slow_period=30
    )
    
    # Ejecutar backtest
    config = BacktestConfig(initial_capital=10000.0)
    engine = BacktestEngine(config)
    result = engine.run(strategy, data, symbol_info)
    
    # Resultados
    print(result.summary())
    
    # Desconectar
    data_manager.disconnect()
```

### Ejemplo 3: Crear Estrategia Personalizada

```python
from strategies.base_strategy import TradingStrategy, Signal
import pandas as pd

class MyCustomStrategy(TradingStrategy):
    def __init__(self, param1=10, param2=20, **kwargs):
        parameters = {
            'param1': param1,
            'param2': param2
        }
        super().__init__(
            name='MyStrategy',
            parameters=parameters,
            **kwargs
        )
    
    def calculate_indicators(self, data: pd.DataFrame) -> pd.DataFrame:
        """Calcula indicadores personalizados"""
        df = data.copy()
        
        # Ejemplo: SMA
        df['sma'] = df['close'].rolling(window=self.parameters['param1']).mean()
        
        # Guardar para uso en señales
        self.indicators['SMA'] = df['sma']
        
        return df
    
    def generate_signals(self, data: pd.DataFrame) -> list:
        """Genera señales de trading"""
        signals = []
        
        for i in range(1, len(data)):
            current = data.iloc[i]
            previous = data.iloc[i-1]
            
            # Ejemplo: Cruce de precio con SMA
            if previous['close'] < previous['sma'] and current['close'] > current['sma']:
                signal = Signal(
                    timestamp=current.name,
                    signal_type='BUY',
                    price=current['close']
                )
                signals.append(signal)
            
            elif previous['close'] > previous['sma'] and current['close'] < current['sma']:
                signal = Signal(
                    timestamp=current.name,
                    signal_type='SELL',
                    price=current['close']
                )
                signals.append(signal)
        
        return signals

# Usar la estrategia
strategy = MyCustomStrategy(param1=20, param2=50)
```

## 📁 Estructura del Proyecto

```
strategy_backtest/
├── config/
│   ├── __init__.py
│   └── settings.py          # Configuraciones globales
├── strategies/
│   ├── __init__.py
│   ├── base_strategy.py     # Clase base abstracta
│   └── moving_average_crossover.py  # Estrategia de ejemplo
├── analysis/
│   ├── __init__.py
│   ├── performance.py       # Análisis de rendimiento
│   └── reporting.py         # Generación de reportes
├── data_manager.py          # Gestor de datos MT5
├── backtest_engine.py       # Motor de backtesting
├── example_usage.py         # Ejemplos de uso
├── requirements.txt         # Dependencias
└── README.md               # Este archivo
```

## 🎯 Componentes Principales

### 1. MT5DataManager

Gestiona la conexión y descarga de datos de MetaTrader 5.

```python
from data_manager import MT5DataManager
from config.settings import MT5Config

# Crear gestor
data_manager = MT5DataManager(MT5Config())

# Conectar
data_manager.connect()

# Validar símbolo
data_manager.validate_symbol("EURUSD")

# Descargar datos
data = data_manager.get_historical_data(
    symbol="EURUSD",
    timeframe="H1",
    start_date=datetime(2024, 1, 1),
    count=5000
)

# Obtener información del símbolo
info = data_manager.get_symbol_info("EURUSD")

# Desconectar
data_manager.disconnect()
```

### 2. BacktestEngine

Ejecuta el backtest con simulación realista.

```python
from backtest_engine import BacktestEngine
from config.settings import BacktestConfig

# Configurar
config = BacktestConfig(
    initial_capital=10000.0,
    commission=0.0,          # Comisión fija por trade
    commission_pct=0.0001,   # 0.01% comisión
    slippage_pct=0.0005,     # 0.05% slippage
    leverage=100.0,
    use_spread=True
)

# Crear engine
engine = BacktestEngine(config)

# Ejecutar
result = engine.run(strategy, data, symbol_info)
```

### 3. TradingStrategy (Base Class)

Clase abstracta para crear estrategias.

**Métodos obligatorios:**
- `calculate_indicators(data)`: Calcula indicadores técnicos
- `generate_signals(data)`: Genera señales de trading

**Métodos opcionales:**
- `manage_risk(signal, price, balance)`: Gestión de riesgo
- `check_exit_conditions(position, bar)`: Condiciones de salida
- `get_parameter_ranges()`: Rangos para optimización

### 4. ReportGenerator

Genera reportes y visualizaciones.

```python
from analysis.reporting import ReportGenerator

# Crear generador
report = ReportGenerator(result)

# Generar reporte HTML completo
report.save_report_html('report.html')

# Crear gráfico interactivo
fig = report.create_full_report()
fig.show()

# Tabla de métricas
metrics_df = report.create_metrics_table()

# Tabla de trades
trades_df = report.create_trades_dataframe()
```

## 📊 Métricas Disponibles

### Métricas Básicas
- **Total Trades**: Número total de operaciones
- **Win Rate**: Porcentaje de trades ganadores
- **Profit Factor**: Ganancia bruta / Pérdida bruta
- **Average Win/Loss**: Ganancia/Pérdida promedio
- **Expectancy**: Ganancia esperada por trade

### Métricas de Riesgo
- **Sharpe Ratio**: Retorno ajustado por volatilidad
- **Sortino Ratio**: Similar a Sharpe, solo volatilidad negativa
- **Omega Ratio**: Probabilidad de ganancias vs pérdidas
- **Maximum Drawdown**: Máxima caída desde el pico
- **Recovery Factor**: Retorno / Max Drawdown
- **Calmar Ratio**: Retorno anualizado / Max Drawdown

### Métricas Avanzadas
- **Kelly Criterion**: Tamaño óptimo de posición
- **Ulcer Index**: Medida de stress del drawdown
- **Serenity Index**: Retorno / Ulcer Index
- **Tail Ratio**: Ratio de colas de distribución
- **MAE/MFE**: Maximum Adverse/Favorable Excursion

## 🔧 Configuración

### MT5Config
```python
from config.settings import MT5Config

config = MT5Config(
    timeout=60000,          # Timeout en ms
    portable=False,         # Modo portable
    login=None,            # Login (opcional)
    password=None,         # Password (opcional)
    server=None,           # Servidor (opcional)
    path=None              # Path a MT5 (opcional)
)
```

### BacktestConfig
```python
from config.settings import BacktestConfig

config = BacktestConfig(
    initial_capital=10000.0,
    commission=0.0,
    commission_pct=0.0001,
    slippage_pct=0.0005,
    leverage=100.0,
    margin_call_level=0.5,
    stop_out_level=0.2,
    use_spread=True,
    timezone='UTC'
)
```

### StrategyConfig
```python
from config.settings import StrategyConfig

config = StrategyConfig(
    risk_per_trade=0.02,        # 2% riesgo por trade
    max_positions=1,
    use_trailing_stop=True,
    trailing_stop_pct=0.02,
    min_risk_reward=2.0,
    max_daily_trades=5,
    max_daily_loss_pct=0.05
)
```

## 🎓 Ejemplos Avanzados

### Optimización de Parámetros

```python
from backtest_engine import BacktestEngine
from strategies.moving_average_crossover import MovingAverageCrossover

# Rangos de parámetros
fast_periods = range(5, 21, 2)
slow_periods = range(20, 51, 5)

best_sharpe = -999
best_params = {}

for fast in fast_periods:
    for slow in slow_periods:
        if fast >= slow:
            continue
        
        strategy = MovingAverageCrossover(
            fast_period=fast,
            slow_period=slow
        )
        
        engine = BacktestEngine(config)
        result = engine.run(strategy, data)
        
        sharpe = result.metrics['sharpe_ratio']
        
        if sharpe > best_sharpe:
            best_sharpe = sharpe
            best_params = {'fast': fast, 'slow': slow}

print(f"Best parameters: {best_params}")
print(f"Best Sharpe: {best_sharpe:.2f}")
```

### Walk-Forward Analysis

```python
# Dividir datos en períodos
total_bars = len(data)
window_size = total_bars // 5  # 5 períodos

for i in range(5):
    start_idx = i * window_size
    end_idx = start_idx + window_size
    
    train_data = data.iloc[start_idx:end_idx]
    
    # Optimizar en train_data
    # ...
    
    if i < 4:  # Hay período de prueba
        test_data = data.iloc[end_idx:end_idx + window_size]
        
        # Probar en test_data
        # ...
```

## 📝 Notas Importantes

### Requisitos de MT5
- MetaTrader 5 debe estar instalado y funcionando
- La cuenta debe estar autorizada para acceso API
- Los símbolos deben estar en Market Watch

### Rendimiento
- El sistema puede procesar miles de barras por segundo
- Para optimizaciones extensas, considerar paralelización
- Los gráficos interactivos pueden ser pesados con muchos datos

### Datos de Calidad
- El sistema valida automáticamente la calidad de datos
- Se detectan gaps, valores nulos y OHLC inválidos
- Se recomienda revisar warnings de calidad de datos

## 🐛 Solución de Problemas

### Error: "MT5 initialization failed"
- Verificar que MT5 esté instalado
- Verificar que MT5 esté ejecutándose
- Verificar permisos de acceso API

### Error: "Symbol not found"
- Verificar que el símbolo esté en Market Watch
- Verificar ortografía del símbolo
- Intentar `symbol_select(symbol, True)`

### Error: "No data retrieved"
- Verificar fechas (no futuras)
- Verificar que el timeframe tenga datos
- Verificar conexión a internet

## 📚 Recursos Adicionales

### Documentación MT5
- [MetaTrader 5 Python Documentation](https://www.mql5.com/en/docs/python_metatrader5)
- [MQL5 Community](https://www.mql5.com/)

### Indicadores Técnicos
- [TA-Lib Documentation](https://mrjbq7.github.io/ta-lib/)
- [Pandas Technical Analysis](https://github.com/bukosabino/ta)

## 🤝 Contribuciones

Las contribuciones son bienvenidas. Para contribuir:

1. Fork el repositorio
2. Crea una rama para tu feature
3. Commit tus cambios
4. Push a la rama
5. Abre un Pull Request

## 📄 Licencia

Este proyecto está bajo la licencia MIT.

## 👨‍💻 Autor

Sistema desarrollado para backtesting profesional de estrategias de trading.

## 🔄 Actualizaciones

### Versión 1.0.0 (Actual)
- ✅ Sistema completo de backtesting
- ✅ Soporte MT5
- ✅ Múltiples métricas
- ✅ Visualizaciones interactivas
- ✅ Estrategia de ejemplo
- ✅ Documentación completa

### Próximas Mejoras
- [ ] Monte Carlo simulation
- [ ] Walk-forward optimization automática
- [ ] Detección de overfitting
- [ ] Más estrategias de ejemplo
- [ ] Soporte para múltiples símbolos
- [ ] Portfolio backtesting

## 📞 Soporte

Para problemas o preguntas:
- Revisa la documentación
- Revisa los ejemplos en `example_usage.py`
- Revisa los logs para errores detallados

---

**¡Feliz Trading! 📈🚀**
