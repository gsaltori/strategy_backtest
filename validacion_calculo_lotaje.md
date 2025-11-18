# 📊 Validación del Cálculo de Lotaje en Todas las Estrategias

## 🔍 Resumen Ejecutivo

He revisado todas las estrategias del proyecto y encontré **problemas significativos** en el cálculo de lotaje que afectan a todas las estrategias excepto NY Range Breakout.

### ⚠️ Hallazgos Principales

| Estrategia | Estado | Problema Principal |
|-----------|--------|-------------------|
| **NY Range Breakout** | ✅ CORRECTO | Usa lotaje fijo (0.01 lotes) - Simple y funcional |
| **Base Strategy** | ❌ INCORRECTO | Fórmula incorrecta para diferentes instrumentos |
| **Moving Average Crossover** | ❌ INCORRECTO | Hereda el cálculo incorrecto de Base Strategy |
| **Example Strategies** | ❌ INCORRECTO | Hereda el cálculo incorrecto de Base Strategy |

---

## 📋 Análisis Detallado por Estrategia

### 1. ✅ NY Range Breakout Strategy - CORRECTO

**Ubicación:** `ny_range_breakout_strategy.py`

**Código Actual:**
```python
# Para XAUUSD: usar 0.01 lotes (1 micro lote) como tamaño fijo por defecto
position_size = 0.01
```

**Evaluación:** ✅ **CORRECTO**

**Justificación:**
- Usa un tamaño fijo de 0.01 lotes (micro lote)
- Simple y predecible
- Apropiado para la naturaleza específica de la estrategia
- No requiere cálculos complejos de riesgo

**Recomendación:** 
- ✅ Mantener como está si la estrategia es para uso personal/educativo
- ⚠️ Si se desea escalar, considerar implementar gestión de riesgo dinámica

---

### 2. ❌ Base Strategy - INCORRECTO

**Ubicación:** `strategies/base_strategy.py`

**Código Actual:**
```python
def _calculate_position_size(
    self,
    signal: Signal,
    current_price: float,
    account_balance: float
) -> float:
    # Cantidad en riesgo
    risk_amount = account_balance * self.risk_per_trade
    
    # Calcular stop loss en precio si no existe
    if signal.stop_loss is None:
        stop_loss = self._calculate_stop_loss(signal, current_price)
    else:
        stop_loss = signal.stop_loss
    
    # Riesgo por unidad
    risk_per_unit = abs(current_price - stop_loss)
    
    if risk_per_unit == 0:
        logger.warning("Risk per unit is zero, using minimum position size")
        return 0.01
    
    # Tamaño de posición
    position_size = risk_amount / risk_per_unit  # ❌ FÓRMULA INCORRECTA
    
    # Redondear a 2 decimales
    position_size = round(position_size, 2)
    
    # Asegurar tamaño mínimo
    min_size = self.parameters.get('min_position_size', 0.01)
    position_size = max(position_size, min_size)
    
    # Asegurar tamaño máximo
    max_size = self.parameters.get('max_position_size', 100.0)
    position_size = min(position_size, max_size)
    
    return position_size
```

**Problema:** ❌ **FÓRMULA INCORRECTA**

La fórmula `position_size = risk_amount / risk_per_unit` es **incorrecta** porque:

1. **No considera el contract_size (tamaño del contrato)**
2. **No considera el valor del punto (point_value)**
3. **Produce resultados incorrectos para diferentes instrumentos**

---

## 🔧 Fórmula Correcta de Cálculo de Lotaje

### 📐 Fórmula Universal

```python
Lotes = Riesgo_USD / (Distancia_Stop_Pips × Valor_Por_Pip)

Donde:
- Riesgo_USD = Balance × Risk_Percent
- Distancia_Stop_Pips = |Precio_Entrada - Stop_Loss| / Point_Size
- Valor_Por_Pip = Contract_Size × Point_Size
```

### 🎯 Ejemplos por Instrumento

