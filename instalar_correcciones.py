#!/usr/bin/env python3
"""
Script de instalación automática de las correcciones de cálculo de lotaje
Ejecutar: python instalar_correcciones.py
"""
import os
import shutil
from pathlib import Path
from datetime import datetime


def print_header(text):
    """Imprime un encabezado formateado"""
    print("\n" + "="*70)
    print(text)
    print("="*70)


def print_step(number, text):
    """Imprime un paso"""
    print(f"\n{number}. {text}")


def backup_file(filepath):
    """Crea un backup de un archivo"""
    if not filepath.exists():
        print(f"   ⚠️ Archivo no encontrado: {filepath}")
        return False
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = filepath.parent / f"{filepath.name}.backup_{timestamp}"
    
    try:
        shutil.copy2(filepath, backup_path)
        print(f"   ✅ Backup creado: {backup_path.name}")
        return True
    except Exception as e:
        print(f"   ❌ Error creando backup: {e}")
        return False


def install_base_strategy():
    """Instala la versión corregida de base_strategy.py"""
    print_step(1, "Instalando base_strategy.py corregido...")
    
    source = Path("archivos_corregidos/strategies/base_strategy.py")
    target = Path("strategies/base_strategy.py")
    
    if not source.exists():
        print(f"   ❌ Archivo fuente no encontrado: {source}")
        return False
    
    if not target.parent.exists():
        print(f"   ⚠️ Directorio 'strategies' no existe. Creándolo...")
        target.parent.mkdir(parents=True, exist_ok=True)
    
    # Backup
    if target.exists():
        if not backup_file(target):
            return False
    
    # Copiar archivo
    try:
        shutil.copy2(source, target)
        print(f"   ✅ {target} actualizado correctamente")
        return True
    except Exception as e:
        print(f"   ❌ Error copiando archivo: {e}")
        return False


def patch_backtest_engine():
    """Aplica el parche a backtest_engine.py"""
    print_step(2, "Parcheando backtest_engine.py...")
    
    filepath = Path("backtest_engine.py")
    
    if not filepath.exists():
        print(f"   ❌ Archivo no encontrado: {filepath}")
        print(f"   ℹ️ Deberás crear o ubicar este archivo manualmente")
        return False
    
    # Backup
    if not backup_file(filepath):
        return False
    
    # Leer contenido
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"   ❌ Error leyendo archivo: {e}")
        return False
    
    # Verificar si ya está parcheado
    if "symbol_info  # ← CRÍTICO" in content or "symbol_info  # CRÍTICO" in content:
        print(f"   ℹ️ El archivo ya parece estar parcheado")
        return True
    
    # Buscar la línea a reemplazar
    old_line = "signal = strategy.manage_risk(signal, bar['close'], self.current_balance)"
    
    if old_line not in content:
        print(f"   ⚠️ No se encontró la línea exacta a reemplazar")
        print(f"   ℹ️ Deberás aplicar el parche manualmente")
        print(f"   ℹ️ Ver: archivos_corregidos/PARCHE_backtest_engine.txt")
        return False
    
    # Aplicar el parche
    new_lines = """signal = strategy.manage_risk(
            signal, 
            bar['close'], 
            self.current_balance,
            symbol_info  # ← CRÍTICO: Pasar información del símbolo
        )"""
    
    content = content.replace(old_line, new_lines)
    
    # Guardar
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"   ✅ {filepath} parcheado correctamente")
        return True
    except Exception as e:
        print(f"   ❌ Error escribiendo archivo: {e}")
        return False


