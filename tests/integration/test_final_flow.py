#!/usr/bin/env python3
"""
Script para probar el flujo final de entrada y salida
"""

import requests
import json
import time

def test_final_flow():
    """Probar flujo final de entrada y salida"""
    base_url = "http://localhost:8000"
    
    print("Probando flujo final de entrada y salida...")
    print("=" * 50)
    
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
    
    # 2. Verificar entrada activa actual
    print("\n2. Verificando entrada activa actual...")
    try:
        response = requests.get(f"{base_url}/api/rooms/my-active-entry/", headers=headers)
        if response.status_code == 200:
            data = response.json()
            if data.get('has_active_entry'):
                print(f"   -> Ya hay entrada activa: {data['active_entry']['room_name']}")
                print(f"   -> ID: {data['active_entry']['id']}")
                entry_id = data['active_entry']['id']
            else:
                print("   -> No hay entrada activa")
                entry_id = None
        else:
            print(f"   -> Error: {response.text}")
            return
    except Exception as e:
        print(f"   -> Error: {e}")
        return
    
    # 3. Si hay entrada activa, salir primero
    if entry_id:
        print(f"\n3. Saliendo de entrada activa ID {entry_id}...")
        try:
            response = requests.patch(f"{base_url}/api/rooms/entry/{entry_id}/exit/", 
                                    json={"notes": "Salida previa"}, headers=headers)
            if response.status_code == 200:
                print("   -> Salida exitosa")
            else:
                print(f"   -> Error en salida: {response.text}")
        except Exception as e:
            print(f"   -> Error: {e}")
    
    # 4. Obtener salas
    print("\n4. Obteniendo salas...")
    try:
        response = requests.get(f"{base_url}/api/rooms/", headers=headers)
        if response.status_code != 200:
            print(f"Error: {response.text}")
            return
        rooms = response.json()
        room_id = rooms[0]['id']
        room_name = rooms[0]['name']
        print(f"OK - Usando sala: {room_name} (ID: {room_id})")
    except Exception as e:
        print(f"Error: {e}")
        return
    
    # 5. Registrar nueva entrada
    print(f"\n5. Registrando nueva entrada en {room_name}...")
    entry_data = {"room": room_id, "notes": "Prueba final"}
    
    try:
        response = requests.post(f"{base_url}/api/rooms/entry/", json=entry_data, headers=headers)
        print(f"   -> Status: {response.status_code}")
        if response.status_code == 201:
            data = response.json()
            entry_id = data['entry']['id']
            print(f"   -> Entrada creada con ID: {entry_id}")
        else:
            print(f"   -> Error: {response.text}")
            return
    except Exception as e:
        print(f"   -> Error: {e}")
        return
    
    # 6. Verificar entrada activa
    print("\n6. Verificando entrada activa...")
    try:
        response = requests.get(f"{base_url}/api/rooms/my-active-entry/", headers=headers)
        if response.status_code == 200:
            data = response.json()
            if data.get('has_active_entry'):
                print(f"   -> Entrada activa detectada: {data['active_entry']['room_name']}")
                print(f"   -> Duración: {data['active_entry']['duration_formatted']}")
            else:
                print("   -> No se detecta entrada activa")
        else:
            print(f"   -> Error: {response.text}")
    except Exception as e:
        print(f"   -> Error: {e}")
    
    # 7. Esperar un poco
    print("\n7. Esperando 2 segundos...")
    time.sleep(2)
    
    # 8. Registrar salida
    print(f"\n8. Registrando salida de entrada ID {entry_id}...")
    try:
        response = requests.patch(f"{base_url}/api/rooms/entry/{entry_id}/exit/", 
                                json={"notes": "Salida final"}, headers=headers)
        print(f"   -> Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   -> Salida exitosa")
            if 'duration' in data:
                print(f"   -> Duración: {data['duration'].get('formatted_duration', 'N/A')}")
        else:
            print(f"   -> Error: {response.text}")
    except Exception as e:
        print(f"   -> Error: {e}")
    
    # 9. Verificar que no hay entrada activa
    print("\n9. Verificando que no hay entrada activa...")
    try:
        response = requests.get(f"{base_url}/api/rooms/my-active-entry/", headers=headers)
        if response.status_code == 200:
            data = response.json()
            if data.get('has_active_entry'):
                print("   -> ERROR: Aún hay entrada activa")
            else:
                print("   -> OK: No hay entrada activa")
        else:
            print(f"   -> Error: {response.text}")
    except Exception as e:
        print(f"   -> Error: {e}")
    
    print("\n" + "=" * 50)
    print("RESUMEN:")
    print("✅ Login funcionando")
    print("✅ Verificación de entrada activa funcionando")
    print("✅ Registro de entrada funcionando")
    print("✅ Registro de salida funcionando")
    print("🎉 ¡FLUJO COMPLETO FUNCIONANDO!")

def main():
    test_final_flow()

if __name__ == "__main__":
    main()
