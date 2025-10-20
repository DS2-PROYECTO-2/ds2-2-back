#!/usr/bin/env python
"""
Script para verificar que todas las dependencias estén instaladas correctamente
"""
import sys
import importlib

def check_dependency(module_name, package_name=None):
    """Verificar si una dependencia está instalada"""
    try:
        importlib.import_module(module_name)
        print(f"✅ {package_name or module_name}: Instalado")
        return True
    except ImportError as e:
        print(f"❌ {package_name or module_name}: No instalado - {e}")
        return False

def main():
    """Verificar todas las dependencias críticas"""
    print("🔍 Verificando dependencias del proyecto")
    print("=" * 50)
    
    dependencies = [
        # Core Django
        ("django", "Django"),
        ("rest_framework", "Django REST Framework"),
        ("corsheaders", "Django CORS Headers"),
        
        # Database
        ("psycopg", "psycopg (PostgreSQL)"),
        ("psycopg2", "psycopg2 (PostgreSQL fallback)"),
        
        # Authentication
        ("rest_framework_simplejwt", "JWT Authentication"),
        ("oauth2_provider", "OAuth2 Toolkit"),
        
        # API Documentation
        ("drf_spectacular", "DRF Spectacular"),
        
        # Testing
        ("pytest", "pytest"),
        ("pytest_django", "pytest-django"),
        
        # Development
        ("debug_toolbar", "Django Debug Toolbar"),
        ("django_extensions", "Django Extensions"),
        
        # Utilities
        ("decouple", "python-decouple"),
        ("environ", "django-environ"),
        ("PIL", "Pillow"),
        
        # Production
        ("gunicorn", "Gunicorn"),
        ("whitenoise", "Whitenoise"),
        
        # Email
        ("anymail", "Django Anymail"),
        ("requests", "Requests"),
        
        # Forms
        ("crispy_forms", "Django Crispy Forms"),
        ("crispy_bootstrap4", "Crispy Bootstrap4"),
        
        # Filtering
        ("django_filters", "Django Filter"),
        ("import_export", "Django Import Export"),
        
        # Export functionality
        ("reportlab", "ReportLab (PDF)"),
        ("openpyxl", "OpenPyXL (Excel)"),
        ("xlsxwriter", "XlsxWriter (Excel)"),
    ]
    
    success_count = 0
    total_count = len(dependencies)
    
    for module_name, package_name in dependencies:
        if check_dependency(module_name, package_name):
            success_count += 1
    
    print("\n📊 Resumen:")
    print(f"   - Dependencias instaladas: {success_count}/{total_count}")
    print(f"   - Porcentaje: {(success_count/total_count)*100:.1f}%")
    
    if success_count == total_count:
        print("\n🎉 ¡Todas las dependencias están instaladas correctamente!")
        print("   El proyecto está listo para ejecutarse.")
    else:
        print(f"\n⚠️  Faltan {total_count - success_count} dependencias")
        print("   Ejecuta: pip install -r requirements.txt")
    
    return success_count == total_count

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
