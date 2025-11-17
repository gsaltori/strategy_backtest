# 📚 ÍNDICE DE DOCUMENTACIÓN

## Documentos Principales

### 🚀 Para Empezar
1. **[QUICKSTART.md](QUICKSTART.md)** - Comienza aquí
   - Instalación en 3 pasos
   - Primera ejecución
   - Personalización rápida

2. **[INSTALLATION.md](INSTALLATION.md)** - Guía de instalación completa
   - Requisitos del sistema
   - Instalación paso a paso
   - Configuración de MT5
   - Solución de problemas

### 📖 Documentación Principal
3. **[README.md](README.md)** - Documentación completa del sistema
   - Características del sistema
   - Ejemplos de código
   - API Reference
   - Componentes principales

### 🎯 Guías Avanzadas
4. **[BEST_PRACTICES.md](BEST_PRACTICES.md)** - Mejores prácticas
   - Desarrollo de estrategias
   - Evitar errores comunes
   - Optimización de parámetros
   - Análisis de resultados

## Estructura del Proyecto

```
strategy_backtest/
├── 📄 Documentación
│   ├── INDEX.md              ← Estás aquí
│   ├── QUICKSTART.md         ← Comienza aquí
│   ├── README.md             ← Documentación completa
│   ├── INSTALLATION.md       ← Guía de instalación
│   └── BEST_PRACTICES.md     ← Mejores prácticas
│
├── ⚙️ Configuración
│   ├── config/
│   │   ├── __init__.py
│   │   └── settings.py       ← Configuraciones globales
│   └── requirements.txt      ← Dependencias Python
│
├── 🧠 Estrategias
│   └── strategies/
│       ├── __init__.py
│       ├── base_strategy.py          ← Clase base abstracta
│       └── moving_average_crossover.py  ← Ejemplo
│
├── 🔧 Core
│   ├── data_manager.py       ← Gestión de datos MT5
│   ├── backtest_engine.py    ← Motor de backtesting
│   └── __init__.py
│
├── 📊 Análisis
│   └── analysis/
│       ├── __init__.py
│       ├── performance.py    ← Métricas avanzadas
│       └── reporting.py      ← Reportes y gráficos
│
└── 💻 Ejemplos
    └── example_usage.py      ← Ejemplos de uso
```

## Flujo de Aprendizaje Recomendado

### Nivel Principiante
1. Lee [QUICKSTART.md](QUICKSTART.md)
2. Instala dependencias
3. Ejecuta `example_usage.py` opción 2
4. Revisa reportes HTML generados
5. Experimenta cambiando parámetros

### Nivel Intermedio
1. Lee [README.md](README.md) sección "Componentes Principales"
2. Estudia `strategies/moving_average_crossover.py`
3. Crea tu primera estrategia personalizada
4. Ejecuta optimización de parámetros (opción 3)
5. Lee [BEST_PRACTICES.md](BEST_PRACTICES.md) sección "Desarrollo de Estrategias"

### Nivel Avanzado
1. Lee [BEST_PRACTICES.md](BEST_PRACTICES.md) completo
2. Implementa walk-forward analysis
3. Estudia `analysis/performance.py` para métricas avanzadas
4. Integra con MT5 real (requiere instalación)
5. Desarrolla sistema de múltiples estrategias

## Guías Rápidas por Tarea

### Quiero empezar inmediatamente
→ [QUICKSTART.md](QUICKSTART.md)

### Tengo problemas con la instalación
→ [INSTALLATION.md](INSTALLATION.md) → Sección "Solución de Problemas"

### Quiero crear mi estrategia
→ [README.md](README.md) → Sección "Crear Estrategia Personalizada"
→ Ver `strategies/moving_average_crossover.py` como ejemplo

### Quiero optimizar parámetros
→ [README.md](README.md) → Sección "Optimización de Parámetros"
→ [BEST_PRACTICES.md](BEST_PRACTICES.md) → Sección "Optimización de Parámetros"

### Quiero entender las métricas
→ [README.md](README.md) → Sección "Métricas Disponibles"

### Quiero conectar con MT5 real
→ [INSTALLATION.md](INSTALLATION.md) → Sección "Instalación de MetaTrader 5"
→ [README.md](README.md) → Ejemplo 2: Backtest con MT5

### Quiero evitar errores comunes
→ [BEST_PRACTICES.md](BEST_PRACTICES.md) → Sección "Evitar Errores Comunes"

