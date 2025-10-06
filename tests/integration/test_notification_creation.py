#!/usr/bin/env python3
"""
Script para probar la creación de notificaciones paso a paso
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ds2_back.settings')
django.setup()

from rooms.models import RoomEntry, Room
from users.models import User
from notifications.models import Notification
from notifications.services import NotificationService
from django.utils import timezone

def test_notification_creation():
    """Probar la creación de notificaciones paso a paso"""
    print("Probando creación de notificaciones...")
    print("=" * 50)
    
    # 1. Obtener usuario y sala
    try:
        user = User.objects.get(username='admin')
        room = Room.objects.first()
        print(f"Usuario: {user.username} (ID: {user.id})")
        print(f"Sala: {room.name} (ID: {room.id})")
    except Exception as e:
        print(f"Error obteniendo datos: {e}")
        return
    
    # 2. Contar notificaciones antes
    notifications_before = Notification.objects.filter(user=user).count()
    print(f"\nNotificaciones antes: {notifications_before}")
    
    # 3. Crear entrada manualmente
    print("\n3. Creando entrada manualmente...")
    try:
        entry = RoomEntry.objects.create(
            user=user,
            room=room,
            notes="Prueba de notificaciones"
        )
        print(f"Entrada creada: ID {entry.id}")
    except Exception as e:
        print(f"Error creando entrada: {e}")
        return
    
    # 4. Probar servicio de notificaciones directamente
    print("\n4. Probando NotificationService.notify_room_entry...")
    try:
        result = NotificationService.notify_room_entry(entry, is_entry=True)
        print(f"Resultado: {result}")
    except Exception as e:
        print(f"Error en NotificationService: {e}")
        import traceback
        traceback.print_exc()
    
    # 5. Contar notificaciones después
    notifications_after = Notification.objects.filter(user=user).count()
    print(f"\nNotificaciones después: {notifications_after}")
    print(f"Diferencia: {notifications_after - notifications_before}")
    
    # 6. Verificar si se crearon notificaciones
    if notifications_after > notifications_before:
        print("\n✅ Notificaciones creadas exitosamente")
        new_notifications = Notification.objects.filter(user=user).order_by('-created_at')[:3]
        for notif in new_notifications:
            print(f"  - {notif.title} ({notif.notification_type})")
    else:
        print("\n❌ No se crearon notificaciones")
    
    # 7. Probar con salida
    print("\n7. Probando notificación de salida...")
    try:
        entry.exit_time = timezone.now()
        entry.active = False
        entry.save()
        print("Entrada actualizada con salida")
        
        result = NotificationService.notify_room_entry(entry, is_entry=False)
        print(f"Resultado salida: {result}")
    except Exception as e:
        print(f"Error en salida: {e}")
    
    # 8. Contar notificaciones final
    notifications_final = Notification.objects.filter(user=user).count()
    print(f"\nNotificaciones finales: {notifications_final}")
    print(f"Total nuevas: {notifications_final - notifications_before}")

def main():
    test_notification_creation()

if __name__ == "__main__":
    main()
