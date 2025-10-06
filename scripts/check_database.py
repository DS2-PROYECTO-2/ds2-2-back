#!/usr/bin/env python3
"""
Script para verificar el estado de la base de datos
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ds2_back.settings')
django.setup()

from rooms.models import RoomEntry
from users.models import User
from django.utils import timezone

def check_database():
    """Verificar el estado de la base de datos"""
    print("Verificando estado de la base de datos...")
    print("=" * 50)
    
    # 1. Verificar usuario admin
    try:
        admin_user = User.objects.get(username='admin')
        print(f"1. Usuario admin encontrado: {admin_user.username} (ID: {admin_user.id})")
    except User.DoesNotExist:
        print("1. Usuario admin no encontrado")
        return
    
    # 2. Verificar entradas del usuario admin
    entries = RoomEntry.objects.filter(user=admin_user).order_by('-created_at')
    print(f"\n2. Total de entradas del usuario admin: {entries.count()}")
    
    for i, entry in enumerate(entries[:5]):  # Mostrar solo las últimas 5
        print(f"   Entrada {i+1}:")
        print(f"     - ID: {entry.id}")
        print(f"     - Sala: {entry.room.name}")
        print(f"     - Hora entrada: {entry.entry_time}")
        print(f"     - Hora salida: {entry.exit_time}")
        print(f"     - Active: {entry.active}")
        print(f"     - is_active (property): {entry.is_active}")
        print()
    
    # 3. Verificar entradas activas
    active_entries = RoomEntry.objects.filter(
        user=admin_user,
        active=True,
        exit_time__isnull=True
    )
    print(f"3. Entradas activas (active=True, exit_time=None): {active_entries.count()}")
    
    for entry in active_entries:
        print(f"   - ID: {entry.id}, Sala: {entry.room.name}, Active: {entry.active}")
    
    # 4. Verificar entradas con exit_time=None
    entries_no_exit = RoomEntry.objects.filter(
        user=admin_user,
        exit_time__isnull=True
    )
    print(f"\n4. Entradas sin salida (exit_time=None): {entries_no_exit.count()}")
    
    for entry in entries_no_exit:
        print(f"   - ID: {entry.id}, Sala: {entry.room.name}, Active: {entry.active}")

def main():
    check_database()

if __name__ == "__main__":
    main()
