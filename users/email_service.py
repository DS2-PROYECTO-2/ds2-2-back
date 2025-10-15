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
        print(f"[RESEND_DEBUG] Enviando request a Resend API...")
        print(f"[RESEND_DEBUG] URL: {RESEND_API_URL}")
        print(f"[RESEND_DEBUG] Headers: {headers}")
        print(f"[RESEND_DEBUG] Payload: {payload}")
        
        response = requests.post(RESEND_API_URL, json=payload, headers=headers)
        
        print(f"[RESEND_DEBUG] Status Code: {response.status_code}")
        print(f"[RESEND_DEBUG] Response: {response.text}")
        
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"[RESEND_ERROR] Request exception: {e}")
        raise Exception(f"Error enviando email via Resend: {e}")
