#!/usr/bin/env python
"""
Script para probar la subida de archivos de attendance
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

def create_test_file():
    """Crear un archivo de prueba"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write("Listado de Asistencia de Prueba\n")
        f.write("Fecha: 2025-01-20\n")
        f.write("Monitor 1: Presente\n")
        f.write("Monitor 2: Ausente\n")
        f.write("Monitor 3: Presente\n")
        return f.name

def test_attendance_upload():
    """Probar subida de archivo de attendance"""
    print("🧪 Probando subida de archivo de attendance...")
    
    # Obtener token
    token = get_auth_token()
    if not token:
        print("❌ No se pudo obtener token")
        return False
    
    headers = {"Authorization": f"Token {token}"}
    base_url = "http://localhost:8000/api/attendance"
    
    try:
        # Crear archivo de prueba
        test_file_path = create_test_file()
        print(f"✅ Archivo de prueba creado: {test_file_path}")
        
        # Preparar datos del formulario
        with open(test_file_path, 'rb') as f:
            files = {'file': ('test_attendance.txt', f, 'text/plain')}
            data = {
                'title': 'Listado de Asistencia - Prueba',
                'date': '2025-01-20',
                'description': 'Listado de prueba para testing'
            }
            
            print("📤 Enviando archivo...")
            response = requests.post(f"{base_url}/attendances/", 
                                   headers=headers, 
                                   files=files,
                                   data=data)
        
        # Limpiar archivo temporal
        os.unlink(test_file_path)
        
        print(f"   - Status: {response.status_code}")
        
        if response.status_code == 201:
            data = response.json()
            print(f"✅ Archivo subido exitosamente!")
            print(f"   - ID: {data.get('id')}")
            print(f"   - Título: {data.get('title')}")
            print(f"   - Fecha: {data.get('date')}")
            print(f"   - Archivo: {data.get('file')}")
            print(f"   - Subido por: {data.get('uploaded_by_username')}")
            return True
        else:
            print(f"❌ Error en subida: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error en subida: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_attendance_list():
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
            
            if data:
                latest = data[0]  # El más reciente
                print(f"   - Último registro:")
                print(f"     * ID: {latest.get('id')}")
                print(f"     * Título: {latest.get('title')}")
                print(f"     * Fecha: {latest.get('date')}")
                print(f"     * Revisado: {latest.get('reviewed')}")
                print(f"     * Subido por: {latest.get('uploaded_by_username')}")
            
            return True
        else:
            print(f"❌ Error en listado: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error en listado: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Función principal"""
    print("🔍 Prueba de subida de archivos de attendance")
    print("=" * 50)
    
    # Prueba 1: Subir archivo
    upload_success = test_attendance_upload()
    
    # Prueba 2: Listar archivos
    list_success = test_attendance_list()
    
    # Resumen
    print("\n📊 Resumen:")
    print(f"   - Subida de archivo: {'✅' if upload_success else '❌'}")
    print(f"   - Listado de archivos: {'✅' if list_success else '❌'}")
    
    if upload_success and list_success:
        print("\n🎉 ¡El endpoint de attendance funciona correctamente!")
        print("   El problema del frontend está resuelto.")
    else:
        print("\n⚠️  Hay problemas con el endpoint")

if __name__ == "__main__":
    main()
