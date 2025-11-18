"""
Tests de validación del cálculo de lotaje correcto
Ejecutar: python test_position_sizing.py
"""
import sys
from pathlib import Path
from datetime import datetime

# Añadir el directorio raíz al path
sys.path.insert(0, str(Path(__file__).parent.parent))

from strategies.base_strategy import TradingStrategy, Signal
import logging

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class TestStrategy(TradingStrategy):
    """Estrategia de prueba simple"""
    
    def calculate_indicators(self, data):
        return data
    
    def generate_signals(self, data):
        return []


def test_forex_eurusd():
    """Test 1: Cálculo de lotaje para FOREX (EURUSD)"""
    print("\n" + "="*70)
    print("TEST 1: FOREX - EURUSD")
    print("="*70)
    
    # Setup
    symbol_info = {
        'name': 'EURUSD',
        'point': 0.00001,              # 5 decimales
        'trade_contract_size': 100000, # 1 lote estándar = 100,000 unidades
        'volume_min': 0.01,
        'volume_max': 100.0,
        'volume_step': 0.01
    }
    
    account_balance = 10000.0
    risk_per_trade = 0.02  # 2%
    current_price = 1.1000
    stop_loss = 1.0980     # 20 pips de distancia
    
    # Cálculo esperado manual
    risk_amount = 10000 * 0.02                        # $200
    stop_distance_pips = (1.1000 - 1.0980) / 0.00001  # 200 pips
    value_per_pip = 100000 * 0.00001                  # $1 por pip por lote
    expected_lots = 200 / (200 * 1)                   # 1.00 lotes
    
    print(f"   Configuración:")
    print(f"     - Balance: ${account_balance:,.2f}")
    print(f"     - Riesgo: {risk_per_trade*100}% = ${risk_amount:.2f}")
    print(f"     - Precio entrada: {current_price}")
    print(f"     - Stop Loss: {stop_loss} ({stop_distance_pips:.0f} pips)")
    print(f"     - Point size: {symbol_info['point']}")
    print(f"     - Contract size: {symbol_info['trade_contract_size']:,}")
    
    print(f"\n   Cálculo Manual:")
    print(f"     - Distancia Stop: {stop_distance_pips:.0f} pips")
    print(f"     - Valor por pip: ${value_per_pip:.2f}")
    print(f"     - Lotaje esperado: {expected_lots:.2f} lotes")
    
    # Ejecutar cálculo con la estrategia
    strategy = TestStrategy(
        name="Test FOREX",
        parameters={},
        risk_per_trade=risk_per_trade
    )
    
    signal = Signal(
        timestamp=datetime.now(),
        signal_type='BUY',
        price=current_price,
        stop_loss=stop_loss
    )
    
    position_size = strategy._calculate_position_size(
        signal, current_price, account_balance, symbol_info
    )
    
    print(f"\n   Resultado del Cálculo:")
    print(f"     - Lotaje calculado: {position_size:.2f} lotes")
    
    # Verificar
    tolerance = 0.01  # Tolerancia de 0.01 lotes
    if abs(position_size - expected_lots) < tolerance:
        print(f"\n   ✅ TEST PASSED: Lotaje correcto ({position_size:.2f} ≈ {expected_lots:.2f})")
        
        # Verificar riesgo real
        actual_risk = position_size * stop_distance_pips * value_per_pip
        print(f"   ✅ Riesgo real: ${actual_risk:.2f} ({(actual_risk/account_balance)*100:.2f}%)")
        
        return True
    else:
        print(f"\n   ❌ TEST FAILED: Lotaje incorrecto")
        print(f"      Esperado: {expected_lots:.2f} lotes")
        print(f"      Obtenido: {position_size:.2f} lotes")
        print(f"      Diferencia: {abs(position_size - expected_lots):.4f} lotes")
        return False


