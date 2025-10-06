#!/usr/bin/env python3
"""
Script simple para probar solo el registro de entrada
"""

import requests
import json

def test_simple_entry():
    """Probar registro simple de entrada"""
    base_url = "http://localhost:8000"
    
    print("Probando registro simple de entrada...")
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
    
    # 2. Obtener salas
    print("\n2. Obteniendo salas...")
    try:
        response = requests.get(f"{base_url}/api/rooms/", headers=headers)
        if response.status_code != 200:
            print(f"Error: {response.text}")
            return
        rooms = response.json()
        room_id = rooms[0]['id']
        print(f"OK - Usando sala ID: {room_id}")
    except Exception as e:
        print(f"Error: {e}")
        return
    
    # 3. Registrar entrada
    print(f"\n3. Registrando entrada en sala {room_id}...")
    entry_data = {"room": room_id, "notes": "Prueba simple"}
    
    try:
        response = requests.post(f"{base_url}/api/rooms/entry/", json=entry_data, headers=headers)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 201:
            data = response.json()
            entry_id = data['entry']['id']
            print(f"OK - Entrada creada con ID: {entry_id}")
        else:
            print("Error en registro de entrada")
    except Exception as e:
        print(f"Error: {e}")

def main():
    test_simple_entry()

if __name__ == "__main__":
    main()
