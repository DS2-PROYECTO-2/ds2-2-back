#!/usr/bin/env python3
"""
Script para probar el registro de entrada en salas
"""

import requests
import json

def test_room_entry():
    """Probar registro de entrada en salas"""
    base_url = "http://localhost:8000"
    
    print("Probando registro de entrada en salas...")
    print("=" * 60)
    
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
    
    # 2. Obtener lista de salas
    print("\n2. Obteniendo lista de salas...")
    try:
        response = requests.get(f"{base_url}/api/rooms/", headers=headers)
        print(f"/api/rooms/ - Status: {response.status_code}")
        if response.status_code == 200:
            rooms = response.json()
            print(f"  -> Salas disponibles: {len(rooms)}")
            if rooms:
                room_id = rooms[0]['id']
                print(f"  -> Usando sala ID: {room_id}")
            else:
                print("  -> No hay salas disponibles")
                return
        else:
            print(f"  -> Error: {response.text}")
            return
    except Exception as e:
        print(f"  -> Error: {e}")
        return
    
    # 3. Probar registro de entrada
    print(f"\n3. Probando registro de entrada en sala {room_id}...")
    entry_data = {
        "room": room_id,
        "notes": "Prueba de entrada"
    }
    
    try:
        response = requests.post(f"{base_url}/api/rooms/entry/", json=entry_data, headers=headers)
        print(f"/api/rooms/entry/ - Status: {response.status_code}")
        print(f"  -> Response: {response.text}")
        
        if response.status_code == 201:
            print("  -> ¡Entrada registrada exitosamente!")
        else:
            print(f"  -> Error en registro: {response.text}")
    except Exception as e:
        print(f"  -> Error: {e}")
    
    # 4. Verificar entrada activa
    print("\n4. Verificando entrada activa...")
    try:
        response = requests.get(f"{base_url}/api/rooms/my-active-entry/", headers=headers)
        print(f"/api/rooms/my-active-entry/ - Status: {response.status_code}")
        print(f"  -> Response: {response.text}")
    except Exception as e:
        print(f"  -> Error: {e}")

def main():
    test_room_entry()

if __name__ == "__main__":
    main()
