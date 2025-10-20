#!/usr/bin/env python
"""
Script para probar descarga directa con ID específico
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

def test_download_with_id():
    """Probar descarga con ID específico"""
    print("🧪 Probando descarga con ID específico...")
    
    # Obtener token
    token = get_auth_token()
    if not token:
        print("❌ No se pudo obtener token")
        return False
    
    headers = {"Authorization": f"Token {token}"}
    base_url = "http://localhost:8000/api/attendance"
    
    try:
        # Probar con ID 11 (el que está en el error del frontend)
        attendance_id = 11
        print(f"📥 Probando descarga de attendance ID {attendance_id}...")
        
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
            
            if len(response.content) > 0:
                print("✅ Archivo tiene contenido")
                print(f"   - Inicio del archivo: {response.content[:50]}")
                return True
            else:
                print("❌ Archivo descargado está vacío")
                return False
        elif response.status_code == 404:
            print("❌ Attendance no encontrado")
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

def test_list_attendances():
    """Probar listado de attendances"""
    print("\n🧪 Probando listado de attendances...")
    
    # Obtener token
    token = get_auth_token()
    if not token:
        print("❌ No se pudo obtener token")
        return False
    
    headers = {"Authorization": f"Token {token}"}
    base_url = "http://localhost:8000/api/attendance"
    
    try:
        response = requests.get(f"{base_url}/attendances/", headers=headers)
        print(f"   - Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Listado obtenido: {len(data)} registros")
            
            # Mostrar IDs disponibles
            if data:
                print("   - IDs disponibles:")
                for item in data:
                    print(f"     * ID: {item.get('id')} - {item.get('title')}")
                return True
            else:
                print("⚠️  No hay registros")
                return False
        else:
            print(f"❌ Error en listado: {response.status_code}")
            print(f"   - Respuesta: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error en listado: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Función principal"""
    print("🔍 Prueba de descarga directa")
    print("=" * 50)
    
    # Prueba 1: Listar attendances
    list_success = test_list_attendances()
    
    # Prueba 2: Descargar con ID específico
    download_success = test_download_with_id()
    
    # Resumen
    print("\n📊 Resumen:")
    print(f"   - Listado: {'✅' if list_success else '❌'}")
    print(f"   - Descarga: {'✅' if download_success else '❌'}")
    
    if download_success:
        print("\n🎉 ¡El endpoint de descarga funciona correctamente!")
        print("   El frontend puede usar:")
        print("   - GET /api/attendance/attendances/{id}/download/")
    else:
        print("\n⚠️  Hay problemas con el endpoint de descarga")

if __name__ == "__main__":
    main()