#### Ejemplo 1: FOREX (EURUSD)
```python
Balance: $10,000
Risk: 2% = $200
Precio: 1.1000
Stop Loss: 1.0980
Point Size: 0.00001 (5 decimales)
Contract Size: 100,000

# Cálculo:
Distancia_Stop = |1.1000 - 1.0980| / 0.00001 = 200 pips
Valor_Por_Pip = 100,000 × 0.00001 = 1 USD por pip por lote
Lotes = 200 USD / (200 pips × 1 USD/pip) = 1.00 lotes

# Verificación:
# Si precio va de 1.1000 a 1.0980 (200 pips)
# Pérdida = 200 pips × 1 USD/pip × 1 lote = $200 ✅
```

#### Ejemplo 2: ORO (XAUUSD)
```python
Balance: $10,000
Risk: 2% = $200
Precio: 2,650.00
Stop Loss: 2,616.00
Point Size: 0.01 (2 decimales)
Contract Size: 100 onzas

# Cálculo:
Distancia_Stop = |2650.00 - 2616.00| / 0.01 = 3,400 pips (34 USD)
Valor_Por_Pip = 100 × 0.01 = 1 USD por pip por lote
Lotes = 200 USD / (3,400 pips × 1 USD/pip) = 0.0588 lotes

# Verificación:
# Si precio va de 2650 a 2616 (34 USD)
# Pérdida = 34 USD × 0.0588 lotes × 100 onzas = $199.92 ≈ $200 ✅
```

#### Ejemplo 3: ÍNDICES (US30)
```python
Balance: $10,000
Risk: 1% = $100
Precio: 44,000
Stop Loss: 43,900
Point Size: 1.0
Contract Size: 1 (CFD)

# Cálculo:
Distancia_Stop = |44000 - 43900| / 1.0 = 100 puntos
Valor_Por_Punto = 1 × 1.0 = 1 USD por punto por lote
Lotes = 100 USD / (100 puntos × 1 USD/punto) = 1.00 lotes

# Verificación:
# Si precio va de 44000 a 43900 (100 puntos)
# Pérdida = 100 puntos × 1 USD/punto × 1 lote = $100 ✅
```

---

## 🔨 Código Corregido

### Implementación Correcta para Base Strategy

```python
def _calculate_position_size(
    self,
    signal: Signal,
    current_price: float,
    account_balance: float,
    symbol_info: Optional[Dict] = None
) -> float:
    """
    Calcula el tamaño de la posición basado en el riesgo
    
    Args:
        signal: Señal de trading
        current_price: Precio actual
        account_balance: Balance de la cuenta
        symbol_info: Información del símbolo (requerido para cálculo correcto)
        
    Returns:
        Tamaño de la posición en lotes
    """
    # Cantidad en riesgo (USD)
    risk_amount = account_balance * self.risk_per_trade
    
    # Calcular stop loss en precio si no existe
    if signal.stop_loss is None:
        stop_loss = self._calculate_stop_loss(signal, current_price)
    else:
        stop_loss = signal.stop_loss
    
    # Validar que tenemos información del símbolo
    if symbol_info is None:
        logger.warning("symbol_info not provided, using default values")
        symbol_info = {
            'point': 0.00001,
            'trade_contract_size': 100000
        }
    
    # Obtener información del instrumento
    point_size = symbol_info.get('point', 0.00001)
    contract_size = symbol_info.get('trade_contract_size', 100000)
    
    # Calcular distancia del stop en pips/puntos
    stop_distance_price = abs(current_price - stop_loss)
    stop_distance_pips = stop_distance_price / point_size
    
    if stop_distance_pips == 0:
        logger.warning("Stop distance is zero, using minimum position size")
        return symbol_info.get('volume_min', 0.01)
    
    # Calcular valor por pip
    value_per_pip = contract_size * point_size
    
    # FÓRMULA CORRECTA: Lotes = Riesgo / (Distancia_Stop_Pips × Valor_Por_Pip)
    position_size = risk_amount / (stop_distance_pips * value_per_pip)
    
    # Aplicar límites del broker
    min_size = symbol_info.get('volume_min', 0.01)
    max_size = symbol_info.get('volume_max', 100.0)
    volume_step = symbol_info.get('volume_step', 0.01)
    
    # Redondear al step válido
    position_size = round(position_size / volume_step) * volume_step
    
    # Aplicar límites
    position_size = max(min_size, min(position_size, max_size))
    
    # Redondear a 2 decimales
    position_size = round(position_size, 2)
    
    logger.info(
        f"Position size calculated: {position_size} lots "
        f"(Risk: ${risk_amount:.2f}, Stop: {stop_distance_pips:.1f} pips)"
    )
    
    return position_size
```

