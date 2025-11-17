# 🎯 EMPIEZA AQUÍ - START HERE

## ¿Nuevo en el sistema? Sigue estos pasos:

### Paso 1: Instala las dependencias (2 minutos)
```bash
pip install -r requirements.txt
```

### Paso 2: Ejecuta el ejemplo (30 segundos)
```bash
python example_usage.py
```

Cuando veas el menú, elige **opción 2** (recomendado).

### Paso 3: Revisa los resultados (5 minutos)

El sistema generará dos archivos HTML:
1. `backtest_report_sample.html` - Abre este archivo en tu navegador
2. `backtest_charts.html` - Gráficos interactivos

### ¡Eso es todo! Ya tienes tu primer backtest corriendo 🎉

---

## ¿Qué sigue?

### Si quieres aprender más:
→ Lee [QUICKSTART.md](QUICKSTART.md) para personalización básica

### Si quieres crear tu estrategia:
→ Lee [README.md](README.md) sección "Crear Estrategia Personalizada"

### Si tienes problemas:
→ Lee [INSTALLATION.md](INSTALLATION.md) sección "Solución de Problemas"

### Si quieres mejores prácticas:
→ Lee [BEST_PRACTICES.md](BEST_PRACTICES.md)

### Si quieres ver todo:
→ Lee [INDEX.md](INDEX.md) para el índice completo

---

## Estructura de Carpetas

```
strategy_backtest/
├── START_HERE.md          ← Estás aquí
├── INDEX.md              ← Índice completo
├── QUICKSTART.md         ← Guía rápida
├── README.md             ← Documentación completa
├── example_usage.py      ← EJECUTA ESTE ARCHIVO
├── requirements.txt      ← Dependencias
├── data_manager.py       ← Conexión MT5
├── backtest_engine.py    ← Motor de backtest
├── config/               ← Configuraciones
├── strategies/           ← Tus estrategias aquí
└── analysis/             ← Análisis y reportes
```

---

## Comandos Rápidos

### Primera ejecución
```bash
# 1. Instalar
pip install -r requirements.txt

# 2. Ejecutar
python example_usage.py

# 3. Elegir opción 2
```

### Cambiar parámetros de estrategia
Edita `example_usage.py` líneas 138-145:
```python
strategy = MovingAverageCrossover(
    fast_period=12,      # ← Cambia esto
    slow_period=26,      # ← Y esto
    risk_per_trade=0.02  # ← Y esto
)
```

### Optimizar parámetros
```bash
python example_usage.py
# Elige opción 3
```

---

## Verificación de Instalación

### Verifica Python
```bash
python --version
# Debe mostrar: Python 3.8 o superior
```

### Verifica instalación de librerías
```bash
python -c "import MetaTrader5, pandas, numpy, plotly; print('✅ OK')"
```

Si ves `✅ OK`, estás listo para empezar!

---

## Resultados Esperados

Al ejecutar el ejemplo verás:

1. **En la consola**: 
   - Resumen de backtest
   - Métricas clave (Win Rate, Profit Factor, etc.)
   - Tabla de métricas detalladas

2. **Archivos generados**:
   - `backtest_report_sample.html` → Reporte completo con gráficos
   - `backtest_charts.html` → Dashboard interactivo
   - `optimization_results.csv` (si ejecutas opción 3)

---

## Métricas Clave a Revisar

Después de ejecutar, busca estas métricas en el resumen:

✅ **Win Rate**: >50% es bueno
✅ **Profit Factor**: >2.0 es excelente
✅ **Sharpe Ratio**: >1.5 es bueno
✅ **Max Drawdown**: <20% es aceptable
✅ **Total Return**: Cuanto mayor, mejor

---

## ¿Tienes MetaTrader 5?

Si ya tienes MT5 instalado y quieres usar datos reales:

1. Ejecuta: `python example_usage.py`
2. Elige opción 1
3. Asegúrate que MT5 esté abierto

**Nota**: Para principiantes, recomendamos empezar con opción 2 (datos de muestra).

---

## FAQ Ultra-Rápido

**¿Necesito MT5?**
No. Usa opción 2.

**¿Cuánto tarda?**
~30 segundos.

**¿Puedo cambiar parámetros?**
Sí. Edita `example_usage.py`.

**¿Los resultados son reales?**
Son simulaciones. No garantía de futuro.

**¿Funciona en mi computadora?**
Si tienes Python 3.8+, sí.

---

## Siguiente Nivel

Una vez que ejecutes el ejemplo exitosamente:

1. ✅ Experimenta con diferentes parámetros
2. ✅ Lee QUICKSTART.md
3. ✅ Crea tu primera estrategia simple
4. ✅ Ejecuta optimización (opción 3)
5. ✅ Lee BEST_PRACTICES.md

---

## Comandos de Ayuda

```bash
# Ver versión de Python
python --version

# Ver librerías instaladas
pip list

# Reinstalar dependencias
pip install -r requirements.txt --upgrade

# Ver archivos del proyecto
ls -la
```

---

## 🚨 ¿Problemas?

### Error: "No module named..."
```bash
pip install -r requirements.txt
```

### Error: "Python no encontrado"
Instala Python desde python.org

### Error: "Permission denied"
En Linux/Mac: `sudo pip install -r requirements.txt`

### Otros problemas
Lee INSTALLATION.md → Sección "Solución de Problemas"

---

## Cronograma Sugerido (Primera Hora)

```
00:00 - 00:02  →  Instalar dependencias
00:02 - 00:03  →  Ejecutar ejemplo (opción 2)
00:03 - 00:08  →  Revisar reportes HTML
00:08 - 00:15  →  Leer QUICKSTART.md
00:15 - 00:25  →  Experimentar con parámetros
00:25 - 00:35  →  Ejecutar optimización (opción 3)
00:35 - 00:50  →  Revisar README.md secciones clave
00:50 - 01:00  →  Planear tu primera estrategia
```

---

## 🎉 ¡Listo para empezar!

```bash
pip install -r requirements.txt
python example_usage.py
# Elige opción 2
```

**¡Feliz backtesting! 📈🚀**

---

*Para más información, consulta el [ÍNDICE COMPLETO](INDEX.md)*