def run_tests():
    """Ejecuta los tests de validación"""
    print_step(3, "Ejecutando tests de validación...")
    
    test_file = Path("archivos_corregidos/test_position_sizing.py")
    
    if not test_file.exists():
        print(f"   ❌ Archivo de tests no encontrado: {test_file}")
        return False
    
    print(f"   🧪 Ejecutando tests...")
    
    import subprocess
    try:
        result = subprocess.run(
            ['python', str(test_file)],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        # Mostrar output
        print(result.stdout)
        
        if result.returncode == 0:
            print(f"\n   ✅ Todos los tests pasaron correctamente")
            return True
        else:
            print(f"\n   ❌ Algunos tests fallaron")
            if result.stderr:
                print(f"   Error: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print(f"   ❌ Tests tomaron demasiado tiempo (timeout)")
        return False
    except Exception as e:
        print(f"   ❌ Error ejecutando tests: {e}")
        return False


def verify_installation():
    """Verifica que los archivos estén correctamente instalados"""
    print_step(4, "Verificando instalación...")
    
    checks = []
    
    # Verificar base_strategy.py
    base_strategy = Path("strategies/base_strategy.py")
    if base_strategy.exists():
        with open(base_strategy, 'r', encoding='utf-8') as f:
            content = f.read()
            if "✅ FÓRMULA CORREGIDA" in content:
                print(f"   ✅ base_strategy.py está correctamente actualizado")
                checks.append(True)
            else:
                print(f"   ⚠️ base_strategy.py existe pero puede no estar actualizado")
                checks.append(False)
    else:
        print(f"   ❌ base_strategy.py no encontrado")
        checks.append(False)
    
    # Verificar backtest_engine.py
    backtest_engine = Path("backtest_engine.py")
    if backtest_engine.exists():
        with open(backtest_engine, 'r', encoding='utf-8') as f:
            content = f.read()
            if "symbol_info  #" in content and "manage_risk" in content:
                print(f"   ✅ backtest_engine.py parece estar parcheado")
                checks.append(True)
            else:
                print(f"   ⚠️ backtest_engine.py puede necesitar el parche")
                checks.append(False)
    else:
        print(f"   ⚠️ backtest_engine.py no encontrado")
        checks.append(False)
    
    return all(checks)


def show_next_steps():
    """Muestra los siguientes pasos"""
    print_header("📋 PRÓXIMOS PASOS")
    
    print("""
1. Revisar los backups creados (*.backup_*)
   - En caso de problemas, puedes restaurar desde el backup

2. Ejecutar un backtest de prueba:
   python example_usage.py

3. Verificar el logging durante el backtest:
   - Buscar: "📊 Position size calculation"
   - Buscar: "💰 Actual risk"
   - Verificar que los valores sean razonables

4. Si algo no funciona:
   - Restaurar desde backup
   - Revisar: archivos_corregidos/README.md
   - Revisar: archivos_corregidos/validacion_calculo_lotaje.md

5. Una vez validado, probar en cuenta DEMO antes de real
""")


def main():
    """Función principal"""
    print_header("🔧 INSTALADOR DE CORRECCIONES - Cálculo de Lotaje")
    
    print("""
Este script instalará las correcciones necesarias para arreglar el
cálculo de lotaje incorrecto en el sistema de backtesting.

⚠️ IMPORTANTE:
- Se crearán backups automáticos de los archivos modificados
- Los tests de validación se ejecutarán automáticamente
- Asegúrate de estar en el directorio raíz del proyecto

¿Deseas continuar? (s/n): """, end='')
    
    response = input().strip().lower()
    if response not in ['s', 'si', 'sí', 'y', 'yes']:
        print("\n❌ Instalación cancelada")
        return 1
    
    results = []
    
    # Paso 1: Instalar base_strategy.py
    results.append(("Instalar base_strategy.py", install_base_strategy()))
    
    # Paso 2: Parchear backtest_engine.py
    results.append(("Parchear backtest_engine.py", patch_backtest_engine()))
    
    # Paso 3: Ejecutar tests
    results.append(("Ejecutar tests", run_tests()))
    
    # Paso 4: Verificar
    results.append(("Verificar instalación", verify_installation()))
    
    # Resumen
    print_header("📊 RESUMEN DE INSTALACIÓN")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅" if result else "❌"
        print(f"   {status} {name}")
    
    print(f"\n   Total: {passed}/{total} pasos completados exitosamente")
    
    if passed == total:
        print("\n   🎉 ¡Instalación completada exitosamente!")
        show_next_steps()
        return 0
    else:
        print("\n   ⚠️ La instalación se completó con algunos errores.")
        print("   Revisa los mensajes arriba para más detalles.")
        print("\n   ℹ️ Puedes aplicar las correcciones manualmente:")
        print("   - Ver: archivos_corregidos/README.md")
        print("   - Ver: archivos_corregidos/PARCHE_backtest_engine.txt")
        return 1


if __name__ == "__main__":
    import sys
    sys.exit(main())