def test_gold_xauusd():
    """Test 2: Cálculo de lotaje para ORO (XAUUSD)"""
    print("\n" + "="*70)
    print("TEST 2: ORO - XAUUSD")
    print("="*70)
    
    # Setup
    symbol_info = {
        'name': 'XAUUSD',
        'point': 0.01,          # 2 decimales
        'trade_contract_size': 100,  # 100 onzas por lote
        'volume_min': 0.01,
        'volume_max': 100.0,
        'volume_step': 0.01
    }
    
    account_balance = 10000.0
    risk_per_trade = 0.02  # 2%
    current_price = 2650.00
    stop_loss = 2616.00    # 34 USD de distancia
    
    # Cálculo esperado manual
    risk_amount = 10000 * 0.02                    # $200
    stop_distance_pips = (2650.00 - 2616.00) / 0.01  # 3400 pips
    value_per_pip = 100 * 0.01                    # $1 por pip por lote
    expected_lots = 200 / (3400 * 1)              # 0.0588 lotes ≈ 0.06
    expected_lots_rounded = 0.06  # Redondeado al step 0.01
    
    print(f"   Configuración:")
    print(f"     - Balance: ${account_balance:,.2f}")
    print(f"     - Riesgo: {risk_per_trade*100}% = ${risk_amount:.2f}")
    print(f"     - Precio entrada: {current_price}")
    print(f"     - Stop Loss: {stop_loss} ({stop_distance_pips:.0f} pips = {current_price-stop_loss:.2f} USD)")
    print(f"     - Point size: {symbol_info['point']}")
    print(f"     - Contract size: {symbol_info['trade_contract_size']} onzas")
    
    print(f"\n   Cálculo Manual:")
    print(f"     - Distancia Stop: {stop_distance_pips:.0f} pips")
    print(f"     - Valor por pip: ${value_per_pip:.2f}")
    print(f"     - Lotaje calculado: {expected_lots:.4f} lotes")
    print(f"     - Lotaje redondeado: {expected_lots_rounded:.2f} lotes")
    
    # Ejecutar cálculo con la estrategia
    strategy = TestStrategy(
        name="Test GOLD",
        parameters={},
        risk_per_trade=risk_per_trade
    )
    
    signal = Signal(
        timestamp=datetime.now(),
        signal_type='BUY',
        price=current_price,
        stop_loss=stop_loss
    )
    
    position_size = strategy._calculate_position_size(
        signal, current_price, account_balance, symbol_info
    )
    
    print(f"\n   Resultado del Cálculo:")
    print(f"     - Lotaje calculado: {position_size:.2f} lotes")
    
    # Verificar (con tolerancia mayor por redondeo)
    tolerance = 0.02  # Tolerancia de 0.02 lotes
    if abs(position_size - expected_lots_rounded) < tolerance:
        print(f"\n   ✅ TEST PASSED: Lotaje correcto ({position_size:.2f} ≈ {expected_lots_rounded:.2f})")
        
        # Verificar riesgo real
        actual_risk = position_size * stop_distance_pips * value_per_pip
        print(f"   ✅ Riesgo real: ${actual_risk:.2f} ({(actual_risk/account_balance)*100:.2f}%)")
        
        return True
    else:
        print(f"\n   ❌ TEST FAILED: Lotaje incorrecto")
        print(f"      Esperado: ~{expected_lots_rounded:.2f} lotes")
        print(f"      Obtenido: {position_size:.2f} lotes")
        print(f"      Diferencia: {abs(position_size - expected_lots_rounded):.4f} lotes")
        return False


def test_index_us30():
    """Test 3: Cálculo de lotaje para ÍNDICES (US30)"""
    print("\n" + "="*70)
    print("TEST 3: ÍNDICE - US30 (Dow Jones)")
    print("="*70)
    
    # Setup
    symbol_info = {
        'name': 'US30',
        'point': 1.0,           # 1 punto
        'trade_contract_size': 1,    # 1 CFD por lote
        'volume_min': 0.01,
        'volume_max': 100.0,
        'volume_step': 0.01
    }
    
    account_balance = 10000.0
    risk_per_trade = 0.01  # 1%
    current_price = 44000.0
    stop_loss = 43900.0    # 100 puntos
    
    # Cálculo esperado manual
    risk_amount = 10000 * 0.01                # $100
    stop_distance_pips = (44000.0 - 43900.0) / 1.0  # 100 puntos
    value_per_pip = 1 * 1.0                   # $1 por punto por lote
    expected_lots = 100 / (100 * 1)           # 1.00 lotes
    
    print(f"   Configuración:")
    print(f"     - Balance: ${account_balance:,.2f}")
    print(f"     - Riesgo: {risk_per_trade*100}% = ${risk_amount:.2f}")
    print(f"     - Precio entrada: {current_price:,.0f}")
    print(f"     - Stop Loss: {stop_loss:,.0f} ({stop_distance_pips:.0f} puntos)")
    print(f"     - Point size: {symbol_info['point']}")
    print(f"     - Contract size: {symbol_info['trade_contract_size']} CFD")
    
    print(f"\n   Cálculo Manual:")
    print(f"     - Distancia Stop: {stop_distance_pips:.0f} puntos")
    print(f"     - Valor por punto: ${value_per_pip:.2f}")
    print(f"     - Lotaje esperado: {expected_lots:.2f} lotes")
    
    # Ejecutar cálculo con la estrategia
    strategy = TestStrategy(
        name="Test INDEX",
        parameters={},
        risk_per_trade=risk_per_trade
    )
    
    signal = Signal(
        timestamp=datetime.now(),
        signal_type='BUY',
        price=current_price,
        stop_loss=stop_loss
    )
    
    position_size = strategy._calculate_position_size(
        signal, current_price, account_balance, symbol_info
    )
    
    print(f"\n   Resultado del Cálculo:")
    print(f"     - Lotaje calculado: {position_size:.2f} lotes")
    
    # Verificar
    tolerance = 0.01
    if abs(position_size - expected_lots) < tolerance:
        print(f"\n   ✅ TEST PASSED: Lotaje correcto ({position_size:.2f} ≈ {expected_lots:.2f})")
        
        # Verificar riesgo real
        actual_risk = position_size * stop_distance_pips * value_per_pip
        print(f"   ✅ Riesgo real: ${actual_risk:.2f} ({(actual_risk/account_balance)*100:.2f}%)")
        
        return True
    else:
        print(f"\n   ❌ TEST FAILED: Lotaje incorrecto")
        print(f"      Esperado: {expected_lots:.2f} lotes")
        print(f"      Obtenido: {position_size:.2f} lotes")
        print(f"      Diferencia: {abs(position_size - expected_lots):.4f} lotes")
        return False