### Llamada Actualizada en manage_risk

```python
def manage_risk(
    self,
    signal: Signal,
    current_price: float,
    account_balance: float,
    symbol_info: Optional[Dict] = None  # ← Añadir parámetro
) -> Signal:
    """
    Gestiona el riesgo de una señal
    
    Args:
        signal: Señal de trading
        current_price: Precio actual
        account_balance: Balance de la cuenta
        symbol_info: Información del símbolo (requerido para cálculo correcto)
        
    Returns:
        Señal con parámetros de riesgo actualizados
    """
    # Calcular stop loss si no está definido
    if signal.stop_loss is None:
        signal.stop_loss = self._calculate_stop_loss(signal, current_price)
    
    # Calcular take profit si no está definido
    if signal.take_profit is None:
        signal.take_profit = self._calculate_take_profit(signal, current_price)
    
    # Calcular tamaño de posición basado en riesgo
    signal.position_size = self._calculate_position_size(
        signal, current_price, account_balance, symbol_info  # ← Pasar symbol_info
    )
    
    return signal
```

---

## 🧪 Casos de Prueba

### Test 1: FOREX - EURUSD

```python
def test_position_size_forex():
    # Setup
    symbol_info = {
        'name': 'EURUSD',
        'point': 0.00001,
        'trade_contract_size': 100000,
        'volume_min': 0.01,
        'volume_max': 100.0,
        'volume_step': 0.01
    }
    
    account_balance = 10000.0
    risk_per_trade = 0.02  # 2%
    current_price = 1.1000
    stop_loss = 1.0980  # 20 pips
    
    # Cálculo esperado
    risk_amount = 10000 * 0.02  # $200
    stop_distance_pips = (1.1000 - 1.0980) / 0.00001  # 200 pips
    value_per_pip = 100000 * 0.00001  # $1
    expected_lots = 200 / (200 * 1)  # 1.00 lotes
    
    # Ejecutar
    strategy = BaseStrategy()
    signal = Signal(
        timestamp=datetime.now(),
        signal_type='BUY',
        price=current_price,
        stop_loss=stop_loss
    )
    
    position_size = strategy._calculate_position_size(
        signal, current_price, account_balance, symbol_info
    )
    
    # Verificar
    assert abs(position_size - expected_lots) < 0.01, \
        f"Expected {expected_lots}, got {position_size}"
    
    print(f"✅ Test FOREX passed: {position_size} lots")
```

### Test 2: ORO - XAUUSD

```python
def test_position_size_gold():
    # Setup
    symbol_info = {
        'name': 'XAUUSD',
        'point': 0.01,
        'trade_contract_size': 100,
        'volume_min': 0.01,
        'volume_max': 100.0,
        'volume_step': 0.01
    }
    
    account_balance = 10000.0
    risk_per_trade = 0.02  # 2%
    current_price = 2650.00
    stop_loss = 2616.00  # 34 USD de distancia
    
    # Cálculo esperado
    risk_amount = 10000 * 0.02  # $200
    stop_distance_pips = (2650.00 - 2616.00) / 0.01  # 3400 pips
    value_per_pip = 100 * 0.01  # $1
    expected_lots = 200 / (3400 * 1)  # 0.0588 lotes
    
    # Ejecutar
    strategy = BaseStrategy()
    signal = Signal(
        timestamp=datetime.now(),
        signal_type='BUY',
        price=current_price,
        stop_loss=stop_loss
    )
    
    position_size = strategy._calculate_position_size(
        signal, current_price, account_balance, symbol_info
    )
    
    # Verificar (redondea a step 0.01)
    assert abs(position_size - 0.06) < 0.01, \
        f"Expected ~0.06, got {position_size}"
    
    print(f"✅ Test GOLD passed: {position_size} lots")
```

