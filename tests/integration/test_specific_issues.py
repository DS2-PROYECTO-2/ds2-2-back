#!/usr/bin/env python3
"""
Script para probar los problemas específicos identificados
"""

import requests
import json

def test_specific_issues():
    """Probar los problemas específicos del backend"""
    base_url = "http://localhost:8000"
    
    print("Probando problemas específicos del backend...")
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
        print(f"   OK - Token: {token[:20]}...")
    except Exception as e:
        print(f"   ERROR: {e}")
        return
    
    headers = {"Authorization": f"Token {token}"}
    
    # 2. Obtener salas
    print("\n2. OBTENER SALAS")
    try:
        response = requests.get(f"{base_url}/api/rooms/", headers=headers)
        if response.status_code == 200:
            rooms = response.json()
            room_id = rooms[0]['id']
            print(f"   OK - Usando sala ID: {room_id}")
        else:
            print(f"   ERROR: {response.text}")
            return
    except Exception as e:
        print(f"   ERROR: {e}")
        return
    
    # 3. Registrar entrada
    print("\n3. REGISTRAR ENTRADA")
    entry_data = {"room": room_id, "notes": "Prueba de problemas específicos"}
    
    try:
        response = requests.post(f"{base_url}/api/rooms/entry/", json=entry_data, headers=headers)
        print(f"   Status: {response.status_code}")
        if response.status_code == 201:
            data = response.json()
            entry_id = data['entry']['id']
            print(f"   OK - Entrada creada con ID: {entry_id}")
            print(f"   Sala: {data['entry']['room_name']}")
            print(f"   Hora: {data['entry']['entry_time']}")
            print(f"   is_active: {data['entry']['is_active']}")
        else:
            print(f"   ERROR: {response.text}")
            return
    except Exception as e:
        print(f"   ERROR: {e}")
        return
    
    # 4. Verificar entrada activa INMEDIATAMENTE
    print("\n4. VERIFICAR ENTRADA ACTIVA (INMEDIATAMENTE)")
    try:
        response = requests.get(f"{base_url}/api/rooms/my-active-entry/", headers=headers)
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.text}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   has_active_entry: {data.get('has_active_entry')}")
            if data.get('has_active_entry'):
                active_entry = data['active_entry']
                print(f"   active_entry ID: {active_entry.get('id')}")
                print(f"   Sala: {active_entry.get('room_name')}")
            else:
                print("   PROBLEMA: No se detecta entrada activa después de crearla")
        else:
            print(f"   ERROR: {response.text}")
    except Exception as e:
        print(f"   ERROR: {e}")
    
    # 5. Probar endpoint de salida específico
    print(f"\n5. PROBAR ENDPOINT DE SALIDA ESPECÍFICO")
    print(f"   Probando: PATCH /api/rooms/entry/{entry_id}/exit/")
    
    try:
        response = requests.patch(f"{base_url}/api/rooms/entry/{entry_id}/exit/", 
                                json={"notes": "Prueba de salida específica"}, headers=headers)
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.text}")
        
        if response.status_code == 200:
            print("   OK - Salida exitosa")
        elif response.status_code == 404:
            print("   PROBLEMA: Endpoint no encontrado (404)")
        else:
            print(f"   ERROR: {response.status_code}")
    except Exception as e:
        print(f"   ERROR: {e}")
    
    # 6. Probar endpoint alternativo de salida
    print(f"\n6. PROBAR ENDPOINT ALTERNATIVO DE SALIDA")
    print(f"   Probando: PATCH /api/rooms/my-active-entry/exit/")
    
    try:
        response = requests.patch(f"{base_url}/api/rooms/my-active-entry/exit/", 
                                json={"notes": "Prueba de salida alternativa"}, headers=headers)
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.text}")
        
        if response.status_code == 200:
            print("   OK - Salida alternativa exitosa")
        elif response.status_code == 400:
            print("   PROBLEMA: No hay entrada activa para salir")
        else:
            print(f"   ERROR: {response.status_code}")
    except Exception as e:
        print(f"   ERROR: {e}")
    
    # 7. Verificar estado final
    print(f"\n7. VERIFICAR ESTADO FINAL")
    try:
        response = requests.get(f"{base_url}/api/rooms/my-active-entry/", headers=headers)
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.text}")
    except Exception as e:
        print(f"   ERROR: {e}")
    
    print("\n" + "=" * 60)
    print("ANÁLISIS DE PROBLEMAS:")
    print("1. ¿Se crea la entrada correctamente?")
    print("2. ¿Se detecta como activa inmediatamente?")
    print("3. ¿Funciona el endpoint de salida específico?")
    print("4. ¿Funciona el endpoint alternativo de salida?")

def main():
    test_specific_issues()

if __name__ == "__main__":
    main()
