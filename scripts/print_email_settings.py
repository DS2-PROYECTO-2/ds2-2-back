import os
import sys
from pathlib import Path


def main() -> int:
    # Asegurar que el proyecto esté en sys.path (para importar ds2_back)
    script_path = Path(__file__).resolve()
    project_root = script_path.parent.parent  # carpeta raíz donde está manage.py
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))

    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ds2_back.settings")
    try:
        import django  # type: ignore
        django.setup()
    except Exception as exc:  # pragma: no cover
        print(f"ERROR: No se pudo inicializar Django: {exc}")
        return 1

    from django.conf import settings  # type: ignore
    from django.core.mail import send_mail  # type: ignore

    print("Configuración efectiva de email:")
    print(f"  BACKEND = {getattr(settings, 'EMAIL_BACKEND', None)}")
    print(f"  HOST    = {getattr(settings, 'EMAIL_HOST', None)}")
    print(f"  PORT    = {getattr(settings, 'EMAIL_PORT', None)}")
    print(f"  TLS     = {getattr(settings, 'EMAIL_USE_TLS', None)}")
    print(f"  USER    = {getattr(settings, 'EMAIL_HOST_USER', None)}")
    print(f"  FROM    = {getattr(settings, 'DEFAULT_FROM_EMAIL', None)}")

    recipient = os.environ.get("TEST_EMAIL_RECIPIENT") or getattr(settings, "EMAIL_HOST_USER", None)
    if not recipient:
        print("ADVERTENCIA: No hay destinatario para prueba (TEST_EMAIL_RECIPIENT ni EMAIL_HOST_USER). Saltando envío.")
        return 0

    print(f"\nIntentando envío de prueba a: {recipient}")
    try:
        sent = send_mail(
            subject="Prueba DS2 correo",
            message="Mensaje de prueba automático.",
            from_email=getattr(settings, "DEFAULT_FROM_EMAIL", None),
            recipient_list=[recipient],
            fail_silently=False,
        )
        print(f"Resultado send_mail: {sent}")
        return 0
    except Exception as exc:  # pragma: no cover
        print(f"ERROR SMTP: {exc}")
        return 2


if __name__ == "__main__":
    sys.exit(main())