### Test 3: ÍNDICES - US30

```python
def test_position_size_index():
    # Setup
    symbol_info = {
        'name': 'US30',
        'point': 1.0,
        'trade_contract_size': 1,
        'volume_min': 0.01,
        'volume_max': 100.0,
        'volume_step': 0.01
    }
    
    account_balance = 10000.0
    risk_per_trade = 0.01  # 1%
    current_price = 44000.0
    stop_loss = 43900.0  # 100 puntos
    
    # Cálculo esperado
    risk_amount = 10000 * 0.01  # $100
    stop_distance_pips = (44000.0 - 43900.0) / 1.0  # 100 puntos
    value_per_pip = 1 * 1.0  # $1
    expected_lots = 100 / (100 * 1)  # 1.00 lotes
    
    # Ejecutar
    strategy = BaseStrategy()
    signal = Signal(
        timestamp=datetime.now(),
        signal_type='BUY',
        price=current_price,
        stop_loss=stop_loss
    )
    
    position_size = strategy._calculate_position_size(
        signal, current_price, account_balance, symbol_info
    )
    
    # Verificar
    assert abs(position_size - expected_lots) < 0.01, \
        f"Expected {expected_lots}, got {position_size}"
    
    print(f"✅ Test INDEX passed: {position_size} lots")
```

---

## 📊 Tabla Comparativa: Antes vs Después

### Ejemplo con XAUUSD

| Escenario | Fórmula Antigua | Fórmula Correcta | Diferencia |
|-----------|----------------|------------------|------------|
| Balance: $10,000 | | | |
| Risk: 2% ($200) | | | |
| Precio: 2,650 | | | |
| Stop Loss: 2,616 (34 USD) | | | |
| **Resultado** | **5.88 lotes** ❌ | **0.06 lotes** ✅ | **98x más grande!** |
| **Riesgo Real** | **$11,992** 💀 | **$204** ✅ | **Pérdida total!** |

### Cálculos:

**Fórmula Antigua (INCORRECTA):**
```python
risk_per_unit = |2650 - 2616| = 34
position_size = 200 / 34 = 5.88 lotes ❌

# Verificación del riesgo:
# 5.88 lotes × 100 onzas × 34 USD = $19,992 💀
# ¡¡Pérdida potencial MUCHO mayor al balance!!
```

**Fórmula Correcta:**
```python
stop_distance_pips = 34 / 0.01 = 3,400 pips
value_per_pip = 100 × 0.01 = 1 USD
position_size = 200 / (3400 × 1) = 0.0588 ≈ 0.06 lotes ✅

# Verificación del riesgo:
# 0.06 lotes × 100 onzas × 34 USD = $204 ✅
# ¡Riesgo controlado al 2%!
```

---

## ⚠️ Impacto en Estrategias Existentes

### 1. Moving Average Crossover
- **Afectado:** ✅ Sí
- **Razón:** Hereda de Base Strategy
- **Solución:** Aplicar la corrección en Base Strategy

### 2. Example Strategies (RSI, Bollinger, etc.)
- **Afectado:** ✅ Sí
- **Razón:** Todas heredan de Base Strategy
- **Solución:** Aplicar la corrección en Base Strategy

### 3. NY Range Breakout
- **Afectado:** ❌ No
- **Razón:** No usa _calculate_position_size, tiene lotaje fijo
- **Solución:** Ninguna necesaria (o implementar gestión de riesgo opcional)

