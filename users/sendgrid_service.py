import requests
from django.conf import settings

SENDGRID_API_URL = "https://api.sendgrid.com/v3/mail/send"

def send_email_via_sendgrid(to, subject, html_content, text_content=None):
    """
    Envía un correo usando SendGrid API HTTP
    Funciona en Render plan gratuito
    """
    api_key = getattr(settings, 'SENDGRID_API_KEY', None)
    if not api_key:
        raise ValueError("SENDGRID_API_KEY no configurado")
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    payload = {
        "personalizations": [
            {
                "to": [{"email": to}],
                "subject": subject
            }
        ],
        "from": {
            "email": settings.DEFAULT_FROM_EMAIL,
            "name": "Soporte DS2"
        },
        "content": [
            {
                "type": "text/html",
                "value": html_content
            }
        ]
    }
    
    # Agregar texto plano si se proporciona
    if text_content:
        payload["content"].append({
            "type": "text/plain",
            "value": text_content
        })

    try:
        print(f"[SENDGRID_DEBUG] Enviando request a SendGrid API...")
        print(f"[SENDGRID_DEBUG] URL: {SENDGRID_API_URL}")
        print(f"[SENDGRID_DEBUG] Headers: {headers}")
        print(f"[SENDGRID_DEBUG] Payload: {payload}")
        
        response = requests.post(SENDGRID_API_URL, json=payload, headers=headers)
        
        print(f"[SENDGRID_DEBUG] Status Code: {response.status_code}")
        print(f"[SENDGRID_DEBUG] Response: {response.text}")
        
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"[SENDGRID_ERROR] Request exception: {e}")
        raise Exception(f"Error enviando email via SendGrid: {e}")
