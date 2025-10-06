#!/usr/bin/env python3
"""
Script para debuggear el calculo de duracion
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
from rooms.services import RoomEntryBusinessLogic
from django.utils import timezone

def debug_duration_calculation():
    """Debuggear el calculo de duracion"""
    print("Debuggeando calculo de duracion...")
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
        print(f"Diferencia manual: {(timezone.now() - entry.entry_time).total_seconds() / 3600:.1f} horas")
    except Exception as e:
        print(f"Error creando entrada: {e}")
        return
    
    # 3. Debuggear calculate_session_duration
    print("\n3. DEBUGGEANDO calculate_session_duration")
    try:
        print(f"entry.exit_time: {entry.exit_time}")
        print(f"entry.entry_time: {entry.entry_time}")
        print(f"timezone.now(): {timezone.now()}")
        
        if not entry.exit_time:
            print("Entrada activa - calculando duracion parcial")
            current_duration = timezone.now() - entry.entry_time
            print(f"current_duration: {current_duration}")
            print(f"current_duration.total_seconds(): {current_duration.total_seconds()}")
            print(f"current_duration.total_seconds() / 3600: {current_duration.total_seconds() / 3600}")
            print(f"round(current_duration.total_seconds() / 3600, 2): {round(current_duration.total_seconds() / 3600, 2)}")
        
        duration_info = RoomEntryBusinessLogic.calculate_session_duration(entry)
        print(f"duration_info: {duration_info}")
        
        total_hours = duration_info.get('total_duration_hours', 0) or duration_info.get('current_duration_hours', 0)
        print(f"total_hours: {total_hours}")
        
    except Exception as e:
        print(f"Error calculando duracion: {e}")
        import traceback
        traceback.print_exc()

def main():
    debug_duration_calculation()

if __name__ == "__main__":
    main()