---

## 🚀 Plan de Acción Recomendado

### Prioridad ALTA

1. **Corregir Base Strategy** (strategies/base_strategy.py)
   - ✅ Implementar la fórmula correcta
   - ✅ Añadir parámetro `symbol_info`
   - ✅ Actualizar método `manage_risk`
   - ✅ Añadir logging detallado

2. **Actualizar BacktestEngine** (backtest_engine.py)
   - ✅ Pasar `symbol_info` a `strategy.manage_risk()`
   - ✅ Verificar que se propaga correctamente

3. **Crear Suite de Tests**
   - ✅ Test para FOREX
   - ✅ Test para ORO
   - ✅ Test para ÍNDICES
   - ✅ Test para CRIPTOS (si aplica)

### Prioridad MEDIA

4. **Actualizar Documentación**
   - Explicar la fórmula correcta
   - Añadir ejemplos por instrumento
   - Actualizar BEST_PRACTICES.md

5. **Añadir Validaciones**
   - Verificar que risk no exceda límites razonables
   - Alertar si position_size es inusualmente grande/pequeña
   - Validar symbol_info antes de calcular

### Prioridad BAJA (Opcional)

6. **Mejorar NY Range Breakout**
   - Implementar gestión de riesgo dinámica opcional
   - Mantener opción de lotaje fijo para simplicidad

7. **Añadir Calculadora de Position Size**
   - Herramienta standalone para calcular lotes
   - Útil para planificación de trades

---

## 📝 Código de Corrección Completo

### Archivo: strategies/base_strategy.py

