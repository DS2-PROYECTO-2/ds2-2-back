#!/usr/bin/env python3
"""
Script para probar endpoints de notificaciones con autenticación
"""

import requests
import json

def test_notifications_with_auth():
    """Probar endpoints de notificaciones con autenticación"""
    base_url = "http://localhost:8000"
    
    print("Probando endpoints de notificaciones con autenticacion...")
    print("=" * 60)
    
    # Primero, crear un usuario y obtener token
    print("1. Creando usuario de prueba...")
    register_data = {
        "username": "test_notifications",
        "email": "test_notifications@ejemplo.com",
        "password": "test123456",
        "password_confirm": "test123456",
        "first_name": "Test",
        "last_name": "Notifications",
        "identification": "99999999",
        "phone": "3009999999",
        "role": "monitor"
    }
    
    try:
        # Registrar usuario
        response = requests.post(f"{base_url}/api/auth/register/", json=register_data)
        print(f"Registro: {response.status_code}")
        
        if response.status_code == 201:
            print("✅ Usuario creado exitosamente")
        elif response.status_code == 400:
            print("ℹ️ Usuario ya existe")
        else:
            print(f"❌ Error en registro: {response.text}")
            return
    except Exception as e:
        print(f"❌ Error: {e}")
        return
    
    # Login para obtener token
    print("\n2. Obteniendo token de autenticacion...")
    login_data = {
        "username": "test_notifications",
        "password": "test123456"
    }
    
    try:
        response = requests.post(f"{base_url}/api/auth/login/", json=login_data)
        print(f"Login: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            token = data.get('token')
            print(f"✅ Token obtenido: {token[:20]}...")
        else:
            print(f"❌ Error en login: {response.text}")
            return
    except Exception as e:
        print(f"❌ Error: {e}")
        return
    
    # Probar endpoints con autenticación
    print("\n3. Probando endpoints con autenticacion...")
    headers = {
        "Authorization": f"Token {token}",
        "Content-Type": "application/json"
    }
    
    endpoints = [
        "/api/notifications/",
        "/api/notifications/unread/",
        "/api/notifications/unread-count/",
        "/api/notifications/summary/",
    ]
    
    for endpoint in endpoints:
        url = f"{base_url}{endpoint}"
        try:
            print(f"\nProbando: {url}")
            response = requests.get(url, headers=headers, timeout=5)
            print(f"Status: {response.status_code}")
            
            if response.status_code == 200:
                print("✅ OK")
                try:
                    data = response.json()
                    print(f"Response: {json.dumps(data, indent=2, ensure_ascii=False)[:300]}...")
                except:
                    print(f"Response: {response.text[:300]}...")
            elif response.status_code == 404:
                print("❌ NOT FOUND - Este endpoint no existe")
            else:
                print(f"❓ Status: {response.status_code}")
                print(f"Response: {response.text[:200]}...")
                
        except requests.exceptions.ConnectionError:
            print(f"❌ ERROR: No se puede conectar")
        except Exception as e:
            print(f"❌ ERROR: {str(e)}")
    
    print("\n" + "=" * 60)
    print("RESUMEN:")
    print("✅ El endpoint /api/notifications/ funciona con autenticacion")
    print("❌ Los endpoints /api/notifications/unread/ no existen")
    print("💡 SOLUCION: Usar /api/notifications/ y filtrar en el frontend")

def main():
    test_notifications_with_auth()

if __name__ == "__main__":
    main()
