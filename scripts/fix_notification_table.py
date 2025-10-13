#!/usr/bin/env python3
"""
Script para arreglar la tabla de notificaciones
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ds2_back.settings')
django.setup()

from django.db import connection

def fix_notification_table():
    """Arreglar la tabla de notificaciones"""
    print("Arreglando tabla de notificaciones...")
    print("=" * 50)
    
    with connection.cursor() as cursor:
        # 1. Verificar si existe la columna is_read
        cursor.execute("PRAGMA table_info(notifications_notification);")
        columns = cursor.fetchall()
        column_names = [col[1] for col in columns]
        
        if 'is_read' in column_names:
            print("Columna is_read existe, eliminándola...")
            # Eliminar la columna is_read duplicada
            cursor.execute("ALTER TABLE notifications_notification DROP COLUMN is_read;")
            print("Columna is_read eliminada")
        
        if 'monitor_id' in column_names:
            print("Columna monitor_id existe, eliminándola...")
            cursor.execute("ALTER TABLE notifications_notification DROP COLUMN monitor_id;")
            print("Columna monitor_id eliminada")
            
        if 'monitor_name' in column_names:
            print("Columna monitor_name existe, eliminándola...")
            cursor.execute("ALTER TABLE notifications_notification DROP COLUMN monitor_name;")
            print("Columna monitor_name eliminada")
    
    print("\nTabla arreglada. Verificando estructura...")
    
    # Verificar estructura final
    with connection.cursor() as cursor:
        cursor.execute("PRAGMA table_info(notifications_notification);")
        columns = cursor.fetchall()
        print("\nEstructura final:")
        for col in columns:
            print(f"  - {col[1]}: {col[2]} {'NOT NULL' if col[3] else 'NULL'}")

def main():
    fix_notification_table()

if __name__ == "__main__":
    main()
