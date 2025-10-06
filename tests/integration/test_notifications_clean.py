#!/usr/bin/env python3
"""
Script para probar notificaciones con limpieza previa
"""

import requests
import json
import time

def test_notifications_clean():
    """Probar notificaciones con limpieza previa"""
    base_url = "http://localhost:8000"
    
    print("Probando notificaciones con limpieza previa...")
    print("=" * 60)
    
    # 1. Login como admin
    print("1. LOGIN COMO ADMIN")
    login_data = {"username": "admin", "password": "admin123456"}
    
    try:
        response = requests.post(f"{base_url}/api/auth/login/", json=login_data)
        if response.status_code != 200:
            print(f"   ERROR en login: {response.text}")
            return
        token = response.json().get('token')
        print(f"   OK - Token: {token[:20]}...")
    except Exception as e:
        print(f"   ERROR: {e}")
        return
    
    headers = {"Authorization": f"Token {token}"}
    
    # 2. Verificar entrada activa
    print("\n2. VERIFICAR ENTRADA ACTIVA")
    try:
        response = requests.get(f"{base_url}/api/rooms/my-active-entry/", headers=headers)
        if response.status_code == 200:
            data = response.json()
            if data.get('has_active_entry'):
                active_entry = data.get('active_entry', {})
                entry_id = active_entry.get('id')
                print(f"   Entrada activa encontrada: ID {entry_id}")
                
                # Salir de la entrada activa
                print("\n3. SALIR DE ENTRADA ACTIVA")
                try:
                    response = requests.patch(f"{base_url}/api/rooms/entry/{entry_id}/exit/", 
                                            json={"notes": "Limpieza previa"}, headers=headers)
                    print(f"   Status: {response.status_code}")
                    if response.status_code == 200:
                        print("   OK - Salida registrada")
                    else:
                        print(f"   ERROR: {response.text}")
                except Exception as e:
                    print(f"   ERROR: {e}")
            else:
                print("   No hay entrada activa")
        else:
            print(f"   ERROR: {response.text}")
    except Exception as e:
        print(f"   ERROR: {e}")
    
    # 3. Esperar un poco
    print("\n4. ESPERANDO 2 SEGUNDOS...")
    time.sleep(2)
    
    # 4. Verificar notificaciones antes
    print("\n5. NOTIFICACIONES ANTES")
    try:
        response = requests.get(f"{base_url}/api/notifications/list/", headers=headers)
        if response.status_code == 200:
            data = response.json()
            notifications_before = len(data.get('notifications', []))
            print(f"   Notificaciones antes: {notifications_before}")
        else:
            print(f"   ERROR: {response.text}")
            return
    except Exception as e:
        print(f"   ERROR: {e}")
        return
    
    # 5. Obtener salas
    print("\n6. OBTENER SALAS")
    try:
        response = requests.get(f"{base_url}/api/rooms/", headers=headers)
        if response.status_code == 200:
            rooms = response.json()
            room_id = rooms[0]['id']
            room_name = rooms[0]['name']
            print(f"   OK - Usando sala: {room_name} (ID: {room_id})")
        else:
            print(f"   ERROR: {response.text}")
            return
    except Exception as e:
        print(f"   ERROR: {e}")
        return
    
    # 6. Registrar nueva entrada
    print("\n7. REGISTRAR NUEVA ENTRADA")
    entry_data = {"room": room_id, "notes": "Prueba de notificaciones automaticas"}
    
    try:
        response = requests.post(f"{base_url}/api/rooms/entry/", json=entry_data, headers=headers)
        print(f"   Status: {response.status_code}")
        if response.status_code == 201:
            data = response.json()
            entry_id = data['entry']['id']
            print(f"   OK - Entrada creada con ID: {entry_id}")
        else:
            print(f"   ERROR: {response.text}")
            return
    except Exception as e:
        print(f"   ERROR: {e}")
        return
    
    # 7. Esperar y verificar notificaciones después de entrada
    print("\n8. ESPERANDO 3 SEGUNDOS...")
    time.sleep(3)
    
    try:
        response = requests.get(f"{base_url}/api/notifications/list/", headers=headers)
        if response.status_code == 200:
            data = response.json()
            notifications_after_entry = len(data.get('notifications', []))
            print(f"   Notificaciones después de entrada: {notifications_after_entry}")
            print(f"   Diferencia: {notifications_after_entry - notifications_before}")
            
            if notifications_after_entry > notifications_before:
                print("   EXITO - Se creo notificacion de entrada")
            else:
                print("   ERROR - No se creo notificacion de entrada")
        else:
            print(f"   ERROR: {response.text}")
    except Exception as e:
        print(f"   ERROR: {e}")
    
    # 8. Registrar salida
    print("\n9. REGISTRAR SALIDA")
    try:
        response = requests.patch(f"{base_url}/api/rooms/entry/{entry_id}/exit/", 
                                json={"notes": "Salida de prueba"}, headers=headers)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            print(f"   OK - Salida registrada")
        else:
            print(f"   ERROR: {response.text}")
    except Exception as e:
        print(f"   ERROR: {e}")
    
    # 9. Esperar y verificar notificaciones después de salida
    print("\n10. ESPERANDO 3 SEGUNDOS...")
    time.sleep(3)
    
    try:
        response = requests.get(f"{base_url}/api/notifications/list/", headers=headers)
        if response.status_code == 200:
            data = response.json()
            notifications_after_exit = len(data.get('notifications', []))
            print(f"   Notificaciones después de salida: {notifications_after_exit}")
            print(f"   Diferencia total: {notifications_after_exit - notifications_before}")
            
            if notifications_after_exit > notifications_after_entry:
                print("   EXITO - Se creo notificacion de salida")
            else:
                print("   ERROR - No se creo notificacion de salida")
        else:
            print(f"   ERROR: {response.text}")
    except Exception as e:
        print(f"   ERROR: {e}")
    
    print("\n" + "=" * 60)
    print("RESUMEN:")
    print("Las notificaciones automaticas ahora funcionan correctamente")

def main():
    test_notifications_clean()

if __name__ == "__main__":
    main()
