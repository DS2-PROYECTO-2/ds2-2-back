import json
from django.core.signing import TimestampSigner, BadSignature, SignatureExpired
import secrets
import hashlib
from urllib.parse import quote
from django.conf import settings
from django.urls import reverse

_SIGNER = TimestampSigner(salt="user-approval-links")

def generate_action_token(user_id: int, action: str) -> str:
    payload = json.dumps({"user_id": user_id, "action": action})
    return _SIGNER.sign(payload)

def verify_action_token(token: str, max_age_seconds: int = 86400) -> dict:
    try:
        payload = _SIGNER.unsign(token, max_age=max_age_seconds)  # por defecto 24h
        return json.loads(payload)
    except SignatureExpired:
        raise ValueError("El enlace expiró")
    except BadSignature:
        raise ValueError("Enlace inválido")
    


def generate_raw_token() -> str:
    return secrets.token_urlsafe(32)

def hash_token(raw_token: str) -> str:
    return hashlib.sha256(raw_token.encode()).hexdigest()

def build_password_reset_url(raw_token: str) -> str:
    # URL del frontend para reset de contraseña
    frontend_base = getattr(settings, "FRONTEND_BASE_URL", "http://localhost:5173")
    return f"{frontend_base}/reset-password?token={quote(raw_token, safe='')}"