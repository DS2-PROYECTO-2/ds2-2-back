#!/usr/bin/env python
"""
Test interno usando Django Test Client para verificar API sin servidor externo
"""
import os
import django
import json

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ds2_back.settings')
django.setup()

from django.test import Client
from django.contrib.auth import get_user_model
from rest_framework.authtoken.models import Token

User = get_user_model()

def test_notification_endpoints():
    """Test directo usando Django Test Client"""
    print("=== PROBANDO ENDPOINTS DE NOTIFICACIONES (Test Client) ===")
    
    try:
        # 1. Obtener token de administrador
        admin_user = User.objects.filter(role='admin', is_verified=True).first()
        if not admin_user:
            print("❌ No se encontró administrador verificado")
            return
        
        token, created = Token.objects.get_or_create(user=admin_user)
        print(f"✅ Usando admin: {admin_user.get_full_name()} ({admin_user.username})")
        
        # 2. Crear cliente de prueba
        client = Client()
        headers = {'HTTP_AUTHORIZATION': f'Token {token.key}'}
        
        # 3. Probar endpoint general de notificaciones
        print("\n📡 Probando GET /api/notifications/notifications/")
        response = client.get('/api/notifications/notifications/', **headers)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Tipo de datos: {type(data)}")
            print(f"Claves disponibles: {list(data.keys()) if isinstance(data, dict) else 'No es dict'}")
            
            # Manejar respuesta paginada o directa
            if isinstance(data, dict) and 'results' in data:
                notifications = data['results']
                print(f"Total notificaciones (paginadas): {len(notifications)}")
                print(f"Count total: {data.get('count', 'N/A')}")
            elif isinstance(data, list):
                notifications = data
                print(f"Total notificaciones: {len(notifications)}")
            else:
                notifications = []
                print(f"Formato inesperado de datos: {data}")
            
            # Filtrar notificaciones de exceso de horas
            excessive_notifications = [n for n in notifications if isinstance(n, dict) and n.get('notification_type') == 'excessive_hours']
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
            if hasattr(response, 'content'):
                print(f"Response: {response.content.decode()}")
        
        # 4. Probar endpoint específico de exceso de horas
        print("\n📡 Probando GET /api/notifications/notifications/excessive_hours/")
        response = client.get('/api/notifications/notifications/excessive_hours/', **headers)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            
            # Manejar respuesta paginada, directa o personalizada
            if isinstance(data, dict) and 'notifications' in data:
                notifications = data['notifications']
                print(f"Notificaciones de exceso específicas: {data.get('count', len(notifications))}")
            elif isinstance(data, dict) and 'results' in data:
                notifications = data['results']
                print(f"Notificaciones de exceso específicas: {len(notifications)}")
            elif isinstance(data, list):
                notifications = data
                print(f"Notificaciones de exceso específicas: {len(notifications)}")
            else:
                notifications = []
                print(f"Formato inesperado: {data}")
            
            if notifications:
                print("\n📧 Ejemplo con información detallada:")
                notif = notifications[0]
                print(f"   ID: {notif.get('id')}")
                print(f"   Título: {notif.get('title')}")
                print(f"   Monitor: {notif.get('monitor_name', 'N/A')} ({notif.get('monitor_username', 'N/A')})")
                print(f"   Sala: {notif.get('room_name', 'N/A')}")
                print(f"   Duración: {notif.get('duration_hours', 'N/A')} horas")
                print(f"   Exceso: {notif.get('excess_hours', 'N/A')} horas")
                print(f"   Entrada relacionada: {notif.get('related_object_id', 'N/A')}")
        else:
            print(f"❌ Error: {response.status_code}")
            if hasattr(response, 'content'):
                print(f"Response: {response.content.decode()}")
        
        # 5. Probar endpoint de resumen
        print("\n📡 Probando GET /api/notifications/notifications/excessive_hours_summary/")
        response = client.get('/api/notifications/notifications/excessive_hours_summary/', **headers)
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
            if hasattr(response, 'content'):
                print(f"Response: {response.content.decode()}")
        
        print(f"\n✅ PRUEBA DE ENDPOINTS COMPLETADA EXITOSAMENTE")
        
    except Exception as e:
        print(f"❌ Error en la prueba: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_notification_endpoints()