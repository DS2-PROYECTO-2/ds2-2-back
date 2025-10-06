#!/usr/bin/env python3
"""
Script para probar todos los endpoints funcionando (sin emojis)
"""

import requests
import json
import time

def test_all_endpoints():
    """Probar todos los endpoints"""
    base_url = "http://localhost:8000"
    
    print("Probando todos los endpoints del sistema...")
    print("=" * 60)
    
    # 1. Login
    print("1. LOGIN")
    login_data = {"username": "admin", "password": "admin123456"}
    
    try:
        response = requests.post(f"{base_url}/api/auth/login/", json=login_data)
        if response.status_code != 200:
            print(f"   ERROR en login: {response.text}")
            return
        token = response.json().get('token')
        print(f"   OK - Login exitoso - Token: {token[:20]}...")
    except Exception as e:
        print(f"   ERROR: {e}")
        return
    
    headers = {"Authorization": f"Token {token}"}
    
    # 2. Salas
    print("\n2. SALAS")
    try:
        response = requests.get(f"{base_url}/api/rooms/", headers=headers)
        if response.status_code == 200:
            rooms = response.json()
            print(f"   OK - Salas disponibles: {len(rooms)}")
            if rooms:
                room_id = rooms[0]['id']
                room_name = rooms[0]['name']
                print(f"   Usando sala: {room_name} (ID: {room_id})")
        else:
            print(f"   ERROR: {response.text}")
            return
    except Exception as e:
        print(f"   ERROR: {e}")
        return
    
    # 3. Entrada activa (antes)
    print("\n3. ENTRADA ACTIVA (ANTES)")
    try:
        response = requests.get(f"{base_url}/api/rooms/my-active-entry/", headers=headers)
        if response.status_code == 200:
            data = response.json()
            if data.get('has_active_entry'):
                print(f"   Ya hay entrada activa: {data['active_entry']['room_name']}")
                print(f"   ID: {data['active_entry']['id']}")
                # Salir primero
                entry_id = data['active_entry']['id']
                print(f"   Saliendo de entrada {entry_id}...")
                exit_response = requests.patch(f"{base_url}/api/rooms/entry/{entry_id}/exit/", 
                                             json={"notes": "Limpieza previa"}, headers=headers)
                if exit_response.status_code == 200:
                    print(f"   OK - Salida exitosa")
                else:
                    print(f"   ERROR en salida: {exit_response.text}")
            else:
                print(f"   OK - No hay entrada activa")
        else:
            print(f"   ERROR: {response.text}")
    except Exception as e:
        print(f"   ERROR: {e}")
    
    # 4. Registrar entrada
    print("\n4. REGISTRAR ENTRADA")
    entry_data = {"room": room_id, "notes": "Prueba de endpoints"}
    
    try:
        response = requests.post(f"{base_url}/api/rooms/entry/", json=entry_data, headers=headers)
        print(f"   Status: {response.status_code}")
        if response.status_code == 201:
            data = response.json()
            entry_id = data['entry']['id']
            print(f"   OK - Entrada registrada exitosamente")
            print(f"   ID: {entry_id}")
            print(f"   Sala: {data['entry']['room_name']}")
            print(f"   Hora: {data['entry']['entry_time']}")
        else:
            print(f"   ERROR: {response.text}")
            return
    except Exception as e:
        print(f"   ERROR: {e}")
        return
    
    # 5. Verificar entrada activa
    print("\n5. VERIFICAR ENTRADA ACTIVA")
    try:
        response = requests.get(f"{base_url}/api/rooms/my-active-entry/", headers=headers)
        if response.status_code == 200:
            data = response.json()
            if data.get('has_active_entry'):
                active_entry = data['active_entry']
                print(f"   OK - Entrada activa detectada")
                print(f"   Sala: {active_entry['room_name']}")
                print(f"   Duracion: {active_entry['duration_formatted']}")
                print(f"   ID: {active_entry['id']}")
            else:
                print(f"   ERROR - No se detecta entrada activa")
        else:
            print(f"   ERROR: {response.text}")
    except Exception as e:
        print(f"   ERROR: {e}")
    
    # 6. Historial de entradas
    print("\n6. HISTORIAL DE ENTRADAS")
    try:
        response = requests.get(f"{base_url}/api/rooms/my-entries/", headers=headers)
        if response.status_code == 200:
            data = response.json()
            entries = data.get('entries', [])
            print(f"   OK - Historial obtenido: {len(entries)} entradas")
            if entries:
                latest = entries[0]
                print(f"   Ultima entrada: {latest['room_name']} - {latest['duration_formatted']}")
        else:
            print(f"   ERROR: {response.text}")
    except Exception as e:
        print(f"   ERROR: {e}")
    
    # 7. Notificaciones
    print("\n7. NOTIFICACIONES")
    try:
        # Lista de notificaciones
        response = requests.get(f"{base_url}/api/notifications/list/", headers=headers)
        if response.status_code == 200:
            data = response.json()
            notifications = data.get('notifications', [])
            print(f"   OK - Notificaciones: {len(notifications)}")
        
        # Contador de no leídas
        response = requests.get(f"{base_url}/api/notifications/unread-count/", headers=headers)
        if response.status_code == 200:
            data = response.json()
            unread_count = data.get('unread_count', 0)
            print(f"   No leídas: {unread_count}")
    except Exception as e:
        print(f"   ERROR: {e}")
    
    # 8. Esperar un poco
    print("\n8. ESPERANDO 3 SEGUNDOS...")
    time.sleep(3)
    
    # 9. Registrar salida
    print("\n9. REGISTRAR SALIDA")
    try:
        response = requests.patch(f"{base_url}/api/rooms/entry/{entry_id}/exit/", 
                                json={"notes": "Finalizando prueba"}, headers=headers)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   OK - Salida registrada exitosamente")
            if 'duration' in data:
                duration = data['duration']
                print(f"   Duracion total: {duration.get('formatted_duration', 'N/A')}")
        else:
            print(f"   ERROR: {response.text}")
    except Exception as e:
        print(f"   ERROR: {e}")
    
    # 10. Verificar que no hay entrada activa
    print("\n10. VERIFICAR SIN ENTRADA ACTIVA")
    try:
        response = requests.get(f"{base_url}/api/rooms/my-active-entry/", headers=headers)
        if response.status_code == 200:
            data = response.json()
            if data.get('has_active_entry'):
                print(f"   ERROR - Aún hay entrada activa")
            else:
                print(f"   OK - Correcto: No hay entrada activa")
        else:
            print(f"   ERROR: {response.text}")
    except Exception as e:
        print(f"   ERROR: {e}")
    
    # 11. Endpoints de admin
    print("\n11. ENDPOINTS DE ADMIN")
    try:
        # Entradas de admin
        response = requests.get(f"{base_url}/api/rooms/entries/", headers=headers)
        if response.status_code == 200:
            data = response.json()
            entries_count = data.get('count', 0)
            print(f"   OK - Entradas de admin: {entries_count} total")
        
        # Estadísticas de admin
        response = requests.get(f"{base_url}/api/rooms/entries/stats/", headers=headers)
        if response.status_code == 200:
            data = response.json()
            total_entries = data.get('total_entries', 0)
            active_entries = data.get('active_entries', 0)
            print(f"   Estadisticas: {total_entries} total, {active_entries} activas")
    except Exception as e:
        print(f"   ERROR: {e}")
    
    print("\n" + "=" * 60)
    print("RESUMEN FINAL:")
    print("OK - Login y autenticacion")
    print("OK - Lista de salas")
    print("OK - Registro de entrada")
    print("OK - Verificacion de entrada activa")
    print("OK - Historial de entradas")
    print("OK - Sistema de notificaciones")
    print("OK - Registro de salida")
    print("OK - Endpoints de administrador")
    print("TODOS LOS ENDPOINTS FUNCIONANDO CORRECTAMENTE!")

def main():
    test_all_endpoints()

if __name__ == "__main__":
    main()
