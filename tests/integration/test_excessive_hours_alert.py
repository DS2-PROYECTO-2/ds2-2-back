#!/usr/bin/env python3
"""
Script para probar el sistema de alertas por exceso de horas
"""

import os
import sys
import django
from datetime import datetime, timedelta

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ds2_back.settings')
django.setup()

from rooms.models import RoomEntry, Room
from users.models import User
from notifications.services import NotificationService
from django.utils import timezone

def test_excessive_hours_alert():
    """Probar el sistema de alertas por exceso de horas"""
    print("Probando sistema de alertas por exceso de horas...")
    print("=" * 60)
    
    # 1. Obtener usuario y sala
    try:
        user = User.objects.get(username='admin')
        room = Room.objects.first()
        print(f"Usuario: {user.username} (ID: {user.id})")
        print(f"Sala: {room.name} (ID: {room.id})")
    except Exception as e:
        print(f"Error obteniendo datos: {e}")
        return
    
    # 2. Crear entrada simulando 8+ horas
    print("\n2. CREANDO ENTRADA CON 8+ HORAS")
    try:
        # Crear entrada con hora de entrada hace 9 horas
        entry_time = timezone.now() - timedelta(hours=9)
        
        entry = RoomEntry.objects.create(
            user=user,
            room=room,
            notes="Prueba de exceso de horas",
            entry_time=entry_time
        )
        print(f"Entrada creada: ID {entry.id}")
        print(f"Hora de entrada: {entry.entry_time}")
        print(f"Hora actual: {timezone.now()}")
        print(f"Diferencia: {(timezone.now() - entry.entry_time).total_seconds() / 3600:.1f} horas")
    except Exception as e:
        print(f"Error creando entrada: {e}")
        return
    
    # 3. Probar notificación de exceso de horas
    print("\n3. PROBANDO NOTIFICACION DE EXCESO DE HORAS")
    try:
        result = NotificationService.notify_excessive_hours(entry)
        print(f"Resultado: {result}")
        
        if result:
            print("✅ NOTIFICACION Y EMAIL ENVIADOS EXITOSAMENTE")
            print("Revisa la bandeja de entrada de los administradores")
        else:
            print("❌ ERROR EN NOTIFICACION")
    except Exception as e:
        print(f"Error en notificacion: {e}")
        import traceback
        traceback.print_exc()
    
    # 4. Verificar notificaciones creadas
    print("\n4. VERIFICANDO NOTIFICACIONES CREADAS")
    try:
        from notifications.models import Notification
        notifications = Notification.objects.filter(
            notification_type='excessive_hours',
            related_object_id=entry.id
        )
        print(f"Notificaciones creadas: {notifications.count()}")
        
        for notif in notifications:
            print(f"  - Para: {notif.user.username}")
            print(f"  - Titulo: {notif.title}")
            print(f"  - Creada: {notif.created_at}")
    except Exception as e:
        print(f"Error verificando notificaciones: {e}")
    
    print("\n" + "=" * 60)
    print("RESUMEN:")
    print("1. Se creo una entrada simulando 9 horas de duracion")
    print("2. Se envio notificacion a administradores")
    print("3. Se envio email de alerta con card profesional")
    print("4. Revisa la bandeja de entrada de los administradores")

def main():
    test_excessive_hours_alert()

if __name__ == "__main__":
    main()
