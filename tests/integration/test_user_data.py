#!/usr/bin/env python3
"""
Script para probar que el endpoint de usuarios devuelva identification y role
"""

import requests
import json

def test_user_endpoints():
    """Probar endpoints de usuarios"""
    base_url = "http://localhost:8000"
    
    print("Probando endpoints de usuarios...")
    print("=" * 50)
    
    # 1. Probar registro
    print("\n1. Probando registro de usuario:")
    register_data = {
        "username": "test_user_data",
        "email": "test_user_data@ejemplo.com",
        "password": "test123456",
        "password_confirm": "test123456",
        "first_name": "Test",
        "last_name": "User",
        "identification": "12345678",
        "phone": "3001234567",
        "role": "monitor"
    }
    
    try:
        response = requests.post(f"{base_url}/api/auth/register/", json=register_data)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 201:
            data = response.json()
            print("✅ Usuario registrado exitosamente")
            print(f"Response: {json.dumps(data, indent=2, ensure_ascii=False)}")
            
            # Verificar campos
            user_data = data.get('user', {})
            print(f"\nCampos del usuario:")
            print(f"- ID: {user_data.get('id')}")
            print(f"- Username: {user_data.get('username')}")
            print(f"- Email: {user_data.get('email')}")
            print(f"- Identification: {user_data.get('identification')}")
            print(f"- Role: {user_data.get('role')}")
            print(f"- Is Verified: {user_data.get('is_verified')}")
            
        elif response.status_code == 400:
            print("ℹ️ Usuario ya existe, continuando con login...")
        else:
            print(f"❌ Error en registro: {response.text}")
            return
    except Exception as e:
        print(f"❌ Error: {e}")
        return
    
    # 2. Probar login
    print("\n2. Probando login:")
    login_data = {
        "username": "test_user_data",
        "password": "test123456"
    }
    
    try:
        response = requests.post(f"{base_url}/api/auth/login/", json=login_data)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Login exitoso")
            print(f"Response: {json.dumps(data, indent=2, ensure_ascii=False)}")
            
            # Verificar campos del usuario en login
            user_data = data.get('user', {})
            print(f"\nCampos del usuario en login:")
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
            print(f"- Date Joined: {user_data.get('date_joined')}")
            
            # Verificar si tiene los campos requeridos
            has_identification = 'identification' in user_data
            has_role = 'role' in user_data
            
            print(f"\nVerificacion de campos:")
            print(f"- Tiene identification: {'✅' if has_identification else '❌'}")
            print(f"- Tiene role: {'✅' if has_role else '❌'}")
            
            if has_identification and has_role:
                print("\n🎉 PERFECTO: El endpoint devuelve identification y role")
            else:
                print("\n❌ PROBLEMA: Faltan campos identification o role")
                
        else:
            print(f"❌ Error en login: {response.text}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # 3. Probar perfil
    print("\n3. Probando endpoint de perfil:")
    try:
        # Obtener token del login anterior
        login_response = requests.post(f"{base_url}/api/auth/login/", json=login_data)
        if login_response.status_code == 200:
            token = login_response.json().get('token')
            headers = {"Authorization": f"Token {token}"}
            
            response = requests.get(f"{base_url}/api/auth/profile/", headers=headers)
            print(f"Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print("✅ Perfil obtenido exitosamente")
                print(f"Response: {json.dumps(data, indent=2, ensure_ascii=False)}")
                
                # Verificar campos del perfil
                print(f"\nCampos del perfil:")
                print(f"- Username: {data.get('username')}")
                print(f"- Email: {data.get('email')}")
                print(f"- First Name: {data.get('first_name')}")
                print(f"- Last Name: {data.get('last_name')}")
                print(f"- Identification: {data.get('identification')}")
                print(f"- Phone: {data.get('phone')}")
                
            else:
                print(f"❌ Error en perfil: {response.text}")
        else:
            print("❌ No se pudo obtener token para probar perfil")
    except Exception as e:
        print(f"❌ Error: {e}")

def main():
    test_user_endpoints()

if __name__ == "__main__":
    main()
