#!/usr/bin/env python3
"""
Script para probar solo el endpoint de entrada activa
"""

import requests
import json

def test_active_entry():
    """Probar endpoint de entrada activa"""
    base_url = "http://localhost:8000"
    
    print("Probando endpoint de entrada activa...")
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
    
    headers = {"Authorization": f"Token {token}"}
    
    # 2. Probar endpoint de entrada activa
    print("\n2. Probando endpoint de entrada activa...")
    try:
        response = requests.get(f"{base_url}/api/rooms/my-active-entry/", headers=headers)
        print(f"  -> Status: {response.status_code}")
        print(f"  -> Response: {response.text}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"  -> has_active_entry: {data.get('has_active_entry')}")
            if data.get('has_active_entry'):
                active_entry = data.get('active_entry')
                print(f"  -> active_entry ID: {active_entry.get('id')}")
                print(f"  -> Sala: {active_entry.get('room_name')}")
    except Exception as e:
        print(f"  -> Error: {e}")
    
    # 3. Probar endpoint de historial
    print("\n3. Probando endpoint de historial...")
    try:
        response = requests.get(f"{base_url}/api/rooms/my-entries/", headers=headers)
        print(f"  -> Status: {response.status_code}")
        print(f"  -> Response: {response.text}")
    except Exception as e:
        print(f"  -> Error: {e}")

def main():
    test_active_entry()

if __name__ == "__main__":
    main()
