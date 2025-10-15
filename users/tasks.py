"""
Tareas asíncronas para envío de emails
Optimización de signals para mejorar rendimiento
"""
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
import logging

logger = logging.getLogger(__name__)


def send_verification_email_async(user_email, user_name, verifier_name=None, is_verified=True):
    """
    Envía email de verificación de forma asíncrona
    """
    try:
        if is_verified:
            subject = '[DS2] Tu cuenta ha sido verificada'
            message = (
                f'Hola {user_name},\n\n'
                f'Tu cuenta fue verificada por {verifier_name or "un administrador"}.\n'
                f'Ya puedes iniciar sesión y usar la plataforma.\n\n'
                f'Saludos.'
            )
        else:
            subject = '[DS2] Actualización de verificación de cuenta'
            message = (
                f'Hola {user_name},\n\n'
                f'Tu cuenta no ha sido verificada en este momento. '
                f'Si crees que es un error, por favor contacta al administrador.\n\n'
                f'Saludos.'
            )
        
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user_email],
            fail_silently=True,
        )
        logger.info(f"Email de verificación enviado a {user_email}")
    except Exception as e:
        logger.error(f"Error enviando email de verificación a {user_email}: {e}")


def send_user_deletion_email_async(user_email, user_name):
    """
    Envía email de eliminación de cuenta de forma asíncrona
    """
    try:
        send_mail(
            subject='[DS2] Tu cuenta ha sido eliminada',
            message=(
                f'Hola {user_name},\n\n'
                f'Tu registro ha sido eliminado por un administrador. '
                f'Si necesitas más información, por favor contáctanos.\n\n'
                f'Saludos.'
            ),
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user_email],
            fail_silently=True,
        )
        logger.info(f"Email de eliminación enviado a {user_email}")
    except Exception as e:
        logger.error(f"Error enviando email de eliminación a {user_email}: {e}")


def send_admin_notification_email_async(admin_emails, user_name, user_username, user_identification, approve_url, reject_url):
    """
    Envía notificación a administradores de forma asíncrona
    """
    try:
        subject = '[DS2] Nuevo monitor pendiente de verificación'
        
        # Versión texto
        texto = (
            f"Nuevo monitor:\n"
            f"Nombre: {user_name} (@{user_username})\n"
            f"Identificación: {user_identification}\n\n"
            f"Aprobar: {approve_url}\n"
            f"Rechazar: {reject_url}\n"
        )
        
        # Versión HTML
        html = f"""
<!doctype html>
<html>
  <body style="font-family:Segoe UI,Arial,sans-serif;background:#f6f7f9;padding:24px;">
    <div style="max-width:560px;margin:0 auto;background:#ffffff;border-radius:12px;box-shadow:0 6px 24px rgba(0,0,0,.08);overflow:hidden;">
      <div style="padding:20px 24px;border-bottom:1px solid #eef2f7;">
        <h2 style="margin:0;color:#111827;">Nuevo monitor registrado</h2>
        <p style="margin:6px 0 0;color:#6b7280;">Requiere verificación de un administrador</p>
      </div>
      <div style="padding:20px 24px;">
        <p style="margin:0 0 8px;color:#111827;"><strong>Nombre:</strong> {user_name} (@{user_username})</p>
        <p style="margin:0 0 20px;color:#111827;"><strong>Identificación:</strong> {user_identification}</p>
        <div style="display:flex;gap:12px;flex-wrap:wrap;">
          <a href="{approve_url}" style="text-decoration:none;background:#16a34a;color:#ffffff;padding:10px 16px;border-radius:8px;display:inline-block;">Aprobar</a>
          <a href="{reject_url}" style="text-decoration:none;background:#dc2626;color:#ffffff;padding:10px 16px;border-radius:8px;display:inline-block;">Rechazar</a>
        </div>
        <p style="margin:20px 0 0;color:#6b7280;font-size:13px;">El enlace expira en 24 horas.</p>
      </div>
    </div>
    <p style="text-align:center;color:#9ca3af;font-size:12px;margin-top:16px;">DS2 • Notificación automática</p>
  </body>
</html>
"""
        
        send_mail(
            subject=subject,
            message=texto,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=admin_emails,
            html_message=html,
            fail_silently=True,
        )
        logger.info(f"Email de notificación enviado a {len(admin_emails)} administradores")
    except Exception as e:
        logger.error(f"Error enviando email de notificación a administradores: {e}")
