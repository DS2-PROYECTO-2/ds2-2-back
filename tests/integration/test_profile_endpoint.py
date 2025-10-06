#!/usr/bin/env python3
"""
Script para probar el endpoint de perfil
"""

import requests
import json

def test_profile():
    """Probar endpoint de perfil"""
    base_url = "http://localhost:8000"
    
    print("Probando endpoint de perfil...")
    print("=" * 50)
    
    # 1. Login para obtener token
    print("1. Obteniendo token...")
    login_data = {
        "username": "admin",
        "password": "admin123456"
    }
    
    try:
        response = requests.post(f"{base_url}/api/auth/login/", json=login_data)
        if response.status_code == 200:
            data = response.json()
            token = data.get('token')
            print(f"OK - Token obtenido: {token[:20]}...")
        else:
            print(f"Error en login: {response.text}")
            return
    except Exception as e:
        print(f"Error: {e}")
        return
    
    # 2. Probar endpoint de perfil
    print("\n2. Probando endpoint de perfil:")
    headers = {"Authorization": f"Token {token}"}
    
    try:
        response = requests.get(f"{base_url}/api/auth/profile/", headers=headers)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("OK - Perfil obtenido exitosamente")
            print(f"Response: {json.dumps(data, indent=2, ensure_ascii=False)}")
            
            # Verificar campos del perfil
            print(f"\nCampos del perfil:")
            print(f"- Username: {data.get('username')}")
            print(f"- Email: {data.get('email')}")
            print(f"- First Name: {data.get('first_name')}")
            print(f"- Last Name: {data.get('last_name')}")
            print(f"- Identification: {data.get('identification')}")
            print(f"- Phone: {data.get('phone')}")
            
            # Verificar si tiene los campos requeridos
            has_identification = 'identification' in data and data.get('identification')
            has_phone = 'phone' in data
            
            print(f"\nVerificacion de campos:")
            print(f"- Tiene identification: {'SI' if has_identification else 'NO'}")
            print(f"- Tiene phone: {'SI' if has_phone else 'NO'}")
            
        else:
            print(f"Error en perfil: {response.text}")
    except Exception as e:
        print(f"Error: {e}")
    
    print("\n" + "=" * 50)
    print("RESUMEN:")
    print("El endpoint de perfil devuelve los campos basicos del usuario")
    print("Para campos completos (incluyendo role), usar el endpoint de login")

def main():
    test_profile()

if __name__ == "__main__":
    main()
