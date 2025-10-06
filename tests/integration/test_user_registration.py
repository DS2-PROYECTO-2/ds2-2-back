#!/usr/bin/env python3
"""
Script para probar el registro de usuario y ver los enlaces de activación
"""

import requests
import json
import time

def test_user_registration():
    """Probar el registro de usuario y ver enlaces de activación"""
    base_url = "http://localhost:8000"
    
    print("Probando registro de usuario...")
    print("=" * 60)
    
    # 1. Registrar nuevo usuario
    print("1. REGISTRAR NUEVO USUARIO")
    import random
    random_id = random.randint(1000, 9999)
    
    user_data = {
        "username": f"testuser_{random_id}",
        "email": f"testuser_{random_id}@example.com",
        "password": "password123",
        "password_confirm": "password123",
        "first_name": "Test",
        "last_name": "User",
        "identification": f"12345678{random_id}",
        "phone": "3001234567",
        "role": "monitor"
    }
    
    try:
        response = requests.post(f"{base_url}/api/auth/register/", json=user_data)
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.json()}")
        
        if response.status_code == 201:
            print("\n   ✅ USUARIO REGISTRADO EXITOSAMENTE")
            print("   Revisa la consola del servidor Django para ver los enlaces de activación")
            print("   Los enlaces aparecerán en la consola con el formato:")
            print("   APROBAR: http://localhost:8000/api/auth/admin/users/activate/?token=...")
            print("   RECHAZAR: http://localhost:8000/api/auth/admin/users/delete/?token=...")
        else:
            print(f"   ❌ ERROR AL REGISTRAR: {response.text}")
    except Exception as e:
        print(f"   ERROR: {e}")
    
    print("\n" + "=" * 60)
    print("NOTA:")
    print("1. El usuario se registra como 'monitor' (no verificado)")
    print("2. Se envía email a los administradores con enlaces de activación")
    print("3. En desarrollo, los enlaces aparecen en la consola del servidor")
    print("4. Los enlaces expiran en 24 horas")

def main():
    test_user_registration()

if __name__ == "__main__":
    main()
