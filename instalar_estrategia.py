"""
Script de Instalación Automática
Copia los archivos corregidos a sus ubicaciones correctas

Uso: python instalar_estrategia.py
"""

import os
import shutil
from pathlib import Path


def instalar_estrategia():
    """Instala la estrategia en el proyecto"""
    
    print("\n" + "="*70)
    print("📦 INSTALACIÓN AUTOMÁTICA - NY Range Breakout")
    print("="*70)
    
    # Detectar directorio actual
    current_dir = Path.cwd()
    print(f"\n📂 Directorio actual: {current_dir}")
    
    # Verificar que estamos en el directorio correcto
    if not (current_dir / "strategies").exists():
        print("\n❌ Error: No se encuentra la carpeta 'strategies'")
        print("   Asegúrate de ejecutar este script desde el directorio raíz del proyecto")
        print(f"   Directorio raíz esperado: strategy_backtest/")
        return False
    
    # Archivos a copiar
    archivos = {
        'ny_range_breakout_strategy.py': 'strategies/ny_range_breakout_strategy.py',
        'run_ny_range_backtest.py': 'run_ny_range_backtest.py',
        'diagnostico_ny_range.py': 'diagnostico_ny_range.py',
        'ejemplo_simple.py': 'ejemplo_simple.py'
    }
    
    print("\n📋 Archivos a instalar:")
    for origen, destino in archivos.items():
        print(f"   {origen} → {destino}")
    
    # Confirmar
    respuesta = input("\n¿Continuar con la instalación? (s/n): ").strip().lower()
    if respuesta not in ['s', 'si', 'y', 'yes']:
        print("❌ Instalación cancelada")
        return False
    
    print("\n⚙️ Instalando archivos...")
    
    # Copiar archivos
    copiados = 0
    errores = 0
    
    for origen, destino in archivos.items():
        try:
            origen_path = current_dir / origen
            destino_path = current_dir / destino
            
            if not origen_path.exists():
                print(f"   ⚠️ {origen} no encontrado en directorio actual")
                print(f"      Buscando en directorio de descargas...")
                
                # Intentar en directorio de usuario
                home = Path.home()
                posibles_rutas = [
                    home / "Downloads" / origen,
                    home / "Descargas" / origen,
                    current_dir.parent / origen
                ]
                
                encontrado = False
                for ruta in posibles_rutas:
                    if ruta.exists():
                        origen_path = ruta
                        encontrado = True
                        print(f"      ✅ Encontrado en: {ruta}")
                        break
                
                if not encontrado:
                    print(f"   ❌ No se pudo encontrar {origen}")
                    errores += 1
                    continue
            
            # Hacer backup si ya existe
            if destino_path.exists():
                backup_path = destino_path.with_suffix('.py.backup')
                shutil.copy2(destino_path, backup_path)
                print(f"   💾 Backup creado: {backup_path.name}")
            
            # Copiar archivo
            shutil.copy2(origen_path, destino_path)
            print(f"   ✅ Copiado: {destino}")
            copiados += 1
            
        except Exception as e:
            print(f"   ❌ Error copiando {origen}: {e}")
            errores += 1
    
    # Resumen
    print("\n" + "="*70)
    print("📊 RESUMEN DE INSTALACIÓN")
    print("="*70)
    print(f"   ✅ Archivos copiados: {copiados}")
    print(f"   ❌ Errores: {errores}")
    
    if errores == 0:
        print("\n🎉 ¡Instalación completada exitosamente!")
        print("\n📋 Próximos pasos:")
        print("   1. Ejecutar: python run_ny_range_backtest.py")
        print("   2. Seleccionar opción 2 (Backtest con datos MT5)")
        print("   3. ¡Disfrutar del backtesting!")
    else:
        print("\n⚠️ Instalación completada con errores")
        print("   Revisa los mensajes de error arriba")
    
    return errores == 0


def verificar_instalacion():
    """Verifica que los archivos estén instalados correctamente"""
    
    print("\n" + "="*70)
    print("🔍 VERIFICACIÓN DE INSTALACIÓN")
    print("="*70)
    
    current_dir = Path.cwd()
    
    archivos_requeridos = [
        'strategies/ny_range_breakout_strategy.py',
        'run_ny_range_backtest.py',
        'diagnostico_ny_range.py',
        'data_manager.py',
        'backtest_engine.py'
    ]
    
    todos_ok = True
    
    for archivo in archivos_requeridos:
        path = current_dir / archivo
        if path.exists():
            # Verificar tamaño
            size_kb = path.stat().st_size / 1024
            
            # Para ny_range_breakout_strategy, verificar que tenga manage_risk sobrescrito
            if 'ny_range_breakout' in archivo:
                with open(path, 'r', encoding='utf-8') as f:
                    contenido = f.read()
                    if 'def manage_risk' in contenido and 'Sobrescribe manage_risk' in contenido:
                        print(f"   ✅ {archivo} ({size_kb:.1f} KB) - manage_risk OK")
                    else:
                        print(f"   ⚠️ {archivo} ({size_kb:.1f} KB) - manage_risk NO sobrescrito")
                        todos_ok = False
            else:
                print(f"   ✅ {archivo} ({size_kb:.1f} KB)")
        else:
            print(f"   ❌ {archivo} - NO ENCONTRADO")
            todos_ok = False
    
    print("\n" + "="*70)
    if todos_ok:
        print("✅ Todos los archivos instalados correctamente")
        print("\n🚀 Listo para ejecutar:")
        print("   python run_ny_range_backtest.py")
    else:
        print("⚠️ Faltan archivos o hay problemas")
        print("\n💡 Ejecuta: python instalar_estrategia.py")
    
    return todos_ok


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == 'verificar':
        verificar_instalacion()
    else:
        if instalar_estrategia():
            print("\n🔍 Verificando instalación...")
            verificar_instalacion()
