#!/usr/bin/env python3
"""
Script para probar la actualización directa en la base de datos
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ds2_back.settings')
django.setup()

from rooms.models import RoomEntry
from django.utils import timezone

def test_direct_exit():
    """Probar actualización directa en la base de datos"""
    print("Probando actualización directa en la base de datos...")
    print("=" * 50)
    
    try:
        # 1. Obtener la entrada
        entry = RoomEntry.objects.get(id=44)
        print(f"1. Entrada encontrada: {entry.id}")
        print(f"   -> Active: {entry.active}")
        print(f"   -> Exit time: {entry.exit_time}")
        
        # 2. Actualizar directamente
        print("\n2. Actualizando directamente...")
        entry.exit_time = timezone.now()
        entry.active = False
        entry.notes = "Salida directa"
        entry.save()
        
        print(f"   -> Active: {entry.active}")
        print(f"   -> Exit time: {entry.exit_time}")
        
        # 3. Verificar en base de datos
        print("\n3. Verificando en base de datos...")
        updated_entry = RoomEntry.objects.get(id=44)
        print(f"   -> Active: {updated_entry.active}")
        print(f"   -> Exit time: {updated_entry.exit_time}")
        
        return True
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    test_direct_exit()

if __name__ == "__main__":
    main()
