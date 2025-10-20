#!/usr/bin/env python
"""
Script para instalar dependencias de exportación
"""
import subprocess
import sys

def install_package(package):
    """Instala un paquete usando pip"""
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        print(f"✅ {package} instalado correctamente")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error instalando {package}: {e}")
        return False

def main():
    """Instala las dependencias necesarias para exportación"""
    print("🔧 Instalando dependencias de exportación...")
    
    dependencies = [
        "reportlab==4.0.9",
        "openpyxl==3.1.2", 
        "xlsxwriter==3.1.9"
    ]
    
    success_count = 0
    for dep in dependencies:
        if install_package(dep):
            success_count += 1
    
    print(f"\n📊 Resumen:")
    print(f"✅ Instalados: {success_count}/{len(dependencies)}")
    
    if success_count == len(dependencies):
        print("🎉 Todas las dependencias instaladas correctamente!")
        print("\n📝 Próximos pasos:")
        print("1. Reinicia el servidor Django")
        print("2. Prueba los endpoints de exportación")
        print("3. Verifica que la funcionalidad PDF/Excel funcione")
    else:
        print("⚠️  Algunas dependencias fallaron. Revisa los errores arriba.")
    
    return success_count == len(dependencies)

if __name__ == "__main__":
    main()

