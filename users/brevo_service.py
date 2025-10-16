import os
import requests
from django.conf import settings

BREVO_API_URL = "https://api.brevo.com/v3/smtp/email"

def send_email_via_brevo(to, subject, html_content, text_content=None):
    """
    Envía un correo usando Brevo API HTTP.
    """
    brevo_api_key = getattr(settings, 'BREVO_API_KEY', None)
    if not brevo_api_key:
        raise ValueError("BREVO_API_KEY no está configurado en las settings.")

    headers = {
        "accept": "application/json",
        "api-key": brevo_api_key,
        "content-type": "application/json"
    }

    # Extraer email del DEFAULT_FROM_EMAIL
    from_email = settings.DEFAULT_FROM_EMAIL
    if '<' in from_email and '>' in from_email:
        # Formato: "Nombre <email@domain.com>"
        from_email_clean = from_email.split('<')[1].split('>')[0].strip()
        from_name = from_email.split('<')[0].strip()
    else:
        # Formato: "email@domain.com"
        from_email_clean = from_email
        from_name = "Soporte DS2"

    payload = {
        "sender": {
            "name": from_name,
            "email": from_email_clean
        },
        "to": [
            {
                "email": to,
                "name": to.split('@')[0]  # Usar parte antes del @ como nombre
            }
        ],
        "subject": subject,
        "htmlContent": html_content
    }
    
    if text_content:
        payload["textContent"] = text_content

    try:
        print(f"[BREVO_DEBUG] Enviando request a Brevo API...")
        print(f"[BREVO_DEBUG] URL: {BREVO_API_URL}")
        print(f"[BREVO_DEBUG] Headers: {headers}")
        print(f"[BREVO_DEBUG] Payload: {payload}")

        response = requests.post(BREVO_API_URL, json=payload, headers=headers)

        print(f"[BREVO_DEBUG] Status Code: {response.status_code}")
        print(f"[BREVO_DEBUG] Response: {response.text}")

        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"[BREVO_ERROR] Request exception: {e}")
        raise Exception(f"Error enviando email via Brevo: {e}")
