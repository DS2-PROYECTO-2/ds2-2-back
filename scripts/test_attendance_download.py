#!/usr/bin/env python
"""
Script para probar el endpoint de descarga de attendance
"""
import os
import sys
import django
import requests

# Configurar Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ds2_back.settings.development')
django.setup()

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

def test_attendance_download():
    """Probar descarga de archivos de attendance"""
    print("🧪 Probando descarga de archivos de attendance...")
    
    # Obtener token
    token = get_auth_token()
    if not token:
        print("❌ No se pudo obtener token")
        return False
    
    headers = {"Authorization": f"Token {token}"}
    base_url = "http://localhost:8000/api/attendance"
    
    try:
        # Primero, obtener la lista de attendances
        print("📋 Obteniendo lista de attendances...")
        response = requests.get(f"{base_url}/attendances/", headers=headers)
        
        if response.status_code != 200:
            print(f"❌ Error obteniendo lista: {response.status_code}")
            return False
        
        attendances = response.json()
        print(f"✅ Lista obtenida: {len(attendances)} registros")
        
        if not attendances:
            print("⚠️  No hay attendances para probar descarga")
            return True
        
        # Probar descarga del primer attendance
        first_attendance = attendances[0]
        attendance_id = first_attendance['id']
        attendance_title = first_attendance['title']
        
        print(f"\n📥 Probando descarga de attendance ID {attendance_id}...")
        print(f"   - Título: {attendance_title}")
        print(f"   - Archivo: {first_attendance.get('file', 'No disponible')}")
        
        # Probar descarga
        download_url = f"{base_url}/attendances/{attendance_id}/download/"
        print(f"   - URL: {download_url}")
        
        response = requests.get(download_url, headers=headers)
        print(f"   - Status: {response.status_code}")
        print(f"   - Content-Type: {response.headers.get('Content-Type', 'No especificado')}")
        print(f"   - Content-Length: {response.headers.get('Content-Length', 'No especificado')}")
        print(f"   - Content-Disposition: {response.headers.get('Content-Disposition', 'No especificado')}")
        
        if response.status_code == 200:
            print(f"✅ Descarga exitosa!")
            print(f"   - Tamaño descargado: {len(response.content)} bytes")
            
            # Verificar que el contenido no esté vacío
            if len(response.content) > 0:
                print("✅ Archivo tiene contenido")
                
                # Mostrar inicio del archivo
                content_preview = response.content[:100]
                print(f"   - Inicio del archivo: {content_preview}")
                
                return True
            else:
                print("❌ Archivo descargado está vacío")
                return False
        else:
            print(f"❌ Error en descarga: {response.status_code}")
            print(f"   - Respuesta: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error en descarga: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_incapacity_download():
    """Probar descarga de documentos de incapacity"""
    print("\n🧪 Probando descarga de documentos de incapacity...")
    
    # Obtener token
    token = get_auth_token()
    if not token:
        print("❌ No se pudo obtener token")
        return False
    
    headers = {"Authorization": f"Token {token}"}
    base_url = "http://localhost:8000/api/attendance"
    
    try:
        # Primero, obtener la lista de incapacities
        print("📋 Obteniendo lista de incapacities...")
        response = requests.get(f"{base_url}/incapacities/", headers=headers)
        
        if response.status_code != 200:
            print(f"❌ Error obteniendo lista: {response.status_code}")
            return False
        
        incapacities = response.json()
        print(f"✅ Lista obtenida: {len(incapacities)} registros")
        
        if not incapacities:
            print("⚠️  No hay incapacities para probar descarga")
            return True
        
        # Probar descarga del primer incapacity
        first_incapacity = incapacities[0]
        incapacity_id = first_incapacity['id']
        incapacity_user = first_incapacity.get('user_username', 'Usuario')
        
        print(f"\n📥 Probando descarga de incapacity ID {incapacity_id}...")
        print(f"   - Usuario: {incapacity_user}")
        print(f"   - Documento: {first_incapacity.get('document', 'No disponible')}")
        
        # Probar descarga
        download_url = f"{base_url}/incapacities/{incapacity_id}/download/"
        print(f"   - URL: {download_url}")
        
        response = requests.get(download_url, headers=headers)
        print(f"   - Status: {response.status_code}")
        
        if response.status_code == 200:
            print(f"✅ Descarga exitosa!")
            print(f"   - Tamaño descargado: {len(response.content)} bytes")
            
            if len(response.content) > 0:
                print("✅ Documento tiene contenido")
                return True
            else:
                print("❌ Documento descargado está vacío")
                return False
        else:
            print(f"❌ Error en descarga: {response.status_code}")
            print(f"   - Respuesta: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error en descarga: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Función principal"""
    print("🔍 Prueba de descarga de archivos")
    print("=" * 50)
    
    # Prueba 1: Descarga de attendance
    attendance_success = test_attendance_download()
    
    # Prueba 2: Descarga de incapacity
    incapacity_success = test_incapacity_download()
    
    # Resumen
    print("\n📊 Resumen:")
    print(f"   - Descarga attendance: {'✅' if attendance_success else '❌'}")
    print(f"   - Descarga incapacity: {'✅' if incapacity_success else '❌'}")
    
    if attendance_success and incapacity_success:
        print("\n🎉 ¡Los endpoints de descarga funcionan correctamente!")
        print("   El frontend ahora puede descargar archivos usando:")
        print("   - GET /api/attendance/attendances/{id}/download/")
        print("   - GET /api/attendance/incapacities/{id}/download/")
    else:
        print("\n⚠️  Hay problemas con algunos endpoints de descarga")

if __name__ == "__main__":
    main()
