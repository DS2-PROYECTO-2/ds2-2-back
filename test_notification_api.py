#!/usr/bin/env python
"""
Test script para verificar que la API de notificaciones de exceso de horas funciona correctamente
"""
import os
import django
import requests
import json

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ds2_back.settings')
django.setup()

from django.contrib.auth import get_user_model
from rest_framework.authtoken.models import Token

User = get_user_model()

def test_excessive_hours_api():
    """Test para verificar que la API de notificaciones de exceso funciona"""
    print("=== PROBANDO API DE NOTIFICACIONES DE EXCESO DE HORAS ===")
    
    try:
        # 1. Obtener token de administrador
        admin_user = User.objects.filter(role='admin', is_verified=True).first()
        if not admin_user:
            print("❌ No se encontró administrador verificado")
            return
        
        token, created = Token.objects.get_or_create(user=admin_user)
        print(f"✅ Usando admin: {admin_user.get_full_name()} ({admin_user.username})")
        print(f"✅ Token obtenido: {token.key[:10]}...")
        
        # 2. Probar endpoint de notificaciones de exceso de horas
        base_url = "http://127.0.0.1:8000"
        headers = {
            'Authorization': f'Token {token.key}',
            'Content-Type': 'application/json'
        }
        
        # Probar endpoint de notificaciones generales
        print("\n📡 Probando GET /api/notifications/notifications/")
        response = requests.get(f"{base_url}/api/notifications/notifications/", headers=headers)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Total notificaciones: {len(data)}")
            
            # Filtrar notificaciones de exceso de horas
            excessive_notifications = [n for n in data if n.get('notification_type') == 'excessive_hours']
            print(f"Notificaciones de exceso: {len(excessive_notifications)}")
            
            if excessive_notifications:
                print("\n📧 Ejemplo de notificación de exceso:")
                notif = excessive_notifications[0]
                print(f"   ID: {notif.get('id')}")
                print(f"   Título: {notif.get('title')}")
                print(f"   Para: {notif.get('recipient_name', 'N/A')}")
                print(f"   Fecha: {notif.get('created_at')}")
                print(f"   Leída: {notif.get('read', False)}")
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"Response: {response.text}")
        
        # 3. Probar endpoint específico de exceso de horas
        print("\n📡 Probando GET /api/notifications/notifications/excessive_hours/")
        response = requests.get(f"{base_url}/api/notifications/notifications/excessive_hours/", headers=headers)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Notificaciones de exceso específicas: {len(data)}")
            
            if data:
                print("\n📧 Ejemplo con información detallada:")
                notif = data[0]
                print(f"   ID: {notif.get('id')}")
                print(f"   Título: {notif.get('title')}")
                print(f"   Monitor: {notif.get('monitor_name', 'N/A')} ({notif.get('monitor_username', 'N/A')})")
                print(f"   Sala: {notif.get('room_name', 'N/A')}")
                print(f"   Duración: {notif.get('duration_hours', 'N/A')} horas")
                print(f"   Exceso: {notif.get('excess_hours', 'N/A')} horas")
                print(f"   Entrada relacionada: {notif.get('related_object_id', 'N/A')}")
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"Response: {response.text}")
        
        # 4. Probar endpoint de resumen
        print("\n📡 Probando GET /api/notifications/notifications/excessive_hours_summary/")
        response = requests.get(f"{base_url}/api/notifications/notifications/excessive_hours_summary/", headers=headers)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Resumen de exceso de horas:")
            print(f"   Total notificaciones: {data.get('total_notifications', 0)}")
            print(f"   Monitores únicos: {data.get('total_monitors', 0)}")
            print(f"   No leídas: {data.get('unread_notifications', 0)}")
            print(f"   Última notificación: {data.get('latest_notification_date', 'N/A')}")
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"Response: {response.text}")
        
        print(f"\n✅ PRUEBA DE API COMPLETADA")
        
    except Exception as e:
        print(f"❌ Error en la prueba: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_excessive_hours_api()