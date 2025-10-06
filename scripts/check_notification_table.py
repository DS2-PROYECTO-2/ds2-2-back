#!/usr/bin/env python3
"""
Script para verificar la estructura de la tabla de notificaciones
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ds2_back.settings')
django.setup()

from django.db import connection
from notifications.models import Notification

def check_notification_table():
    """Verificar la estructura de la tabla de notificaciones"""
    print("Estructura de la tabla notifications_notification:")
    print("=" * 60)
    
    with connection.cursor() as cursor:
        # Obtener información de las columnas
        cursor.execute("PRAGMA table_info(notifications_notification);")
        columns = cursor.fetchall()
        print("Columnas de la tabla:")
        for col in columns:
            # col[1] es el nombre de la columna, col[2] es el tipo, col[3] es NOT NULL, col[5] es default value
            print(f"  - {col[1]}: {col[2]} {'NOT NULL' if col[3] else 'NULL'} {'PRIMARY KEY' if col[5] == '1' else ''}")
            if col[5]:  # Si hay valor por defecto
                print(f"    Default: {col[5]}")
    
    print("\n" + "=" * 60)
    print("Verificando modelo Django:")
    
    # Verificar campos del modelo
    for field in Notification._meta.fields:
        print(f"  - {field.name}: {field.__class__.__name__}")
        if hasattr(field, 'default'):
            print(f"    Default: {field.default}")
        if hasattr(field, 'null'):
            print(f"    Null: {field.null}")
        if hasattr(field, 'blank'):
            print(f"    Blank: {field.blank}")

def main():
    check_notification_table()

if __name__ == "__main__":
    main()
