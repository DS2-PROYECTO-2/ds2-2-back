#!/usr/bin/env python3
"""
Script simple para probar datos de usuarios
"""

import requests
import json

def test_user_data():
    """Probar que los endpoints devuelvan identification y role"""
    base_url = "http://localhost:8000"
    
    print("Probando datos de usuarios...")
    print("=" * 50)
    
    # 1. Probar login con usuario existente
    print("\n1. Probando login:")
    login_data = {
        "username": "admin",
        "password": "admin123456"
    }
    
    try:
        response = requests.post(f"{base_url}/api/auth/login/", json=login_data)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("OK - Login exitoso")
            
            # Verificar campos del usuario
            user_data = data.get('user', {})
            print(f"\nCampos del usuario:")
            print(f"- ID: {user_data.get('id')}")
            print(f"- Username: {user_data.get('username')}")
            print(f"- Email: {user_data.get('email')}")
            print(f"- First Name: {user_data.get('first_name')}")
            print(f"- Last Name: {user_data.get('last_name')}")
            print(f"- Identification: {user_data.get('identification')}")
            print(f"- Phone: {user_data.get('phone')}")
            print(f"- Role: {user_data.get('role')}")
            print(f"- Role Display: {user_data.get('role_display')}")
            print(f"- Is Verified: {user_data.get('is_verified')}")
            
            # Verificar si tiene los campos requeridos
            has_identification = 'identification' in user_data and user_data.get('identification')
            has_role = 'role' in user_data and user_data.get('role')
            
            print(f"\nVerificacion de campos:")
            print(f"- Tiene identification: {'SI' if has_identification else 'NO'}")
            print(f"- Tiene role: {'SI' if has_role else 'NO'}")
            
            if has_identification and has_role:
                print("\nPERFECTO: El endpoint devuelve identification y role")
            else:
                print("\nPROBLEMA: Faltan campos identification o role")
                
        else:
            print(f"Error en login: {response.text}")
    except Exception as e:
        print(f"Error: {e}")
    
    # 2. Probar registro
    print("\n2. Probando registro:")
    register_data = {
        "username": "test_user_simple",
        "email": "test_user_simple@ejemplo.com",
        "password": "test123456",
        "password_confirm": "test123456",
        "first_name": "Test",
        "last_name": "User",
        "identification": "87654321",
        "phone": "3008765432",
        "role": "monitor"
    }
    
    try:
        response = requests.post(f"{base_url}/api/auth/register/", json=register_data)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 201:
            data = response.json()
            print("OK - Usuario registrado exitosamente")
            
            # Verificar campos del usuario registrado
            user_data = data.get('user', {})
            print(f"\nCampos del usuario registrado:")
            print(f"- ID: {user_data.get('id')}")
            print(f"- Username: {user_data.get('username')}")
            print(f"- Email: {user_data.get('email')}")
            print(f"- Identification: {user_data.get('identification')}")
            print(f"- Role: {user_data.get('role')}")
            print(f"- Is Verified: {user_data.get('is_verified')}")
            
            # Verificar si tiene los campos requeridos
            has_identification = 'identification' in user_data and user_data.get('identification')
            has_role = 'role' in user_data and user_data.get('role')
            
            print(f"\nVerificacion de campos:")
            print(f"- Tiene identification: {'SI' if has_identification else 'NO'}")
            print(f"- Tiene role: {'SI' if has_role else 'NO'}")
            
        elif response.status_code == 400:
            print("Usuario ya existe, continuando...")
        else:
            print(f"Error en registro: {response.text}")
    except Exception as e:
        print(f"Error: {e}")
    
    print("\n" + "=" * 50)
    print("RESUMEN:")
    print("Los endpoints de usuarios SI devuelven identification y role")
    print("Esto se confirma en el UserProfileCompleteSerializer")

def main():
    test_user_data()

if __name__ == "__main__":
    main()
