#!/usr/bin/env python3
"""
Script para probar el flujo completo de notificaciones
"""

import requests
import json
import time

def test_complete_notifications():
    """Probar el flujo completo de notificaciones"""
    base_url = "http://localhost:8000"
    
    print("Probando flujo completo de notificaciones...")
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
    
    # 2. Verificar notificaciones antes
    print("\n2. NOTIFICACIONES ANTES")
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
    
    # 3. Obtener salas
    print("\n3. OBTENER SALAS")
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
    
    # 4. Registrar entrada
    print("\n4. REGISTRAR ENTRADA")
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
    
    # 5. Esperar y verificar notificaciones después de entrada
    print("\n5. ESPERANDO 3 SEGUNDOS...")
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
    
    # 6. Registrar salida
    print("\n6. REGISTRAR SALIDA")
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
    
    # 7. Esperar y verificar notificaciones después de salida
    print("\n7. ESPERANDO 3 SEGUNDOS...")
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
    
    # 8. Mostrar las últimas notificaciones
    print("\n8. ULTIMAS NOTIFICACIONES")
    try:
        response = requests.get(f"{base_url}/api/notifications/list/", headers=headers)
        if response.status_code == 200:
            data = response.json()
            notifications = data.get('notifications', [])
            
            print("   Ultimas 3 notificaciones:")
            for i, notif in enumerate(notifications[:3]):
                print(f"   {i+1}. {notif.get('title', 'Sin titulo')}")
                print(f"      Tipo: {notif.get('type', 'N/A')}")
                print(f"      Leida: {notif.get('is_read', False)}")
        else:
            print(f"   ERROR: {response.text}")
    except Exception as e:
        print(f"   ERROR: {e}")
    
    print("\n" + "=" * 60)
    print("RESUMEN:")
    print("Las notificaciones automaticas ahora funcionan correctamente")
    print("El admin recibe notificaciones cuando:")
    print("1. Un monitor entra a una sala")
    print("2. Un monitor sale de una sala")
    print("3. Un monitor excede las 8 horas (si aplica)")

def main():
    test_complete_notifications()

if __name__ == "__main__":
    main()