def test_comparison_old_vs_new():
    """Test 4: Comparación fórmula antigua vs nueva"""
    print("\n" + "="*70)
    print("TEST 4: COMPARACIÓN FÓRMULA ANTIGUA VS NUEVA (XAUUSD)")
    print("="*70)
    
    symbol_info = {
        'name': 'XAUUSD',
        'point': 0.01,
        'trade_contract_size': 100,
        'volume_min': 0.01,
        'volume_max': 100.0,
        'volume_step': 0.01
    }
    
    account_balance = 10000.0
    risk_per_trade = 0.02
    current_price = 2650.00
    stop_loss = 2616.00
    
    risk_amount = account_balance * risk_per_trade  # $200
    stop_distance_price = abs(current_price - stop_loss)  # 34 USD
    
    # FÓRMULA ANTIGUA (INCORRECTA)
    old_position_size = risk_amount / stop_distance_price
    old_risk = old_position_size * stop_distance_price  # NO considera contract_size
    
    # FÓRMULA NUEVA (CORRECTA)
    stop_distance_pips = stop_distance_price / symbol_info['point']
    value_per_pip = symbol_info['trade_contract_size'] * symbol_info['point']
    new_position_size = risk_amount / (stop_distance_pips * value_per_pip)
    new_position_size = round(new_position_size, 2)
    new_risk = new_position_size * stop_distance_pips * value_per_pip
    
    print(f"   Escenario:")
    print(f"     - Balance: ${account_balance:,.2f}")
    print(f"     - Riesgo objetivo: {risk_per_trade*100}% = ${risk_amount:.2f}")
    print(f"     - Precio: {current_price}")
    print(f"     - Stop Loss: {stop_loss} (Distancia: {stop_distance_price} USD)")
    
    print(f"\n   ❌ FÓRMULA ANTIGUA (INCORRECTA):")
    print(f"      position_size = risk_amount / risk_per_unit")
    print(f"      = {risk_amount:.2f} / {stop_distance_price:.2f}")
    print(f"      = {old_position_size:.2f} lotes")
    print(f"      Riesgo real: ${old_risk:.2f} ({(old_risk/account_balance)*100:.2f}%)")
    print(f"      ⚠️ Problema: ¡Ignora el tamaño del contrato!")
    
    print(f"\n   ✅ FÓRMULA NUEVA (CORRECTA):")
    print(f"      position_size = risk_amount / (stop_pips × value_per_pip)")
    print(f"      = {risk_amount:.2f} / ({stop_distance_pips:.0f} × {value_per_pip:.2f})")
    print(f"      = {new_position_size:.2f} lotes")
    print(f"      Riesgo real: ${new_risk:.2f} ({(new_risk/account_balance)*100:.2f}%)")
    print(f"      ✅ Correcto: Considera el tamaño del contrato")
    
    print(f"\n   📊 DIFERENCIA:")
    difference = abs(old_position_size - new_position_size)
    multiplier = old_position_size / new_position_size if new_position_size > 0 else 0
    print(f"      Diferencia absoluta: {difference:.2f} lotes")
    print(f"      Multiplier: {multiplier:.1f}x más grande con fórmula antigua")
    print(f"      Diferencia en riesgo: ${abs(old_risk - new_risk):,.2f}")
    
    if multiplier > 10:
        print(f"\n   ⚠️ PELIGRO: La fórmula antigua produce posiciones {multiplier:.0f}x más grandes!")
        print(f"      Esto podría causar pérdidas catastróficas en trading real.")
    
    return True


def run_all_tests():
    """Ejecutar todos los tests"""
    print("\n" + "="*70)
    print("🧪 INICIANDO SUITE DE TESTS DE CÁLCULO DE LOTAJE")
    print("="*70)
    
    results = []
    
    # Test 1: FOREX
    results.append(("FOREX (EURUSD)", test_forex_eurusd()))
    
    # Test 2: ORO
    results.append(("ORO (XAUUSD)", test_gold_xauusd()))
    
    # Test 3: ÍNDICE
    results.append(("ÍNDICE (US30)", test_index_us30()))
    
    # Test 4: Comparación
    results.append(("COMPARACIÓN", test_comparison_old_vs_new()))
    
    # Resumen
    print("\n" + "="*70)
    print("📊 RESUMEN DE TESTS")
    print("="*70)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"   {status} - {name}")
    
    print(f"\n   Total: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n   🎉 ¡Todos los tests pasaron correctamente!")
        print("   ✅ El cálculo de lotaje está funcionando bien.")
        return 0
    else:
        print("\n   ⚠️ Algunos tests fallaron.")
        print("   ❌ Revisa la implementación del cálculo de lotaje.")
        return 1


if __name__ == "__main__":
    import sys
    sys.exit(run_all_tests())
