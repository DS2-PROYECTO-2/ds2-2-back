#!/usr/bin/env python
"""
Script para probar la descarga de archivos y verificar si están vacíos
"""
import os
import sys
import django
import requests

# Configurar Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ds2_back.settings.development')
django.setup()

from export.models import ExportJob
from users.models import User
from django.contrib.auth import authenticate

def get_auth_token():
    """Obtener token de autenticación"""
    try:
        admin_user = User.objects.filter(role=User.ADMIN).first()
        if not admin_user:
            return None
        
        user = authenticate(username=admin_user.username, password='admin123')
        if not user:
            return None
        
        from rest_framework.authtoken.models import Token
        token, created = Token.objects.get_or_create(user=user)
        return token.key
        
    except Exception as e:
        print(f"❌ Error obteniendo token: {e}")
        return None

def test_file_download():
    """Probar descarga de archivo"""
    print("🧪 Probando descarga de archivo...")
    
    # Obtener token
    token = get_auth_token()
    if not token:
        print("❌ No se pudo obtener token")
        return False
    
    try:
        # Buscar trabajo completado
        export_job = ExportJob.objects.filter(
            status=ExportJob.COMPLETED,
            file__isnull=False
        ).first()
        
        if not export_job:
            print("❌ No se encontró trabajo completado")
            return False
        
        print(f"✅ Trabajo encontrado: ID {export_job.id}")
        print(f"   - Archivo: {export_job.file.name}")
        print(f"   - Tamaño en BD: {export_job.file_size} bytes")
        
        # Verificar archivo en disco
        if export_job.file:
            try:
                with export_job.file.open('rb') as f:
                    file_content = f.read()
                    print(f"   - Contenido real: {len(file_content)} bytes")
                    
                    if len(file_content) == 0:
                        print("❌ PROBLEMA: Archivo en disco está vacío!")
                        return False
                    else:
                        print("✅ Archivo en disco tiene contenido")
            except Exception as e:
                print(f"❌ Error leyendo archivo: {e}")
                return False
        
        # Probar descarga HTTP
        headers = {"Authorization": f"Token {token}"}
        download_url = f"http://localhost:8000/api/export/jobs/{export_job.id}/download/"
        
        print(f"📥 Descargando desde: {download_url}")
        
        response = requests.get(download_url, headers=headers)
        
        print(f"   - Status: {response.status_code}")
        print(f"   - Content-Type: {response.headers.get('Content-Type')}")
        print(f"   - Content-Length: {response.headers.get('Content-Length')}")
        print(f"   - Tamaño descargado: {len(response.content)} bytes")
        
        if response.status_code == 200:
            if len(response.content) == 0:
                print("❌ PROBLEMA: Respuesta HTTP está vacía!")
                return False
            else:
                print("✅ Respuesta HTTP tiene contenido")
                
                # Verificar que es PDF válido
                if response.content.startswith(b'%PDF'):
                    print("✅ Contenido es PDF válido")
                else:
                    print("❌ Contenido no es PDF válido")
                    print(f"   - Inicio: {response.content[:50]}")
                    return False
                
                return True
        else:
            print(f"❌ Error HTTP: {response.status_code}")
            print(f"   - Respuesta: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error en descarga: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_new_export_and_download():
    """Crear nueva exportación y probar descarga"""
    print("\n🧪 Probando nueva exportación y descarga...")
    
    # Obtener token
    token = get_auth_token()
    if not token:
        print("❌ No se pudo obtener token")
        return False
    
    try:
        # Crear nueva exportación
        admin_user = User.objects.filter(role=User.ADMIN).first()
        export_job = ExportJob.objects.create(
            title="Test Download",
            export_type=ExportJob.MONITORS_DATA,
            format=ExportJob.PDF,
            status=ExportJob.PENDING,
            requested_by=admin_user
        )
        
        print(f"✅ Trabajo creado: ID {export_job.id}")
        
        # Generar archivo
        from export.services import MonitorDataExporter
        exporter = MonitorDataExporter(export_job)
        success = exporter.export_to_pdf()
        
        if not success:
            print("❌ Error generando archivo")
            return False
        
        print("✅ Archivo generado")
        
        # Verificar archivo generado
        if export_job.file:
            with export_job.file.open('rb') as f:
                file_content = f.read()
                print(f"   - Tamaño generado: {len(file_content)} bytes")
                
                if len(file_content) == 0:
                    print("❌ PROBLEMA: Archivo generado está vacío!")
                    return False
        
        # Probar descarga
        headers = {"Authorization": f"Token {token}"}
        download_url = f"http://localhost:8000/api/export/jobs/{export_job.id}/download/"
        
        response = requests.get(download_url, headers=headers)
        
        if response.status_code == 200:
            print(f"✅ Descarga exitosa: {len(response.content)} bytes")
            
            if len(response.content) == 0:
                print("❌ PROBLEMA: Descarga está vacía!")
                return False
            else:
                print("✅ Descarga tiene contenido")
                return True
        else:
            print(f"❌ Error en descarga: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error en proceso: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Función principal"""
    print("🔍 Prueba de descarga de archivos")
    print("=" * 50)
    
    # Prueba 1: Descargar archivo existente
    download_success = test_file_download()
    
    # Prueba 2: Crear nuevo y descargar
    new_success = test_new_export_and_download()
    
    # Resumen
    print("\n📊 Resumen:")
    print(f"   - Descarga existente: {'✅' if download_success else '❌'}")
    print(f"   - Nueva exportación: {'✅' if new_success else '❌'}")
    
    if download_success and new_success:
        print("\n🎉 ¡La descarga funciona correctamente!")
        print("   El problema del archivo vacío NO está en el backend.")
        print("   Puede ser un problema de:")
        print("   - Configuración de CORS")
        print("   - Autenticación en el frontend")
        print("   - Manejo de la respuesta en el frontend")
    else:
        print("\n⚠️  Hay problemas con la descarga")

if __name__ == "__main__":
    main()
