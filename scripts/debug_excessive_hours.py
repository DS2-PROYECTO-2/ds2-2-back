#!/usr/bin/env python3
"""
Script para debuggear el sistema de exceso de horas
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
from rooms.services import RoomEntryBusinessLogic
from django.utils import timezone

def debug_excessive_hours():
    """Debuggear el sistema de exceso de horas"""
    print("Debuggeando sistema de exceso de horas...")
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
    except Exception as e:
        print(f"Error creando entrada: {e}")
        return
    
    # 3. Calcular duración manualmente
    print("\n3. CALCULANDO DURACION MANUALMENTE")
    try:
        duration_info = RoomEntryBusinessLogic.calculate_session_duration(entry)
        total_hours = duration_info.get('total_duration_hours', 0)
        print(f"Duracion calculada: {total_hours} horas")
        print(f"Excede 8 horas: {total_hours > 8}")
    except Exception as e:
        print(f"Error calculando duracion: {e}")
        return
    
    # 4. Verificar administradores
    print("\n4. VERIFICANDO ADMINISTRADORES")
    try:
        admins = User.objects.filter(role='admin', is_active=True)
        print(f"Administradores encontrados: {admins.count()}")
        for admin in admins:
            print(f"  - {admin.username} ({admin.email})")
    except Exception as e:
        print(f"Error obteniendo administradores: {e}")
        return
    
    # 5. Probar notificación paso a paso
    print("\n5. PROBANDO NOTIFICACION PASO A PASO")
    try:
        if total_hours > 8:
            print("Condicion cumplida: total_hours > 8")
            
            excess_hours = round(total_hours - 8, 2)
            print(f"Horas de exceso: {excess_hours}")
            
            for admin in admins:
                print(f"Procesando admin: {admin.username}")
                
                # Crear notificación
                notification = NotificationService.create_notification(
                    user=admin,
                    notification_type='excessive_hours',
                    title=f"Exceso de Horas - {entry.user.get_full_name()}",
                    message=f"El monitor ha excedido las 8 horas: {total_hours:.1f}h",
                    related_object_id=entry.id
                )
                print(f"  Notificacion creada: {notification is not None}")
                
                # Enviar email
                try:
                    NotificationService.send_excessive_hours_email(admin, entry, total_hours, excess_hours)
                    print(f"  Email enviado a: {admin.email}")
                except Exception as e:
                    print(f"  Error enviando email: {e}")
            
            print("Proceso completado exitosamente")
        else:
            print("Condicion NO cumplida: total_hours <= 8")
    except Exception as e:
        print(f"Error en proceso: {e}")
        import traceback
        traceback.print_exc()

def main():
    debug_excessive_hours()

if __name__ == "__main__":
    main()
