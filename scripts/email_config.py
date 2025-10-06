"""
Configuración de email para desarrollo y producción
"""

import os
from django.core.mail.backends.console import EmailBackend as ConsoleEmailBackend

class DevelopmentEmailBackend(ConsoleEmailBackend):
    """
    Backend de email para desarrollo que muestra los emails en consola
    """
    def send_messages(self, email_messages):
        """
        Enviar mensajes y mostrarlos en consola
        """
        for message in email_messages:
            print("\n" + "="*60)
            print("📧 EMAIL ENVIADO (MODO DESARROLLO)")
            print("="*60)
            print(f"Para: {', '.join(message.to)}")
            print(f"De: {message.from_email}")
            print(f"Asunto: {message.subject}")
            print("-"*60)
            print("Contenido:")
            print(message.body)
            if hasattr(message, 'alternatives') and message.alternatives:
                print("\nContenido HTML:")
                for content, mimetype in message.alternatives:
                    if mimetype == 'text/html':
                        print(content)
            print("="*60)
            print()
        
        return super().send_messages(email_messages)

def get_email_config():
    """
    Obtener configuración de email según el entorno
    """
    DEBUG = os.getenv('DEBUG', 'True').lower() == 'true'
    
    if DEBUG:
        return {
            'EMAIL_BACKEND': 'email_config.DevelopmentEmailBackend',
            'EMAIL_HOST': 'smtp.gmail.com',
            'EMAIL_PORT': 587,
            'EMAIL_USE_TLS': True,
            'EMAIL_HOST_USER': os.getenv('EMAIL_HOST_USER', 'tu-email@gmail.com'),
            'EMAIL_HOST_PASSWORD': os.getenv('EMAIL_HOST_PASSWORD', 'tu-password-app'),
            'DEFAULT_FROM_EMAIL': os.getenv('DEFAULT_FROM_EMAIL', 'tu-email@gmail.com'),
        }
    else:
        return {
            'EMAIL_BACKEND': 'django.core.mail.backends.smtp.EmailBackend',
            'EMAIL_HOST': os.getenv('EMAIL_HOST', 'smtp.gmail.com'),
            'EMAIL_PORT': int(os.getenv('EMAIL_PORT', '587')),
            'EMAIL_USE_TLS': os.getenv('EMAIL_USE_TLS', 'True').lower() == 'true',
            'EMAIL_HOST_USER': os.getenv('EMAIL_HOST_USER'),
            'EMAIL_HOST_PASSWORD': os.getenv('EMAIL_HOST_PASSWORD'),
            'DEFAULT_FROM_EMAIL': os.getenv('DEFAULT_FROM_EMAIL'),
        }
