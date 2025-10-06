#!/usr/bin/env python3
"""
Script para ver qué emails existen en la base de datos
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ds2_back.settings')
django.setup()

from users.models import User

def check_emails():
    """Ver emails existentes en la base de datos"""
    print("Emails existentes en la base de datos:")
    print("=" * 50)
    
    users = User.objects.all()
    print(f"Total de usuarios: {users.count()}")
    
    for user in users:
        print(f"  - {user.username}: {user.email} (Activo: {user.is_active})")

def main():
    check_emails()

if __name__ == "__main__":
    main()
