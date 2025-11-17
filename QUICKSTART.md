# 🚀 QUICK START GUIDE

## Instalación en 3 Pasos

### 1. Instalar Python 3.8+
Descarga e instala Python desde [python.org](https://www.python.org/downloads/)

### 2. Instalar Dependencias
```bash
pip install -r requirements.txt
```

### 3. Ejecutar Ejemplo
```bash
python example_usage.py
```

## Primera Ejecución

Al ejecutar `example_usage.py`, verás un menú:

```
Select an example to run:
1. Backtest with MetaTrader 5 data (requires MT5 installed)
2. Backtest with sample data (no MT5 required) - RECOMMENDED
3. Parameter optimization example
4. Run all examples

Enter your choice (1-4):
```

**Recomendación: Elige opción 2** (no requiere MT5)

## Resultados

El sistema generará:
- ✅ Resumen en consola con métricas clave
- ✅ `backtest_report_sample.html` - Reporte completo
- ✅ `backtest_charts.html` - Gráficos interactivos

## Personalización Rápida

### Cambiar Parámetros de la Estrategia

Edita en `example_usage.py`:

```python
strategy = MovingAverageCrossover(
    fast_period=12,      # Cambia este valor
    slow_period=26,      # Cambia este valor
    ma_type='EMA',       # 'SMA' o 'EMA'
    rsi_period=14,
    risk_per_trade=0.02  # 2% riesgo por trade
)
```

### Cambiar Capital Inicial

```python
backtest_config = BacktestConfig(
    initial_capital=10000.0,  # Cambia este valor
    commission_pct=0.0001,
    slippage_pct=0.0005
)
```

## Crear Tu Propia Estrategia

1. Copia `strategies/moving_average_crossover.py`
2. Renombra el archivo y la clase
3. Modifica `calculate_indicators()` y `generate_signals()`
4. Importa y usa tu estrategia en `example_usage.py`

## Estructura de Archivos Generados

```
strategy_backtest/
├── backtest_report_sample.html    # Reporte completo
├── backtest_charts.html           # Gráficos interactivos
└── optimization_results.csv       # Resultados de optimización
```

## Métricas Clave a Revisar

### Rendimiento
- **Total Return %**: Retorno total del período
- **Win Rate**: Porcentaje de trades ganadores (>50% es bueno)
- **Profit Factor**: Debe ser >1.5 (>2.0 es excelente)

### Riesgo
- **Max Drawdown**: Caída máxima (<20% es aceptable)
- **Sharpe Ratio**: >1.0 es bueno, >2.0 es excelente
- **Expectancy**: Ganancia esperada por trade (debe ser positiva)

## Próximos Pasos

1. ✅ Ejecuta el ejemplo con datos de muestra
2. ✅ Revisa los reportes HTML generados
3. ✅ Experimenta con diferentes parámetros
4. ✅ Crea tu propia estrategia
5. ✅ Ejecuta optimización de parámetros (opción 3)
6. ✅ Si tienes MT5, prueba con datos reales (opción 1)

## Troubleshooting

### Error: Module not found
```bash
pip install -r requirements.txt
```

### Error: MT5 initialization failed
- Solo afecta opción 1
- Usa opción 2 (datos de muestra)
- O instala MetaTrader 5

### Gráficos no se muestran
- Abre los archivos .html en tu navegador
- Usa Chrome/Firefox para mejor compatibilidad

## Consejos de Trading

⚠️ **IMPORTANTE**: Este sistema es para BACKTESTING únicamente.

- ✅ Prueba estrategias con datos históricos
- ✅ Valida resultados en múltiples períodos
- ✅ Considera comisiones y slippage realistas
- ⚠️ Resultados pasados NO garantizan rendimiento futuro
- ⚠️ Practica con cuenta demo antes de real

## Recursos

- 📖 README.md - Documentación completa
- 💻 example_usage.py - Código de ejemplo
- 📊 strategies/ - Ejemplos de estrategias

---

**¡Buena suerte con tu backtesting! 📈**
