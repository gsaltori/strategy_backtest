# 📦 INSTALACIÓN Y CONFIGURACIÓN

## Requisitos del Sistema

### Sistema Operativo
- ✅ Windows 10/11 (recomendado para MT5)
- ✅ Linux (Ubuntu 20.04+)
- ✅ macOS (con Wine para MT5)

### Software Requerido
- **Python 3.8 o superior**
- **MetaTrader 5** (opcional, solo para datos reales)

## Instalación Paso a Paso

### 1. Verificar Python

```bash
python --version
```

Debe mostrar Python 3.8 o superior. Si no está instalado:
- Windows: [python.org/downloads](https://www.python.org/downloads/)
- Linux: `sudo apt-get install python3.8`
- macOS: `brew install python@3.8`

### 2. Crear Entorno Virtual (Recomendado)

```bash
# Crear entorno virtual
python -m venv venv

# Activar en Windows
venv\Scripts\activate

# Activar en Linux/macOS
source venv/bin/activate
```

### 3. Instalar Dependencias

```bash
cd strategy_backtest
pip install -r requirements.txt
```

### 4. Verificar Instalación

```bash
python -c "import MetaTrader5, pandas, numpy, plotly; print('✅ All dependencies installed')"
```

## Instalación de MetaTrader 5 (Opcional)

### Windows

1. Descargar MT5:
   - Visita: [metatrader5.com](https://www.metatrader5.com/en/download)
   - Descarga e instala el instalador

2. Configurar cuenta:
   - Abre MetaTrader 5
   - File > Open Account
   - Elige un broker o cuenta demo

3. Habilitar API:
   - Tools > Options > Expert Advisors
   - ✅ Marcar "Allow automated trading"
   - ✅ Marcar "Allow DLL imports"

### Linux

```bash
# Instalar Wine
sudo apt-get install wine64

# Descargar MT5
wget https://download.mql5.com/cdn/web/metaquotes.software.corp/mt5/mt5setup.exe

# Instalar
wine mt5setup.exe
```

### macOS

```bash
# Instalar Wine via Homebrew
brew install wine

# Descargar e instalar MT5
# Similar a Linux
```

## Configuración del Sistema

### 1. Configurar MT5 (si usas datos reales)

Edita `config/settings.py`:

```python
MT5Config(
    path='/path/to/terminal64.exe',  # Path a MT5
    login=12345678,                   # Tu login
    password='your_password',         # Tu password
    server='Broker-Server',           # Servidor del broker
)
```

### 2. Configurar Backtest

Edita `config/settings.py`:

```python
BacktestConfig(
    initial_capital=10000.0,    # Capital inicial
    commission_pct=0.0001,      # 0.01% comisión
    slippage_pct=0.0005,        # 0.05% slippage
    leverage=100.0,             # Apalancamiento
    use_spread=True             # Incluir spread
)
```

## Prueba de Instalación

### Test Básico

```bash
python example_usage.py
```

Selecciona opción 2 (datos de muestra).

### Test con MT5

```bash
python -c "import MetaTrader5 as mt5; print(mt5.initialize())"
```

Debe retornar `True` si MT5 está configurado correctamente.

## Solución de Problemas Comunes

### Error: "No module named 'MetaTrader5'"

```bash
pip install MetaTrader5==5.0.4518
```

### Error: "DLL load failed"

En Windows:
- Instala Visual C++ Redistributable
- Descarga desde: [microsoft.com/vcredist](https://aka.ms/vs/17/release/vc_redist.x64.exe)

### Error: "Cannot connect to MT5"

1. Verifica que MT5 esté ejecutándose
2. Verifica que "Allow automated trading" esté habilitado
3. Verifica credenciales en `config/settings.py`

### Plotly no muestra gráficos

```bash
pip install --upgrade plotly kaleido
```

### Pandas/Numpy errores

```bash
pip install --upgrade pandas numpy scipy
```

## Actualización del Sistema

```bash
cd strategy_backtest
git pull  # Si usas git
pip install -r requirements.txt --upgrade
```

## Desinstalación

```bash
# Desactivar entorno virtual
deactivate

# Eliminar entorno virtual
rm -rf venv

# Eliminar archivos del proyecto
rm -rf strategy_backtest
```

## Estructura de Archivos Post-Instalación

```
strategy_backtest/
├── config/                 ✅ Configuraciones
├── strategies/             ✅ Estrategias
├── analysis/               ✅ Análisis
├── data_manager.py         ✅ Gestor MT5
├── backtest_engine.py      ✅ Motor backtesting
├── example_usage.py        ✅ Ejemplos
├── requirements.txt        ✅ Dependencias
├── README.md              ✅ Documentación
├── QUICKSTART.md          ✅ Inicio rápido
└── INSTALLATION.md        ✅ Este archivo
```

## Configuración Avanzada

### Usar TA-Lib (Opcional)

TA-Lib proporciona más indicadores técnicos:

**Windows:**
```bash
# Descargar wheel desde:
# https://www.lfd.uci.edu/~gohlke/pythonlibs/#ta-lib
pip install TA_Lib‑0.4.28‑cp38‑cp38‑win_amd64.whl
```

**Linux:**
```bash
sudo apt-get install ta-lib
pip install ta-lib
```

**macOS:**
```bash
brew install ta-lib
pip install ta-lib
```

### Configurar Jupyter Notebook (Opcional)

Para análisis interactivo:

```bash
pip install jupyter notebook ipywidgets

# Ejecutar
jupyter notebook
```

Crea un nuevo notebook y:

```python
import sys
sys.path.append('/path/to/strategy_backtest')

from backtest_engine import BacktestEngine
from strategies.moving_average_crossover import MovingAverageCrossover
```

### Configurar VSCode (Opcional)

1. Instala VSCode: [code.visualstudio.com](https://code.visualstudio.com/)

2. Instala extensiones:
   - Python
   - Pylance
   - Jupyter

3. Abre la carpeta `strategy_backtest`

4. Configura el intérprete de Python:
   - Ctrl+Shift+P
   - "Python: Select Interpreter"
   - Selecciona el entorno virtual

## Permisos y Seguridad

### Windows Defender
Si Windows Defender bloquea la ejecución:
1. Windows Security > Virus & threat protection
2. Manage settings > Add exclusion
3. Añade la carpeta `strategy_backtest`

### Firewall
MT5 necesita acceso a internet:
1. Windows Firewall > Allow an app
2. Añade MetaTrader 5

## Performance y Optimización

### Para mejor rendimiento:

1. **Usar SSD** para datos
2. **Más RAM** (8GB mínimo, 16GB recomendado)
3. **Python 64-bit** (no 32-bit)
4. **Cerrar aplicaciones** innecesarias durante backtesting

### Optimizar código:

```python
# Usar numba para funciones críticas
from numba import jit

@jit(nopython=True)
def fast_calculation(data):
    # Tu código aquí
    pass
```

## Backup y Versionado

### Backup de configuraciones:

```bash
cp config/settings.py config/settings.backup.py
```

### Usar Git (recomendado):

```bash
cd strategy_backtest
git init
git add .
git commit -m "Initial commit"
```

## Soporte y Recursos

### Documentación
- README.md - Documentación completa
- QUICKSTART.md - Guía rápida
- Código comentado en todos los módulos

### Comunidad MT5
- [MQL5.com Community](https://www.mql5.com/)
- [MetaTrader 5 Forum](https://www.mql5.com/en/forum)

### Python Trading
- [QuantStats](https://github.com/ranaroussi/quantstats)
- [Backtrader](https://www.backtrader.com/)
- [Zipline](https://zipline.io/)

## Próximos Pasos

1. ✅ Completar instalación
2. ✅ Ejecutar ejemplo básico
3. ✅ Revisar documentación
4. ✅ Crear tu primera estrategia
5. ✅ Optimizar parámetros
6. ✅ ¡Empezar a hacer backtesting!

---

**¿Problemas? Revisa los logs en consola para mensajes de error detallados.**
