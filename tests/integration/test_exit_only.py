#!/usr/bin/env python3
"""
Script para probar solo el endpoint de salida
"""

import requests
import json

def test_exit_only():
    """Probar solo el endpoint de salida"""
    base_url = "http://localhost:8000"
    
    print("Probando solo el endpoint de salida...")
    print("=" * 40)
    
    # 1. Login
    print("1. Login...")
    login_data = {"username": "admin", "password": "admin123456"}
    
    try:
        response = requests.post(f"{base_url}/api/auth/login/", json=login_data)
        if response.status_code != 200:
            print(f"Error en login: {response.text}")
            return
        token = response.json().get('token')
        print(f"OK - Token: {token[:20]}...")
    except Exception as e:
        print(f"Error: {e}")
        return
    
    headers = {"Authorization": f"Token {token}"}
    
    # 2. Probar salida de entrada ID 44
    print("\n2. Probando salida de entrada ID 44...")
    try:
        response = requests.patch(f"{base_url}/api/rooms/entry/44/exit/", 
                                json={"notes": "Prueba de salida"}, headers=headers)
        print(f"   -> Status: {response.status_code}")
        print(f"   -> Response: {response.text}")
        
        if response.status_code == 200:
            print("   -> Salida exitosa")
        else:
            print("   -> Error en salida")
    except Exception as e:
        print(f"   -> Error: {e}")

def main():
    test_exit_only()

if __name__ == "__main__":
    main()
