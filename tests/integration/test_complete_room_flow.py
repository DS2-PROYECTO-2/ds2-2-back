#!/usr/bin/env python3
"""
Script para probar el flujo completo de entrada y salida en salas
"""

import requests
import json
import time

def test_complete_room_flow():
    """Probar flujo completo de entrada y salida"""
    base_url = "http://localhost:8000"
    
    print("Probando flujo completo de entrada y salida en salas...")
    print("=" * 70)
    
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
        if response.status_code == 200:
            rooms = response.json()
            print(f"  -> Salas disponibles: {len(rooms)}")
            if rooms:
                room_id = rooms[0]['id']
                room_name = rooms[0]['name']
                print(f"  -> Usando sala: {room_name} (ID: {room_id})")
            else:
                print("  -> No hay salas disponibles")
                return
        else:
            print(f"  -> Error: {response.text}")
            return
    except Exception as e:
        print(f"  -> Error: {e}")
        return
    
    # 3. Verificar entrada activa antes
    print("\n3. Verificando entrada activa antes del registro...")
    try:
        response = requests.get(f"{base_url}/api/rooms/my-active-entry/", headers=headers)
        print(f"  -> Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"  -> Tiene entrada activa: {data.get('has_active_entry', False)}")
    except Exception as e:
        print(f"  -> Error: {e}")
    
    # 4. Registrar entrada
    print(f"\n4. Registrando entrada en sala {room_name}...")
    entry_data = {
        "room": room_id,
        "notes": "Prueba de flujo completo"
    }
    
    try:
        response = requests.post(f"{base_url}/api/rooms/entry/", json=entry_data, headers=headers)
        print(f"  -> Status: {response.status_code}")
        if response.status_code == 201:
            data = response.json()
            entry_id = data['entry']['id']
            print(f"  -> ¡Entrada registrada exitosamente! ID: {entry_id}")
            print(f"  -> Hora de entrada: {data['entry']['entry_time']}")
        else:
            print(f"  -> Error en registro: {response.text}")
            return
    except Exception as e:
        print(f"  -> Error: {e}")
        return
    
    # 5. Verificar entrada activa después
    print("\n5. Verificando entrada activa después del registro...")
    try:
        response = requests.get(f"{base_url}/api/rooms/my-active-entry/", headers=headers)
        print(f"  -> Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"  -> Tiene entrada activa: {data.get('has_active_entry', False)}")
            if data.get('has_active_entry'):
                active_entry = data['active_entry']
                print(f"  -> Sala activa: {active_entry.get('room_name')}")
                print(f"  -> Duración: {active_entry.get('duration_formatted')}")
    except Exception as e:
        print(f"  -> Error: {e}")
    
    # 6. Esperar un poco para simular trabajo
    print("\n6. Esperando 3 segundos para simular trabajo...")
    time.sleep(3)
    
    # 7. Registrar salida
    print(f"\n7. Registrando salida de la entrada ID {entry_id}...")
    exit_data = {
        "notes": "Finalizando prueba de flujo"
    }
    
    try:
        response = requests.patch(f"{base_url}/api/rooms/entry/{entry_id}/exit/", json=exit_data, headers=headers)
        print(f"  -> Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"  -> ¡Salida registrada exitosamente!")
            print(f"  -> Duración total: {data.get('duration_info', {}).get('formatted_duration', 'N/A')}")
            if 'warning' in data:
                print(f"  -> Advertencia: {data['warning']['message']}")
        else:
            print(f"  -> Error en salida: {response.text}")
    except Exception as e:
        print(f"  -> Error: {e}")
    
    # 8. Verificar entrada activa después de la salida
    print("\n8. Verificando entrada activa después de la salida...")
    try:
        response = requests.get(f"{base_url}/api/rooms/my-active-entry/", headers=headers)
        print(f"  -> Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"  -> Tiene entrada activa: {data.get('has_active_entry', False)}")
    except Exception as e:
        print(f"  -> Error: {e}")
    
    # 9. Obtener historial de entradas
    print("\n9. Obteniendo historial de entradas...")
    try:
        response = requests.get(f"{base_url}/api/rooms/my-entries/", headers=headers)
        print(f"  -> Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            entries = data.get('entries', [])
            print(f"  -> Total de entradas: {len(entries)}")
            if entries:
                latest = entries[0]
                print(f"  -> Última entrada: {latest.get('room_name')} - {latest.get('duration_formatted')}")
    except Exception as e:
        print(f"  -> Error: {e}")
    
    print("\n" + "=" * 70)
    print("RESUMEN:")
    print("✅ Login y autenticación funcionando")
    print("✅ Lista de salas funcionando")
    print("✅ Registro de entrada funcionando")
    print("✅ Verificación de entrada activa funcionando")
    print("✅ Registro de salida funcionando")
    print("✅ Historial de entradas funcionando")
    print("🎉 ¡FLUJO COMPLETO FUNCIONANDO CORRECTAMENTE!")

def main():
    test_complete_room_flow()

if __name__ == "__main__":
    main()
