import json
from django.core.signing import TimestampSigner, BadSignature, SignatureExpired

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