```python
def _calculate_position_size(
    self,
    signal: Signal,
    current_price: float,
    account_balance: float,
    symbol_info: Optional[Dict] = None
) -> float:
    """
    Calcula el tamaño de la posición basado en el riesgo usando fórmula correcta.
    
    Fórmula: Lotes = Riesgo_USD / (Distancia_Stop_Pips × Valor_Por_Pip)
    
    Args:
        signal: Señal de trading
        current_price: Precio actual
        account_balance: Balance de la cuenta
        symbol_info: Información del símbolo con:
            - point: Tamaño del punto (ej: 0.00001 para EURUSD)
            - trade_contract_size: Tamaño del contrato (ej: 100000 para EURUSD)
            - volume_min: Volumen mínimo permitido
            - volume_max: Volumen máximo permitido
            - volume_step: Incremento de volumen
            
    Returns:
        Tamaño de la posición en lotes
        
    Examples:
        >>> # EURUSD: Balance $10k, Risk 2%, Entry 1.1000, SL 1.0980
        >>> symbol_info = {'point': 0.00001, 'trade_contract_size': 100000}
        >>> position_size = strategy._calculate_position_size(signal, 1.1000, 10000, symbol_info)
        >>> # Resultado: 1.00 lotes (200 USD de riesgo / 200 pips × $1/pip)
        
        >>> # XAUUSD: Balance $10k, Risk 2%, Entry 2650, SL 2616
        >>> symbol_info = {'point': 0.01, 'trade_contract_size': 100}
        >>> position_size = strategy._calculate_position_size(signal, 2650, 10000, symbol_info)
        >>> # Resultado: 0.06 lotes (200 USD de riesgo / 3400 pips × $1/pip)
    """
    # Cantidad en riesgo (USD)
    risk_amount = account_balance * self.risk_per_trade
    
    # Calcular stop loss en precio si no existe
    if signal.stop_loss is None:
        stop_loss = self._calculate_stop_loss(signal, current_price)
    else:
        stop_loss = signal.stop_loss
    
    # Validar que tenemos información del símbolo
    if symbol_info is None:
        logger.warning(
            "symbol_info not provided to _calculate_position_size. "
            "Using default values for FOREX. This may produce incorrect results "
            "for other instruments like GOLD, INDICES, etc."
        )
        symbol_info = {
            'point': 0.00001,
            'trade_contract_size': 100000,
            'volume_min': 0.01,
            'volume_max': 100.0,
            'volume_step': 0.01
        }
    
    # Obtener información del instrumento
    point_size = symbol_info.get('point', 0.00001)
    contract_size = symbol_info.get('trade_contract_size', 100000)
    
    # Calcular distancia del stop en pips/puntos
    stop_distance_price = abs(current_price - stop_loss)
    stop_distance_pips = stop_distance_price / point_size
    
    # Validación: stop distance debe ser mayor a 0
    if stop_distance_pips == 0:
        logger.error(
            f"Stop distance is zero! Entry: {current_price}, SL: {stop_loss}. "
            f"Using minimum position size."
        )
        return symbol_info.get('volume_min', 0.01)
    
    # Calcular valor por pip (cuánto vale 1 pip de movimiento por 1 lote)
    value_per_pip = contract_size * point_size
    
    # FÓRMULA CORRECTA
    # Lotes = Riesgo_USD / (Distancia_Stop_Pips × Valor_Por_Pip)
    position_size_calculated = risk_amount / (stop_distance_pips * value_per_pip)
    
    # Obtener límites del broker
    min_size = symbol_info.get('volume_min', 0.01)
    max_size = symbol_info.get('volume_max', 100.0)
    volume_step = symbol_info.get('volume_step', 0.01)
    
    # Redondear al step válido del broker
    position_size = round(position_size_calculated / volume_step) * volume_step
    
    # Aplicar límites del broker
    position_size = max(min_size, min(position_size, max_size))
    
    # Redondear a 2 decimales para claridad
    position_size = round(position_size, 2)
    
    # Logging detallado
    logger.info(
        f"Position size calculation: "
        f"Risk=${risk_amount:.2f} ({self.risk_per_trade*100:.1f}%), "
        f"Stop={stop_distance_pips:.1f} pips, "
        f"Value/pip=${value_per_pip:.2f}, "
        f"Result={position_size:.2f} lots"
    )
    
    # Validación adicional: alertar si el tamaño es inusual
    if position_size == max_size:
        logger.warning(
            f"Position size hit maximum limit of {max_size} lots. "
            f"Consider reducing risk or increasing stop distance."
        )
    
    if position_size == min_size and position_size_calculated < min_size:
        logger.warning(
            f"Position size hit minimum limit of {min_size} lots. "
            f"Calculated size was {position_size_calculated:.4f} lots. "
            f"Actual risk may be higher than intended."
        )
    
    # Calcular el riesgo real que se va a tomar
    actual_risk = position_size * stop_distance_pips * value_per_pip
    actual_risk_pct = (actual_risk / account_balance) * 100
    
    logger.info(
        f"Actual risk: ${actual_risk:.2f} ({actual_risk_pct:.2f}% of balance)"
    )
    
    # Alerta si el riesgo real difiere significativamente del objetivo
    risk_difference = abs(actual_risk - risk_amount)
    if risk_difference > risk_amount * 0.1:  # Más de 10% de diferencia
        logger.warning(
            f"Actual risk (${actual_risk:.2f}) differs from target "
            f"(${risk_amount:.2f}) by ${risk_difference:.2f}"
        )
    
    return position_size


def manage_risk(
    self,
    signal: Signal,
    current_price: float,
    account_balance: float,
    symbol_info: Optional[Dict] = None
) -> Signal:
    """
    Gestiona el riesgo de una señal calculando SL, TP y position size.
    
    Args:
        signal: Señal de trading
        current_price: Precio actual
        account_balance: Balance de la cuenta
        symbol_info: Información del símbolo (REQUERIDO para cálculo correcto)
        
    Returns:
        Señal con parámetros de riesgo actualizados
    """
    # Calcular stop loss si no está definido
    if signal.stop_loss is None:
        signal.stop_loss = self._calculate_stop_loss(signal, current_price)
    
    # Calcular take profit si no está definido
    if signal.take_profit is None:
        signal.take_profit = self._calculate_take_profit(signal, current_price)
    
    # Calcular tamaño de posición basado en riesgo
    # IMPORTANTE: Pasar symbol_info para cálculo correcto
    signal.position_size = self._calculate_position_size(
        signal, 
        current_price, 
        account_balance,
        symbol_info  # ← CRÍTICO: Pasar información del símbolo
    )
    
    return signal
```

