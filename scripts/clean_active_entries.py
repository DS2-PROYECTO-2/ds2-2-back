#!/usr/bin/env python3
"""
Script para limpiar todas las entradas activas
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ds2_back.settings')
django.setup()

from rooms.models import RoomEntry
from django.utils import timezone

def clean_active_entries():
    """Limpiar todas las entradas activas"""
    print("Limpiando entradas activas...")
    print("=" * 40)
    
    # 1. Encontrar todas las entradas activas
    active_entries = RoomEntry.objects.filter(
        active=True,
        exit_time__isnull=True
    )
    
    print(f"Entradas activas encontradas: {active_entries.count()}")
    
    # 2. Mostrar detalles
    for entry in active_entries:
        print(f"  - ID: {entry.id}, Usuario: {entry.user.username}, Sala: {entry.room.name}")
        print(f"    Entrada: {entry.entry_time}")
        print(f"    Activa: {entry.active}")
    
    # 3. Cerrar todas las entradas activas
    if active_entries.exists():
        print("\nCerrando todas las entradas activas...")
        for entry in active_entries:
            entry.exit_time = timezone.now()
            entry.active = False
            entry.notes = f"{entry.notes or ''} - Cerrada automaticamente para limpieza"
            entry.save()
            print(f"  - Entrada {entry.id} cerrada")
        
        print("Todas las entradas activas han sido cerradas")
    else:
        print("No hay entradas activas para cerrar")
    
    # 4. Verificar resultado
    remaining_active = RoomEntry.objects.filter(
        active=True,
        exit_time__isnull=True
    ).count()
    
    print(f"\nEntradas activas restantes: {remaining_active}")

def main():
    clean_active_entries()

if __name__ == "__main__":
    main()
