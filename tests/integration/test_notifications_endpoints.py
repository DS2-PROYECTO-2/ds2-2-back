#!/usr/bin/env python3
"""
Script para probar los endpoints de notificaciones
"""

import requests
import json

def test_notification_endpoints():
    """Probar endpoints de notificaciones"""
    base_url = "http://localhost:8000"
    
    print("Probando endpoints de notificaciones...")
    print("=" * 50)
    
    # Endpoints a probar
    endpoints = [
        "/api/notifications/",
        "/api/notifications/unread/",
        "/api/notifications/unread-count/",
        "/api/notifications/summary/",
        "/api/notifications/excessive-hours/",
        "/api/notifications/excessive-hours-summary/",
    ]
    
    for endpoint in endpoints:
        url = f"{base_url}{endpoint}"
        try:
            print(f"\nProbando: {url}")
            response = requests.get(url, timeout=5)
            print(f"Status: {response.status_code}")
            
            if response.status_code == 401:
                print("  -> Requiere autenticacion (normal)")
            elif response.status_code == 200:
                print("  -> OK")
                try:
                    data = response.json()
                    print(f"  -> Response: {json.dumps(data, indent=2, ensure_ascii=False)[:200]}...")
                except:
                    print(f"  -> Response: {response.text[:200]}...")
            elif response.status_code == 404:
                print("  -> NOT FOUND - Este endpoint no existe")
            else:
                print(f"  -> Status inesperado: {response.status_code}")
                
        except requests.exceptions.ConnectionError:
            print(f"  -> ERROR: No se puede conectar")
        except Exception as e:
            print(f"  -> ERROR: {str(e)}")
    
    print("\n" + "=" * 50)
    print("URLs CORRECTAS para el frontend:")
    print("-" * 30)
    print("GET  /api/notifications/                    # Lista todas las notificaciones")
    print("GET  /api/notifications/unread/             # Solo no leídas")
    print("GET  /api/notifications/unread-count/       # Contador de no leídas")
    print("GET  /api/notifications/summary/            # Resumen de notificaciones")
    print("PATCH /api/notifications/{id}/mark-read/     # Marcar como leída")
    print("PATCH /api/notifications/mark-all-read/     # Marcar todas como leídas")

def main():
    test_notification_endpoints()

if __name__ == "__main__":
    main()
