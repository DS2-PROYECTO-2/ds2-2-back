"""
Utilidades para envío de emails con Brevo API
"""
from django.conf import settings
from django.core.mail import send_mail
from .brevo_service import send_email_via_brevo


def send_email_unified(to, subject, text_content, html_content=None):
    """
    Función unificada para envío de emails que maneja:
    - Gmail SMTP en desarrollo local
    - Brevo API en producción
    - Locmem backend en testing
    """
    # Verificar si hay API key de Brevo configurada
    brevo_api_key = getattr(settings, 'BREVO_API_KEY', None)
    
    # En modo testing, usar fallback a locmem
    if brevo_api_key == 'test-key':
        print(f"[EMAIL_DEBUG] Modo testing detectado - usando locmem backend")
        result = send_mail(
            subject=subject,
            message=text_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[to] if isinstance(to, str) else to,
            html_message=html_content,
            fail_silently=False,
        )
        print(f"[EMAIL_SUCCESS] Correo enviado via locmem")
        return result
    
    # En desarrollo local (sin BREVO_API_KEY), usar Gmail SMTP
    if not brevo_api_key:
        print(f"[EMAIL_DEBUG] Modo desarrollo local - usando Gmail SMTP")
        result = send_mail(
            subject=subject,
            message=text_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[to] if isinstance(to, str) else to,
            html_message=html_content,
            fail_silently=False,
        )
        print(f"[EMAIL_SUCCESS] Correo enviado via Gmail SMTP")
        return result
    
    # En producción (con BREVO_API_KEY), usar Brevo API
    print(f"[EMAIL_DEBUG] Modo producción - usando Brevo API...")
    result = send_email_via_brevo(
        to=to,
        subject=subject,
        html_content=html_content,
        text_content=text_content
    )
    print(f"[EMAIL_SUCCESS] Correo enviado via Brevo API")
    return result
