#!/usr/bin/env python
"""
Script para diagnosticar por qué se descargan archivos vacíos
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
from attendance.models import Attendance

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

def check_attendance_files():
    """Verificar archivos de attendance en la base de datos"""
    print("🔍 Verificando archivos de attendance en la base de datos...")
    
    try:
        attendances = Attendance.objects.all()
        print(f"✅ Total de attendances: {attendances.count()}")
        
        for attendance in attendances:
            print(f"\n📋 Attendance ID {attendance.id}:")
            print(f"   - Título: {attendance.title}")
            print(f"   - Archivo: {attendance.file.name if attendance.file else 'No archivo'}")
            
            if attendance.file:
                try:
                    # Verificar si el archivo existe en el sistema de archivos
                    if attendance.file.storage.exists(attendance.file.name):
                        print(f"   - ✅ Archivo existe en storage")
                        
                        # Leer el archivo y verificar tamaño
                        with attendance.file.open('rb') as f:
                            content = f.read()
                            print(f"   - Tamaño en storage: {len(content)} bytes")
                            
                            if len(content) == 0:
                                print("   - ❌ PROBLEMA: Archivo está vacío en storage")
                            else:
                                print("   - ✅ Archivo tiene contenido en storage")
                                
                                # Mostrar inicio del archivo
                                preview = content[:50]
                                print(f"   - Inicio: {preview}")
                    else:
                        print(f"   - ❌ PROBLEMA: Archivo no existe en storage")
                        
                except Exception as e:
                    print(f"   - ❌ Error leyendo archivo: {e}")
            else:
                print(f"   - ❌ PROBLEMA: No hay archivo asociado")
                
    except Exception as e:
        print(f"❌ Error verificando attendances: {e}")
        import traceback
        traceback.print_exc()

def test_download_with_debug():
    """Probar descarga con debugging detallado"""
    print("\n🧪 Probando descarga con debugging...")
    
    # Obtener token
    token = get_auth_token()
    if not token:
        print("❌ No se pudo obtener token")
        return False
    
    headers = {"Authorization": f"Token {token}"}
    base_url = "http://localhost:8000/api/attendance"
    
    try:
        # Obtener lista de attendances
        response = requests.get(f"{base_url}/attendances/", headers=headers)
        
        if response.status_code != 200:
            print(f"❌ Error obteniendo lista: {response.status_code}")
            return False
        
        attendances = response.json()
        print(f"✅ Lista obtenida: {len(attendances)} registros")
        
        if not attendances:
            print("⚠️  No hay attendances para probar")
            return False
        
        # Probar descarga del primer attendance
        first_attendance = attendances[0]
        attendance_id = first_attendance['id']
        
        print(f"\n📥 Probando descarga de attendance ID {attendance_id}...")
        
        download_url = f"{base_url}/attendances/{attendance_id}/download/"
        print(f"   - URL: {download_url}")
        
        # Hacer petición de descarga
        response = requests.get(download_url, headers=headers)
        
        print(f"   - Status: {response.status_code}")
        print(f"   - Headers recibidos:")
        for key, value in response.headers.items():
            print(f"     * {key}: {value}")
        
        if response.status_code == 200:
            content = response.content
            print(f"   - Tamaño descargado: {len(content)} bytes")
            
            if len(content) == 0:
                print("❌ PROBLEMA: Respuesta está vacía")
                return False
            else:
                print("✅ Respuesta tiene contenido")
                print(f"   - Inicio del contenido: {content[:50]}")
                
                # Verificar si es un PDF válido
                if content.startswith(b'%PDF'):
                    print("✅ Contenido es PDF válido")
                else:
                    print("⚠️  Contenido no parece ser PDF válido")
                
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

def test_direct_file_access():
    """Probar acceso directo a archivos"""
    print("\n🧪 Probando acceso directo a archivos...")
    
    try:
        attendances = Attendance.objects.filter(file__isnull=False)
        print(f"✅ Attendances con archivos: {attendances.count()}")
        
        for attendance in attendances:
            print(f"\n📋 Probando attendance ID {attendance.id}:")
            print(f"   - Archivo: {attendance.file.name}")
            
            try:
                # Acceso directo al archivo
                with attendance.file.open('rb') as f:
                    content = f.read()
                    print(f"   - Tamaño directo: {len(content)} bytes")
                    
                    if len(content) == 0:
                        print("   - ❌ PROBLEMA: Archivo está vacío en acceso directo")
                    else:
                        print("   - ✅ Archivo tiene contenido en acceso directo")
                        print(f"   - Inicio: {content[:50]}")
                        
            except Exception as e:
                print(f"   - ❌ Error en acceso directo: {e}")
                
    except Exception as e:
        print(f"❌ Error en acceso directo: {e}")
        import traceback
        traceback.print_exc()

def main():
    """Función principal"""
    print("🔍 Diagnóstico de archivos vacíos")
    print("=" * 50)
    
    # Verificar archivos en la base de datos
    check_attendance_files()
    
    # Probar descarga con debugging
    download_success = test_download_with_debug()
    
    # Probar acceso directo
    test_direct_file_access()
    
    # Resumen
    print("\n📊 Resumen del diagnóstico:")
    print(f"   - Descarga HTTP: {'✅' if download_success else '❌'}")
    
    if download_success:
        print("\n🎉 ¡La descarga funciona correctamente!")
        print("   Si el frontend recibe archivos vacíos, el problema está en:")
        print("   - Manejo de la respuesta en el frontend")
        print("   - Configuración de la petición HTTP")
        print("   - Procesamiento del blob en el frontend")
    else:
        print("\n⚠️  Hay problemas con la descarga en el backend")

if __name__ == "__main__":
    main()
