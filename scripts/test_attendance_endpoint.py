#!/usr/bin/env python
"""
Script para probar el endpoint de attendance
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

def test_attendance_endpoints():
    """Probar endpoints de attendance"""
    print("🧪 Probando endpoints de attendance...")
    
    # Obtener token
    token = get_auth_token()
    if not token:
        print("❌ No se pudo obtener token")
        return False
    
    headers = {"Authorization": f"Token {token}"}
    base_url = "http://localhost:8000/api/attendance"
    
    try:
        # Probar GET /attendances/
        print("📋 Probando GET /attendances/...")
        response = requests.get(f"{base_url}/attendances/", headers=headers)
        print(f"   - Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   - Respuesta: {len(data)} listados encontrados")
            print("✅ GET /attendances/ funciona")
        else:
            print(f"❌ Error en GET: {response.text}")
            return False
        
        # Probar GET /attendances/my_uploads/
        print("\n📋 Probando GET /attendances/my_uploads/...")
        response = requests.get(f"{base_url}/attendances/my_uploads/", headers=headers)
        print(f"   - Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   - Respuesta: {len(data)} mis listados")
            print("✅ GET /attendances/my_uploads/ funciona")
        else:
            print(f"❌ Error en GET my_uploads: {response.text}")
            return False
        
        # Probar POST /attendances/ (sin archivo por ahora)
        print("\n📤 Probando POST /attendances/...")
        test_data = {
            "title": "Test Attendance List",
            "date": "2025-01-20",
            "description": "Listado de prueba"
        }
        
        response = requests.post(f"{base_url}/attendances/", 
                               headers=headers, 
                               json=test_data)
        print(f"   - Status: {response.status_code}")
        
        if response.status_code == 201:
            data = response.json()
            print(f"   - Respuesta: Listado creado con ID {data.get('id')}")
            print("✅ POST /attendances/ funciona")
            return True
        else:
            print(f"❌ Error en POST: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error en pruebas: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_incapacity_endpoints():
    """Probar endpoints de incapacity"""
    print("\n🧪 Probando endpoints de incapacity...")
    
    # Obtener token
    token = get_auth_token()
    if not token:
        print("❌ No se pudo obtener token")
        return False
    
    headers = {"Authorization": f"Token {token}"}
    base_url = "http://localhost:8000/api/attendance"
    
    try:
        # Probar GET /incapacities/
        print("📋 Probando GET /incapacities/...")
        response = requests.get(f"{base_url}/incapacities/", headers=headers)
        print(f"   - Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   - Respuesta: {len(data)} incapacidades encontradas")
            print("✅ GET /incapacities/ funciona")
        else:
            print(f"❌ Error en GET: {response.text}")
            return False
        
        # Probar GET /incapacities/my_incapacities/
        print("\n📋 Probando GET /incapacities/my_incapacities/...")
        response = requests.get(f"{base_url}/incapacities/my_incapacities/", headers=headers)
        print(f"   - Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   - Respuesta: {len(data)} mis incapacidades")
            print("✅ GET /incapacities/my_incapacities/ funciona")
            return True
        else:
            print(f"❌ Error en GET my_incapacities: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error en pruebas: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Función principal"""
    print("🔍 Prueba de endpoints de attendance")
    print("=" * 50)
    
    # Prueba 1: Endpoints de attendance
    attendance_success = test_attendance_endpoints()
    
    # Prueba 2: Endpoints de incapacity
    incapacity_success = test_incapacity_endpoints()
    
    # Resumen
    print("\n📊 Resumen:")
    print(f"   - Attendance endpoints: {'✅' if attendance_success else '❌'}")
    print(f"   - Incapacity endpoints: {'✅' if incapacity_success else '❌'}")
    
    if attendance_success and incapacity_success:
        print("\n🎉 ¡Todos los endpoints funcionan correctamente!")
    else:
        print("\n⚠️  Algunos endpoints tienen problemas")

if __name__ == "__main__":
    main()
