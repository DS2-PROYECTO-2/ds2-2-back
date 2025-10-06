#!/usr/bin/env python3
"""
Script para ver las notificaciones de forma segura
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ds2_back.settings')
django.setup()

from notifications.models import Notification
from users.models import User

def safe_print(text):
    """Imprimir texto de forma segura, manejando emojis"""
    try:
        print(text)
    except UnicodeEncodeError:
        # Reemplazar emojis problemáticos
        safe_text = text.encode('ascii', 'ignore').decode('ascii')
        print(safe_text)

def check_notifications_safe():
    """Ver notificaciones de forma segura"""
    print("Notificaciones del admin:")
    print("=" * 50)
    
    # 1. Obtener usuario admin
    try:
        admin_user = User.objects.get(username='admin')
        print(f"Admin: {admin_user.username} (ID: {admin_user.id})")
    except User.DoesNotExist:
        print("Admin no encontrado")
        return
    
    # 2. Obtener notificaciones del admin
    notifications = Notification.objects.filter(user=admin_user).order_by('-created_at')
    print(f"Total: {notifications.count()}")
    
    # 3. Mostrar las últimas 3 notificaciones
    print("\nUltimas 3 notificaciones:")
    for i, notif in enumerate(notifications[:3]):
        print(f"\n{i+1}. ID: {notif.id}")
        print(f"   Tipo: {notif.notification_type}")
        safe_print(f"   Titulo: {notif.title}")
        print(f"   Leida: {notif.read}")
        print(f"   Creada: {notif.created_at}")
        # Mostrar solo los primeros 50 caracteres del mensaje
        message_preview = str(notif.message)[:50] + "..." if len(str(notif.message)) > 50 else str(notif.message)
        safe_print(f"   Mensaje: {message_preview}")
    
    # 4. Contar por tipo
    print("\nConteo por tipo:")
    type_counts = {}
    for notif in notifications:
        type_name = notif.notification_type
        type_counts[type_name] = type_counts.get(type_name, 0) + 1
    
    for type_name, count in type_counts.items():
        print(f"   {type_name}: {count}")
    
    # 5. Contar no leídas
    unread_count = notifications.filter(read=False).count()
    print(f"\nNo leidas: {unread_count}")
    
    # 6. Mostrar tipos disponibles
    print("\nTipos de notificaciones disponibles:")
    for choice in Notification.TYPE_CHOICES:
        print(f"   {choice[0]}: {choice[1]}")

def main():
    check_notifications_safe()

if __name__ == "__main__":
    main()
