#!/usr/bin/env python
"""
Script para probar la descarga de PDF generado
"""
import os
import sys
import django
import requests
import tempfile

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
        # Buscar usuario admin
        admin_user = User.objects.filter(role=User.ADMIN).first()
        if not admin_user:
            print("❌ No se encontró usuario admin")
            return None
        
        # Autenticar usuario
        user = authenticate(username=admin_user.username, password='admin123')
        if not user:
            print("❌ Error de autenticación")
            return None
        
        # Obtener o crear token
        from rest_framework.authtoken.models import Token
        token, created = Token.objects.get_or_create(user=user)
        
        print(f"✅ Token obtenido: {token.key[:10]}...")
        return token.key
        
    except Exception as e:
        print(f"❌ Error obteniendo token: {e}")
        return None

def test_pdf_download():
    """Probar descarga de PDF"""
    print("🧪 Probando descarga de PDF...")
    
    # Obtener token
    token = get_auth_token()
    if not token:
        return False
    
    try:
        # Buscar un trabajo de exportación PDF completado
        export_job = ExportJob.objects.filter(
            format=ExportJob.PDF,
            status=ExportJob.COMPLETED,
            file__isnull=False
        ).first()
        
        if not export_job:
            print("❌ No se encontró trabajo de exportación PDF completado")
            return False
        
        print(f"✅ Trabajo encontrado: ID {export_job.id}")
        print(f"   - Archivo: {export_job.file.name}")
        print(f"   - Tamaño: {export_job.file_size} bytes")
        
        # Probar descarga
        headers = {"Authorization": f"Token {token}"}
        download_url = f"http://localhost:8000/api/export/jobs/{export_job.id}/download/"
        
        print(f"📥 Descargando desde: {download_url}")
        
        response = requests.get(download_url, headers=headers)
        
        print(f"   - Status Code: {response.status_code}")
        print(f"   - Content-Type: {response.headers.get('Content-Type', 'No especificado')}")
        print(f"   - Content-Length: {response.headers.get('Content-Length', 'No especificado')}")
        
        if response.status_code == 200:
            # Guardar archivo temporal para verificar
            with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
                tmp_file.write(response.content)
                tmp_file_path = tmp_file.name
            
            print(f"✅ Descarga exitosa")
            print(f"   - Archivo guardado en: {tmp_file_path}")
            print(f"   - Tamaño descargado: {len(response.content)} bytes")
            
            # Verificar que es un PDF válido
            if response.content.startswith(b'%PDF'):
                print("✅ Archivo PDF válido")
            else:
                print("❌ Archivo PDF inválido")
                print(f"   - Inicio del archivo: {response.content[:50]}")
            
            # Limpiar archivo temporal
            os.unlink(tmp_file_path)
            
            return True
        else:
            print(f"❌ Error en descarga: {response.status_code}")
            print(f"   - Respuesta: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error en descarga: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_pdf_generation_and_download():
    """Probar generación y descarga completa"""
    print("🧪 Probando generación y descarga completa...")
    
    # Obtener token
    token = get_auth_token()
    if not token:
        return False
    
    try:
        # Crear nuevo trabajo de exportación
        admin_user = User.objects.filter(role=User.ADMIN).first()
        export_job = ExportJob.objects.create(
            title="Test PDF Download",
            export_type=ExportJob.MONITORS_DATA,
            format=ExportJob.PDF,
            status=ExportJob.PENDING,
            requested_by=admin_user
        )
        
        print(f"✅ Trabajo creado: ID {export_job.id}")
        
        # Generar PDF
        from export.services import MonitorDataExporter
        exporter = MonitorDataExporter(export_job)
        success = exporter.export_to_pdf()
        
        if not success:
            print("❌ Error generando PDF")
            return False
        
        print("✅ PDF generado exitosamente")
        
        # Probar descarga
        headers = {"Authorization": f"Token {token}"}
        download_url = f"http://localhost:8000/api/export/jobs/{export_job.id}/download/"
        
        response = requests.get(download_url, headers=headers)
        
        if response.status_code == 200:
            print("✅ Descarga exitosa")
            print(f"   - Content-Type: {response.headers.get('Content-Type')}")
            print(f"   - Tamaño: {len(response.content)} bytes")
            
            if response.content.startswith(b'%PDF'):
                print("✅ PDF válido descargado")
                return True
            else:
                print("❌ PDF inválido descargado")
                return False
        else:
            print(f"❌ Error en descarga: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error en proceso completo: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Función principal"""
    print("🔍 Prueba de descarga de PDF")
    print("=" * 50)
    
    # Prueba 1: Descargar PDF existente
    print("\n1. Probando descarga de PDF existente...")
    download_success = test_pdf_download()
    
    # Prueba 2: Generar y descargar nuevo PDF
    print("\n2. Probando generación y descarga...")
    generate_success = test_pdf_generation_and_download()
    
    # Resumen
    print("\n📊 Resumen:")
    print(f"   - Descarga existente: {'✅' if download_success else '❌'}")
    print(f"   - Generación y descarga: {'✅' if generate_success else '❌'}")
    
    if download_success and generate_success:
        print("\n🎉 ¡La descarga de PDF funciona correctamente!")
        print("   El problema puede estar en el frontend o en la visualización.")
    else:
        print("\n⚠️  Hay problemas con la descarga de PDF")

if __name__ == "__main__":
    main()
