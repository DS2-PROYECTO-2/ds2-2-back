#!/usr/bin/env python3
"""
Script para verificar la estructura de la tabla rooms_roomentry
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ds2_back.settings')
django.setup()

from rooms.models import RoomEntry
from django.db import connection

def check_table_structure():
    """Verificar la estructura de la tabla"""
    print("Estructura de la tabla rooms_roomentry:")
    print("=" * 50)
    
    # 1. Obtener información de la tabla usando SQL directo
    with connection.cursor() as cursor:
        cursor.execute("PRAGMA table_info(rooms_roomentry)")
        columns = cursor.fetchall()
        
        print("Columnas de la tabla:")
        for col in columns:
            cid, name, type_name, notnull, default_value, pk = col
            print(f"  - {name}: {type_name} {'NOT NULL' if notnull else 'NULL'} {'PRIMARY KEY' if pk else ''}")
    
    print("\n" + "=" * 50)
    
    # 2. Mostrar algunos registros de ejemplo
    print("Registros en la tabla:")
    entries = RoomEntry.objects.all().order_by('-created_at')[:5]
    
    for entry in entries:
        print(f"\nID: {entry.id}")
        print(f"  Usuario: {entry.user.username} (ID: {entry.user.id})")
        print(f"  Sala: {entry.room.name} (ID: {entry.room.id})")
        print(f"  Hora entrada: {entry.entry_time}")
        print(f"  Hora salida: {entry.exit_time}")
        print(f"  Active: {entry.active}")
        print(f"  Notas: {entry.notes}")
        print(f"  Creado: {entry.created_at}")
        print(f"  Actualizado: {entry.updated_at}")

def main():
    check_table_structure()

if __name__ == "__main__":
    main()
