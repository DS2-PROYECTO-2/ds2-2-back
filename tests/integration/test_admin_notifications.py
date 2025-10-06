#!/usr/bin/env python3
"""
Script para probar las notificaciones que recibe el admin
"""

import requests
import json
import time

def test_admin_notifications():
    """Probar notificaciones del admin"""
    base_url = "http://localhost:8000"
    
    print("Probando notificaciones del admin...")
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
    print("\n2. NOTIFICACIONES ANTES DE LA PRUEBA")
    try:
        response = requests.get(f"{base_url}/api/notifications/list/", headers=headers)
        if response.status_code == 200:
            data = response.json()
            notifications = data.get('notifications', [])
            print(f"   Notificaciones actuales: {len(notifications)}")
            
            # Mostrar las últimas 3 notificaciones
            for i, notif in enumerate(notifications[:3]):
                print(f"   {i+1}. {notif.get('title', 'Sin título')}")
                print(f"      Tipo: {notif.get('type', 'N/A')}")
                print(f"      Leída: {notif.get('is_read', False)}")
        else:
            print(f"   ERROR: {response.text}")
    except Exception as e:
        print(f"   ERROR: {e}")
    
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
    
    # 4. Registrar entrada (debería generar notificación)
    print("\n4. REGISTRAR ENTRADA (GENERA NOTIFICACIÓN)")
    entry_data = {"room": room_id, "notes": "Prueba de notificaciones"}
    
    try:
        response = requests.post(f"{base_url}/api/rooms/entry/", json=entry_data, headers=headers)
        print(f"   Status: {response.status_code}")
        if response.status_code == 201:
            data = response.json()
            entry_id = data['entry']['id']
            print(f"   OK - Entrada creada con ID: {entry_id}")
            print(f"   Sala: {data['entry']['room_name']}")
        else:
            print(f"   ERROR: {response.text}")
            return
    except Exception as e:
        print(f"   ERROR: {e}")
        return
    
    # 5. Esperar un poco para que se procese la notificación
    print("\n5. ESPERANDO 2 SEGUNDOS...")
    time.sleep(2)
    
    # 6. Verificar notificaciones después de la entrada
    print("\n6. NOTIFICACIONES DESPUÉS DE LA ENTRADA")
    try:
        response = requests.get(f"{base_url}/api/notifications/list/", headers=headers)
        if response.status_code == 200:
            data = response.json()
            notifications = data.get('notifications', [])
            print(f"   Total de notificaciones: {len(notifications)}")
            
            # Mostrar las notificaciones más recientes
            for i, notif in enumerate(notifications[:3]):
                print(f"   {i+1}. {notif.get('title', 'Sin título')}")
                print(f"      Tipo: {notif.get('type', 'N/A')}")
                print(f"      Mensaje: {notif.get('message', 'N/A')[:100]}...")
                print(f"      Leída: {notif.get('is_read', False)}")
                print(f"      Creada: {notif.get('created_at', 'N/A')}")
                print()
        else:
            print(f"   ERROR: {response.text}")
    except Exception as e:
        print(f"   ERROR: {e}")
    
    # 7. Registrar salida (debería generar otra notificación)
    print("\n7. REGISTRAR SALIDA (GENERA NOTIFICACIÓN)")
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
    
    # 8. Esperar un poco
    print("\n8. ESPERANDO 2 SEGUNDOS...")
    time.sleep(2)
    
    # 9. Verificar notificaciones después de la salida
    print("\n9. NOTIFICACIONES DESPUÉS DE LA SALIDA")
    try:
        response = requests.get(f"{base_url}/api/notifications/list/", headers=headers)
        if response.status_code == 200:
            data = response.json()
            notifications = data.get('notifications', [])
            print(f"   Total de notificaciones: {len(notifications)}")
            
            # Mostrar las notificaciones más recientes
            for i, notif in enumerate(notifications[:5]):
                print(f"   {i+1}. {notif.get('title', 'Sin título')}")
                print(f"      Tipo: {notif.get('type', 'N/A')}")
                print(f"      Leída: {notif.get('is_read', False)}")
                print()
        else:
            print(f"   ERROR: {response.text}")
    except Exception as e:
        print(f"   ERROR: {e}")
    
    # 10. Contador de no leídas
    print("\n10. CONTADOR DE NO LEÍDAS")
    try:
        response = requests.get(f"{base_url}/api/notifications/unread-count/", headers=headers)
        if response.status_code == 200:
            data = response.json()
            unread_count = data.get('unread_count', 0)
            print(f"   No leídas: {unread_count}")
        else:
            print(f"   ERROR: {response.text}")
    except Exception as e:
        print(f"   ERROR: {e}")
    
    print("\n" + "=" * 60)
    print("RESUMEN DE NOTIFICACIONES DEL ADMIN:")
    print("1. Entrada a sala - Se genera cuando un monitor entra")
    print("2. Salida de sala - Se genera cuando un monitor sale")
    print("3. Exceso de horas - Se genera cuando un monitor excede 8 horas")
    print("4. Verificación de usuario - Se genera cuando se verifica un usuario")
    print("5. Reportes de equipo - Se genera cuando hay problemas con equipos")
    print("6. Listado de asistencia - Se genera para reportes de asistencia")

def main():
    test_admin_notifications()

if __name__ == "__main__":
    main()
