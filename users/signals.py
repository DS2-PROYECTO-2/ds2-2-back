from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import User, ApprovalLink
from notifications.models import Notification
from django.core.mail import send_mail
from django.conf import settings
from django.db.models.signals import post_delete
from django.urls import reverse
from urllib.parse import quote
import secrets
import hashlib


@receiver(post_save, sender=User)
def notify_admin_new_user_registration(sender, instance, created, **kwargs):
    """
    Envía notificación a administradores cuando un monitor se registra
    """
    if created and instance.role == 'monitor':
        # Obtener todos los administradores
        admin_users = User.objects.filter(role='admin', is_active=True, is_verified=True)
        
        # Crear notificación para cada administrador
        for admin in admin_users:
            Notification.objects.create(
                user=admin,
                notification_type='admin_verification',
                title=f'Nuevo monitor registrado: {instance.get_full_name()}',
                message=f'El monitor {instance.get_full_name()} ({instance.username}) se ha registrado y requiere verificación.',
                related_object_id=instance.id
            )
        
        # Email a admins con enlaces de acción
        admin_emails = list(admin_users.values_list('email', flat=True))
        if admin_emails:
            # Generar tokens aleatorios seguros
            approve_token = secrets.token_urlsafe(32)
            reject_token = secrets.token_urlsafe(32)
            
            # Crear hashes para almacenar en DB
            approve_hash = hashlib.sha256(approve_token.encode()).hexdigest()
            reject_hash = hashlib.sha256(reject_token.encode()).hexdigest()
            
            # Guardar enlaces en DB (ambos para el mismo usuario)
            ApprovalLink.objects.create(
                user=instance,
                action=ApprovalLink.APPROVE,
                token_hash=approve_hash
            )
            ApprovalLink.objects.create(
                user=instance,
                action=ApprovalLink.REJECT,
                token_hash=reject_hash
            )

            # URLs absolutas
            base = getattr(settings, "PUBLIC_BASE_URL", "http://localhost:8000")
            # URL-encode del token para que no se rompa por caracteres especiales
            approve_url = f"{base}{reverse('admin_user_activate')}?token={quote(approve_token, safe='')}"
            reject_url  = f"{base}{reverse('admin_user_delete')}?token={quote(reject_token, safe='')}"

            # Correo a admins (texto + HTML con botones)
            subject = '[DS2] Nuevo monitor pendiente de verificación'
            texto = (
                f"Nuevo monitor:\n"
                f"Nombre: {instance.get_full_name()} (@{instance.username})\n"
                f"Identificación: {instance.identification}\n\n"
                f"Aprobar: {approve_url}\n"
                f"Rechazar: {reject_url}\n"
            )
            html = f"""
<!doctype html>
<html>
  <body style=\"font-family:Segoe UI,Arial,sans-serif;background:#f6f7f9;padding:24px;\">
    <div style=\"max-width:560px;margin:0 auto;background:#ffffff;border-radius:12px;box-shadow:0 6px 24px rgba(0,0,0,.08);overflow:hidden;\">
      <div style=\"padding:20px 24px;border-bottom:1px solid #eef2f7;\">
        <h2 style=\"margin:0;color:#111827;\">Nuevo monitor registrado</h2>
        <p style=\"margin:6px 0 0;color:#6b7280;\">Requiere verificación de un administrador</p>
      </div>
      <div style=\"padding:20px 24px;\">
        <p style=\"margin:0 0 8px;color:#111827;\"><strong>Nombre:</strong> {instance.get_full_name()} (@{instance.username})</p>
        <p style=\"margin:0 0 20px;color:#111827;\"><strong>Identificación:</strong> {instance.identification}</p>
        <div style=\"display:flex;gap:12px;flex-wrap:wrap;\">
          <a href=\"{approve_url}\" style=\"text-decoration:none;background:#16a34a;color:#ffffff;padding:10px 16px;border-radius:8px;display:inline-block;\">Aprobar</a>
          <a href=\"{reject_url}\" style=\"text-decoration:none;background:#dc2626;color:#ffffff;padding:10px 16px;border-radius:8px;display:inline-block;\">Rechazar</a>
        </div>
        <p style=\"margin:20px 0 0;color:#6b7280;font-size:13px;\">El enlace expira en 24 horas.</p>
      </div>
    </div>
    <p style=\"text-align:center;color:#9ca3af;font-size:12px;margin-top:16px;\">DS2 • Notificación automática</p>
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
            
            # Solo mostrar enlaces en consola si está en modo consola (no SMTP real)
            if settings.EMAIL_BACKEND == 'django.core.mail.backends.console.EmailBackend':
                print(f"\n{'='*60}")
                print(f"ENLACES DE ACTIVACIÓN PARA: {instance.get_full_name()}")
                print(f"{'='*60}")
                print(f"APROBAR: {approve_url}")
                print(f"RECHAZAR: {reject_url}")
                print(f"{'='*60}\n")


@receiver(post_save, sender=User)
def notify_user_verification_status(sender, instance, **kwargs):
    """
    Notifica al usuario cuando su estado de verificación cambia
    """
    if hasattr(instance, '_verification_changed'):
        if instance.is_verified:
            # Nombre del verificador tolerante a None (enlace por correo)
            verifier_name = (
                instance.verified_by.get_full_name()
                if getattr(instance, "verified_by", None) else
                "un administrador"
            )

            # Notificación al usuario
            Notification.objects.create(
                user=instance,
                notification_type='admin_verification',
                title='¡Cuenta verificada!',
                message=f'Tu cuenta ha sido verificada exitosamente por {verifier_name}. Ya puedes acceder a todas las funcionalidades del sistema.',
                related_object_id=instance.id
            )
            # Email de activación
            try:
                send_mail(
                    subject='[DS2] Tu cuenta ha sido verificada',
                    message=(
                        f'Hola {instance.get_full_name()},\n\n'
                        f'Tu cuenta fue verificada por {verifier_name}.\n'
                        f'Ya puedes iniciar sesión y usar la plataforma.\n\n'
                        f'Saludos.'
                    ),
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[instance.email],
                    fail_silently=True,
                )
            except Exception:
                pass
        else:
            # Rechazo / desverificación
            Notification.objects.create(
                user=instance,
                notification_type='admin_verification',
                title='Verificación de cuenta',
                message='Tu solicitud de verificación ha sido procesada. Contacta al administrador para más información.',
                related_object_id=instance.id
            )
            # Email de rechazo/desverificación
            try:
                send_mail(
                    subject='[DS2] Actualización de verificación de cuenta',
                    message=(
                        f'Hola {instance.get_full_name()},\n\n'
                        f'Tu cuenta no ha sido verificada en este momento. '
                        f'Si crees que es un error, por favor contacta al administrador.\n\n'
                        f'Saludos.'
                    ),
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[instance.email],
                    fail_silently=True,
                )
            except Exception:
                pass

        # Limpiar el flag
        delattr(instance, '_verification_changed')


@receiver(post_delete, sender=User)
def notify_user_on_delete(sender, instance, **kwargs):
    """
    Envía correo al usuario cuando su cuenta es eliminada
    (por admin vía panel o endpoint)
    """
    if instance.email:
        try:
            send_mail(
                subject='[DS2] Tu cuenta ha sido eliminada',
                message=(
                    f'Hola {instance.get_full_name()},\n\n'
                    f'Tu registro ha sido eliminado por un administrador. '
                    f'Si necesitas más información, por favor contáctanos.\n\n'
                    f'Saludos.'
                ),
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[instance.email],
                fail_silently=True,
            )
        except Exception:
            pass