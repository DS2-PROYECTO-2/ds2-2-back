#!/usr/bin/env python
"""
Script para probar descarga con ID específico
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

def test_download_specific_id():
    """Probar descarga con ID específico"""
    print("🧪 Probando descarga con ID específico...")
    
    # Obtener token
    token = get_auth_token()
    if not token:
        print("❌ No se pudo obtener token")
        return False
    
    headers = {"Authorization": f"Token {token}"}
    base_url = "http://localhost:8000/api/attendance"
    
    # Probar con IDs específicos que sabemos que existen
    test_ids = [11, 12, 13]
    
    for attendance_id in test_ids:
        print(f"\n📥 Probando descarga de attendance ID {attendance_id}...")
        
        download_url = f"{base_url}/attendances/{attendance_id}/download/"
        print(f"   - URL: {download_url}")
        
        try:
            response = requests.get(download_url, headers=headers)
            print(f"   - Status: {response.status_code}")
            print(f"   - Content-Type: {response.headers.get('Content-Type', 'No especificado')}")
            print(f"   - Content-Length: {response.headers.get('Content-Length', 'No especificado')}")
            
            if response.status_code == 200:
                content = response.content
                print(f"   - Tamaño descargado: {len(content)} bytes")
                
                if len(content) == 0:
                    print("   - ❌ PROBLEMA: Archivo descargado está vacío")
                else:
                    print("   - ✅ Archivo descargado tiene contenido")
                    print(f"   - Inicio: {content[:50]}")
                    
                    # Verificar si es PDF válido
                    if content.startswith(b'%PDF'):
                        print("   - ✅ Es PDF válido")
                    else:
                        print("   - ⚠️  No parece ser PDF válido")
                    
                    return True
            else:
                print(f"   - ❌ Error: {response.status_code}")
                print(f"   - Respuesta: {response.text}")
                
        except Exception as e:
            print(f"   - ❌ Error en petición: {e}")
    
    return False

def test_download_with_stream():
    """Probar descarga con stream=True para archivos grandes"""
    print("\n🧪 Probando descarga con stream=True...")
    
    # Obtener token
    token = get_auth_token()
    if not token:
        print("❌ No se pudo obtener token")
        return False
    
    headers = {"Authorization": f"Token {token}"}
    base_url = "http://localhost:8000/api/attendance"
    
    attendance_id = 11
    download_url = f"{base_url}/attendances/{attendance_id}/download/"
    
    try:
        print(f"📥 Descargando con stream=True desde {download_url}")
        
        response = requests.get(download_url, headers=headers, stream=True)
        print(f"   - Status: {response.status_code}")
        
        if response.status_code == 200:
            # Leer contenido en chunks
            content = b""
            chunk_count = 0
            
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    content += chunk
                    chunk_count += 1
                    if chunk_count <= 5:  # Mostrar primeros 5 chunks
                        print(f"   - Chunk {chunk_count}: {len(chunk)} bytes")
            
            print(f"   - Total chunks: {chunk_count}")
            print(f"   - Tamaño total: {len(content)} bytes")
            
            if len(content) == 0:
                print("   - ❌ PROBLEMA: Contenido está vacío")
                return False
            else:
                print("   - ✅ Contenido descargado correctamente")
                print(f"   - Inicio: {content[:50]}")
                return True
        else:
            print(f"   - ❌ Error: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"   - ❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Función principal"""
    print("🔍 Prueba de descarga con ID específico")
    print("=" * 50)
    
    # Prueba 1: Descarga normal
    normal_success = test_download_specific_id()
    
    # Prueba 2: Descarga con stream
    stream_success = test_download_with_stream()
    
    # Resumen
    print("\n📊 Resumen:")
    print(f"   - Descarga normal: {'✅' if normal_success else '❌'}")
    print(f"   - Descarga con stream: {'✅' if stream_success else '❌'}")
    
    if normal_success or stream_success:
        print("\n🎉 ¡La descarga funciona correctamente!")
        print("   Si el frontend recibe archivos vacíos, el problema está en:")
        print("   - Configuración de la petición en el frontend")
        print("   - Manejo de la respuesta HTTP en el frontend")
        print("   - Procesamiento del blob en el frontend")
    else:
        print("\n⚠️  Hay problemas con la descarga en el backend")

if __name__ == "__main__":
    main()
