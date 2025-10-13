#!/usr/bin/env python3
"""
Script para verificar la configuracion de email
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ds2_back.settings')
django.setup()

from django.core.mail import send_mail
from django.conf import settings

def verify_email_config():
    """Verificar la configuracion de email"""
    print("Verificando configuracion de email...")
    print("=" * 50)
    
    print(f"EMAIL_BACKEND: {settings.EMAIL_BACKEND}")
    print(f"EMAIL_HOST: {settings.EMAIL_HOST}")
    print(f"EMAIL_PORT: {settings.EMAIL_PORT}")
    print(f"EMAIL_USE_TLS: {settings.EMAIL_USE_TLS}")
    print(f"EMAIL_HOST_USER: {settings.EMAIL_HOST_USER}")
    print(f"DEFAULT_FROM_EMAIL: {settings.DEFAULT_FROM_EMAIL}")
    
    print("\nProbando envio de email de prueba...")
    
    try:
        # Intentar enviar un email de prueba
        result = send_mail(
            subject='Prueba de Email - DS2 Sistema',
            message='Este es un email de prueba para verificar que la configuracion de email funciona correctamente.',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=['admin@ejemplo.com'],
            fail_silently=False
        )
        print(f"Resultado del envio: {result}")
        print("Email enviado exitosamente por SMTP")
        print("Revisa la bandeja de entrada de admin@ejemplo.com")
    except Exception as e:
        print(f"Error enviando email: {e}")
        print("Verifica las credenciales de Gmail")

def main():
    verify_email_config()

if __name__ == "__main__":
    main()
