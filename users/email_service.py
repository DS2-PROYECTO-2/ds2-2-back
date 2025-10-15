import os
import requests
from django.conf import settings

RESEND_API_URL = "https://api.resend.com/emails"

def send_email_via_resend(to, subject, html_content, text_content=None):
    """
    Envía un correo usando Resend API HTTP (no SMTP)
    Funciona en Render plan gratuito
    """
    api_key = getattr(settings, 'RESEND_API_KEY', None)
    if not api_key:
        raise ValueError("RESEND_API_KEY no configurado")
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    payload = {
        "from": "Soporte DS2 <onboarding@resend.dev>",  # Email genérico de Resend
        "to": [to] if isinstance(to, str) else to,
        "subject": subject,
        "html": html_content
    }
    
    # Agregar texto plano si se proporciona
    if text_content:
        payload["text"] = text_content

    try:
        response = requests.post(RESEND_API_URL, json=payload, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        raise Exception(f"Error enviando email via Resend: {e}")
