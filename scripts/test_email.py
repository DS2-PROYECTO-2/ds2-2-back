#!/usr/bin/env python
"""
Script para probar la configuración de email
"""
import os
import sys
import django

# Configurar Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ds2_back.settings')
django.setup()

from django.core.mail import send_mail
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

def test_email_configuration():
    """Probar la configuración de email"""
    print("🔍 Verificando configuración de email...")
    
    # Verificar variables de entorno
    print(f"EMAIL_BACKEND: {settings.EMAIL_BACKEND}")
    print(f"EMAIL_HOST: {settings.EMAIL_HOST}")
    print(f"EMAIL_PORT: {settings.EMAIL_PORT}")
    print(f"EMAIL_USE_TLS: {settings.EMAIL_USE_TLS}")
    print(f"EMAIL_HOST_USER: {settings.EMAIL_HOST_USER}")
    print(f"DEFAULT_FROM_EMAIL: {settings.DEFAULT_FROM_EMAIL}")
    
    # Probar envío de email
    try:
        send_mail(
            subject='[DS2] Prueba de configuración de email',
            message='Este es un email de prueba para verificar que la configuración funciona correctamente.',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=['sado56hdgm@gmail.com'],
            fail_silently=False,
        )
        print("✅ Email enviado exitosamente!")
        return True
    except Exception as e:
        print(f"❌ Error enviando email: {e}")
        return False

if __name__ == '__main__':
    test_email_configuration()
