#!/usr/bin/env python3
"""
Script para probar la creación directa de entradas
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ds2_back.settings')
django.setup()

from rooms.models import RoomEntry, Room
from users.models import User
from django.utils import timezone

def test_direct_entry():
    """Probar creación directa de entrada"""
    print("Probando creación directa de entrada...")
    print("=" * 40)
    
    try:
        # 1. Obtener usuario y sala
        user = User.objects.get(username='admin')
        room = Room.objects.first()
        
        print(f"1. Usuario: {user.username} (ID: {user.id})")
        print(f"2. Sala: {room.name} (ID: {room.id})")
        
        # 2. Crear entrada directamente
        print("\n3. Creando entrada directamente...")
        entry = RoomEntry.objects.create(
            user=user,
            room=room,
            notes="Prueba directa"
        )
        
        print(f"   -> Entrada creada con ID: {entry.id}")
        print(f"   -> Active: {entry.active}")
        print(f"   -> Entry time: {entry.entry_time}")
        
        # 3. Verificar que se guardó
        print("\n4. Verificando en base de datos...")
        saved_entry = RoomEntry.objects.get(id=entry.id)
        print(f"   -> Entrada encontrada: {saved_entry.id}")
        print(f"   -> Active: {saved_entry.active}")
        
        # 4. Verificar entradas del usuario
        user_entries = RoomEntry.objects.filter(user=user)
        print(f"\n5. Total entradas del usuario: {user_entries.count()}")
        
        return True
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    test_direct_entry()

if __name__ == "__main__":
    main()