### Archivo: backtest_engine.py

Actualizar en el método `_open_position`:

```python
def _open_position(
    self,
    signal: Signal,
    bar: pd.Series,
    symbol_info: Optional[Dict],
    strategy: TradingStrategy
) -> None:
    """
    Abre una nueva posición
    """
    # Aplicar gestión de riesgo
    # IMPORTANTE: Pasar symbol_info a manage_risk
    signal = strategy.manage_risk(
        signal, 
        bar['close'], 
        self.current_balance,
        symbol_info  # ← Pasar symbol_info
    )
    
    # ... resto del código ...
```

---

## ✅ Checklist de Validación

Después de aplicar las correcciones, verificar:

- [ ] La fórmula usa `stop_distance_pips` (no `risk_per_unit` directamente)
- [ ] Se considera el `contract_size` del instrumento
- [ ] Se considera el `point_size` del instrumento
- [ ] `symbol_info` se pasa a `manage_risk()` en BacktestEngine
- [ ] Los tests pasan para FOREX, ORO e ÍNDICES
- [ ] El logging muestra cálculos detallados
- [ ] Se validan límites min/max del broker
- [ ] Se alerta si el riesgo real difiere del objetivo
- [ ] La documentación está actualizada

---

## 📚 Referencias y Recursos

### Documentación Relevante
- [MetaTrader 5 - SymbolInfo](https://www.mql5.com/en/docs/constants/environment_state/marketinfoconstants)
- [Position Sizing en Trading](https://www.investopedia.com/articles/trading/06/positionsizing.asp)
- [Risk Management](https://www.babypips.com/learn/forex/risk-management)

### Fórmulas por Tipo de Instrumento

| Instrumento | Point Size | Contract Size | Ejemplo |
|-------------|-----------|---------------|---------|
| EURUSD | 0.00001 | 100,000 | 1 lote = $100k |
| GBPUSD | 0.00001 | 100,000 | 1 lote = £100k |
| XAUUSD | 0.01 | 100 | 1 lote = 100 oz |
| XAGUSD | 0.001 | 5000 | 1 lote = 5000 oz |
| US30 | 1.0 | 1 | 1 lote = 1 CFD |
| SPX500 | 0.01 | 1 | 1 lote = 1 CFD |
| BTCUSD | 1.0 | 1 | 1 lote = 1 BTC |

---

## 🎯 Conclusión

**Resumen de Problemas Encontrados:**

1. ✅ **NY Range Breakout**: Correcto (usa lotaje fijo)
2. ❌ **Base Strategy**: Fórmula incorrecta que no considera contract_size ni point_value
3. ❌ **Estrategias heredadas**: Todas afectadas por el problema de Base Strategy

**Impacto:**
- **CRÍTICO**: Puede resultar en posiciones 10-100x más grandes de lo esperado
- **Riesgo real**: Mucho mayor al porcentaje configurado
- **Aplicable a**: TODAS las estrategias excepto NY Range Breakout

**Solución:**
- Implementar la fórmula correcta en Base Strategy
- Pasar `symbol_info` a través de toda la cadena de llamadas
- Validar con tests comprehensivos

**Prioridad:** 🔴 **ALTA - Corregir inmediatamente antes de usar en producción**

---

## 📧 Contacto

Si tienes dudas sobre esta validación o necesitas ayuda implementando las correcciones, no dudes en preguntar.

**Documento creado:** 2025-11-17
**Versión:** 1.0
**Estado:** ⚠️ CORRECCIONES PENDIENTES