### Quiero generar mejores reportes
→ [README.md](README.md) → Sección "ReportGenerator"
→ Ver `analysis/reporting.py`

## Archivos de Código Principal

### Core Components
| Archivo | Descripción | Líneas |
|---------|-------------|--------|
| `data_manager.py` | Gestión de conexión y datos MT5 | ~450 |
| `backtest_engine.py` | Motor de backtesting | ~600 |
| `strategies/base_strategy.py` | Clase base para estrategias | ~350 |

### Strategy Examples
| Archivo | Descripción | Estrategia |
|---------|-------------|------------|
| `strategies/moving_average_crossover.py` | Cruce de MAs con RSI | MA + RSI |

### Analysis Tools
| Archivo | Descripción | Propósito |
|---------|-------------|-----------|
| `analysis/performance.py` | Métricas avanzadas | 20+ métricas |
| `analysis/reporting.py` | Generación de reportes | HTML + Gráficos |

### Configuration
| Archivo | Descripción | Configuraciones |
|---------|-------------|-----------------|
| `config/settings.py` | Todas las configuraciones | MT5, Backtest, Strategy |

## Recursos Externos

### MetaTrader 5
- [Documentación oficial MT5 Python](https://www.mql5.com/en/docs/python_metatrader5)
- [MQL5 Community](https://www.mql5.com/en/forum)
- [Descarga MT5](https://www.metatrader5.com/en/download)

### Python Libraries
- [Pandas Docs](https://pandas.pydata.org/docs/)
- [NumPy Docs](https://numpy.org/doc/)
- [Plotly Docs](https://plotly.com/python/)
- [QuantStats](https://github.com/ranaroussi/quantstats)

### Trading Education
- [Investopedia](https://www.investopedia.com/)
- [BabyPips](https://www.babypips.com/)
- [TradingView Education](https://www.tradingview.com/education/)

## FAQ Rápido

**¿Necesito MT5 instalado?**
→ No para empezar. Usa datos de muestra (opción 2 en examples).

**¿Cuánto tiempo lleva el backtest?**
→ Depende de datos. Típicamente segundos para 1 año de datos horarios.

**¿Puedo usar con otros brokers?**
→ Sí, si soportan MT5.

**¿Es gratis?**
→ Sí, el sistema es de código abierto.

**¿Funciona en Mac/Linux?**
→ Sí, pero MT5 requiere Wine en Mac/Linux.

**¿Puedo crear múltiples estrategias?**
→ Sí, hereda de `TradingStrategy` y crea las que quieras.

**¿Los resultados son reales?**
→ Son simulaciones basadas en datos históricos. No garantía de futuro.

**¿Cómo reporto bugs?**
→ Revisa logs, documentación, y describe el problema detalladamente.

## Checklist de Primeros Pasos

- [ ] Leer QUICKSTART.md
- [ ] Instalar Python y dependencias
- [ ] Ejecutar example_usage.py opción 2
- [ ] Revisar backtest_report_sample.html
- [ ] Experimentar con parámetros de estrategia
- [ ] Leer README.md secciones principales
- [ ] Crear una estrategia personalizada simple
- [ ] Ejecutar optimización básica
- [ ] Leer BEST_PRACTICES.md
- [ ] ¡Desarrollar tu propia estrategia ganadora!

## Contribuciones y Soporte

### ¿Encontraste un bug?
1. Revisa que no sea un error de configuración
2. Consulta INSTALLATION.md
3. Revisa los logs para más detalles

### ¿Quieres contribuir?
1. Mejora la documentación
2. Añade nuevas estrategias de ejemplo
3. Optimiza el código existente
4. Comparte tus resultados

## Versión del Sistema

**Versión Actual**: 1.0.0
**Última Actualización**: 2024
**Python Requerido**: 3.8+
**Licencia**: MIT

---

## 🎯 Camino Rápido al Éxito

```
1. QUICKSTART.md (5 min)
   ↓
2. Ejecutar ejemplo (2 min)
   ↓
3. Ver resultados (5 min)
   ↓
4. Experimentar parámetros (10 min)
   ↓
5. Crear estrategia simple (30 min)
   ↓
6. Leer BEST_PRACTICES.md (20 min)
   ↓
7. ¡Desarrollar estrategia ganadora!
```

**Total para estar productivo: ~1 hora**

---

**¡Feliz backtesting! 📊🚀**
