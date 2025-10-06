#!/usr/bin/env python3
"""
Script para probar la configuración de email
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ds2_back.settings')
django.setup()

from django.core.mail import send_mail
from django.conf import settings

def test_email_config():
    """Probar la configuración de email"""
    print("Probando configuración de email...")
    print("=" * 50)
    
    print(f"EMAIL_BACKEND: {settings.EMAIL_BACKEND}")
    print(f"EMAIL_HOST: {settings.EMAIL_HOST}")
    print(f"EMAIL_PORT: {settings.EMAIL_PORT}")
    print(f"EMAIL_USE_TLS: {settings.EMAIL_USE_TLS}")
    print(f"EMAIL_HOST_USER: {settings.EMAIL_HOST_USER}")
    print(f"DEFAULT_FROM_EMAIL: {settings.DEFAULT_FROM_EMAIL}")
    
    print("\nProbando envío de email...")
    
    try:
        # Intentar enviar un email de prueba
        result = send_mail(
            subject='Prueba de Email - DS2',
            message='Este es un email de prueba para verificar la configuración.',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=['test@example.com'],
            fail_silently=False
        )
        print(f"Resultado del envío: {result}")
        print("Email enviado exitosamente")
    except Exception as e:
        print(f"Error enviando email: {e}")

def main():
    test_email_config()

if __name__ == "__main__":
    main()
