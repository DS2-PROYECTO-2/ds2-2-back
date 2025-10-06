#!/usr/bin/env python3
"""
Script para ver las notificaciones del admin (sin emojis)
"""

import requests
import json

def test_notifications_simple():
    """Ver notificaciones del admin"""
    base_url = "http://localhost:8000"
    
    print("Notificaciones del admin...")
    print("=" * 40)
    
    # 1. Login como admin
    login_data = {"username": "admin", "password": "admin123456"}
    
    try:
        response = requests.post(f"{base_url}/api/auth/login/", json=login_data)
        if response.status_code != 200:
            print(f"ERROR en login: {response.text}")
            return
        token = response.json().get('token')
        print(f"OK - Token: {token[:20]}...")
    except Exception as e:
        print(f"ERROR: {e}")
        return
    
    headers = {"Authorization": f"Token {token}"}
    
    # 2. Ver notificaciones
    print("\nNOTIFICACIONES DEL ADMIN:")
    try:
        response = requests.get(f"{base_url}/api/notifications/list/", headers=headers)
        if response.status_code == 200:
            data = response.json()
            notifications = data.get('notifications', [])
            print(f"Total: {len(notifications)}")
            
            for i, notif in enumerate(notifications[:5]):
                print(f"\n{i+1}. {notif.get('title', 'Sin titulo')}")
                print(f"   Tipo: {notif.get('type', 'N/A')}")
                print(f"   Leida: {notif.get('is_read', False)}")
                print(f"   Creada: {notif.get('created_at', 'N/A')}")
                if 'message' in notif:
                    message = notif['message'][:100] + "..." if len(notif['message']) > 100 else notif['message']
                    print(f"   Mensaje: {message}")
        else:
            print(f"ERROR: {response.text}")
    except Exception as e:
        print(f"ERROR: {e}")
    
    # 3. Contador de no leídas
    print("\nCONTADOR DE NO LEIDAS:")
    try:
        response = requests.get(f"{base_url}/api/notifications/unread-count/", headers=headers)
        if response.status_code == 200:
            data = response.json()
            unread_count = data.get('unread_count', 0)
            print(f"No leidas: {unread_count}")
        else:
            print(f"ERROR: {response.text}")
    except Exception as e:
        print(f"ERROR: {e}")

def main():
    test_notifications_simple()

if __name__ == "__main__":
    main()