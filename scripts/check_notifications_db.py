#!/usr/bin/env python3
"""
Script para ver las notificaciones directamente de la base de datos
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ds2_back.settings')
django.setup()

from notifications.models import Notification
from users.models import User

def check_notifications_db():
    """Ver notificaciones directamente de la base de datos"""
    print("Notificaciones del admin desde la base de datos:")
    print("=" * 60)
    
    # 1. Obtener usuario admin
    try:
        admin_user = User.objects.get(username='admin')
        print(f"Admin encontrado: {admin_user.username} (ID: {admin_user.id})")
    except User.DoesNotExist:
        print("Admin no encontrado")
        return
    
    # 2. Obtener notificaciones del admin
    notifications = Notification.objects.filter(user=admin_user).order_by('-created_at')
    print(f"\nTotal de notificaciones: {notifications.count()}")
    
    # 3. Mostrar las últimas 5 notificaciones
    print("\nUltimas 5 notificaciones:")
    for i, notif in enumerate(notifications[:5]):
        print(f"\n{i+1}. ID: {notif.id}")
        print(f"   Tipo: {notif.notification_type}")
        print(f"   Titulo: {notif.title}")
        print(f"   Leida: {notif.read}")
        print(f"   Creada: {notif.created_at}")
        print(f"   Mensaje: {notif.message[:100]}...")
    
    # 4. Contar por tipo
    print("\nConteo por tipo de notificacion:")
    type_counts = {}
    for notif in notifications:
        type_name = notif.notification_type
        type_counts[type_name] = type_counts.get(type_name, 0) + 1
    
    for type_name, count in type_counts.items():
        print(f"   {type_name}: {count}")
    
    # 5. Contar no leídas
    unread_count = notifications.filter(read=False).count()
    print(f"\nNo leidas: {unread_count}")
    
    # 6. Mostrar tipos de notificaciones disponibles
    print("\nTipos de notificaciones disponibles:")
    for choice in Notification.TYPE_CHOICES:
        print(f"   {choice[0]}: {choice[1]}")

def main():
    check_notifications_db()

if __name__ == "__main__":
    main()
