from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.conf import settings
from django.core.mail import send_mail
from django.urls import reverse
from django.db import transaction

from urllib.parse import quote
import threading
import secrets
import hashlib
import sys

from .models import User, ApprovalLink
from notifications.models import Notification


@receiver(post_save, sender=User)
def notify_admin_new_user_registration(sender, instance, created, **kwargs):
    """
    Notifica a administradores cuando un monitor se registra.
    Optimizado para no bloquear la respuesta HTTP:
    - En producción usa transaction.on_commit + hilo para el email
    - En tests (email backend en memoria) ejecuta sincrónicamente
    """
    if not (created and instance.role == 'monitor'):
        return

    is_test_backend = settings.EMAIL_BACKEND == 'django.core.mail.backends.locmem.EmailBackend'

    def job():
        # Obtener todos los administradores activos y verificados
        admin_users = User.objects.filter(role='admin', is_active=True, is_verified=True)

        # Crear notificación para cada admin
        for admin in admin_users:
            Notification.objects.create(
                user=admin,
                notification_type='admin_verification',
                title=f'Nuevo monitor registrado: {instance.get_full_name()}',
                message=(
                    f'El monitor {instance.get_full_name()} ({instance.username}) '
                    f'se ha registrado y requiere verificación.'
                ),
                related_object_id=instance.id,
            )

        admin_emails = list(admin_users.values_list('email', flat=True))
        if not admin_emails:
            return

        # Generar tokens y hashes
        approve_token = secrets.token_urlsafe(32)
        reject_token = secrets.token_urlsafe(32)
        approve_hash = hashlib.sha256(approve_token.encode()).hexdigest()
        reject_hash = hashlib.sha256(reject_token.encode()).hexdigest()

        # Guardar enlaces de aprobación/rechazo
        ApprovalLink.objects.create(user=instance, action=ApprovalLink.APPROVE, token_hash=approve_hash)
        ApprovalLink.objects.create(user=instance, action=ApprovalLink.REJECT, token_hash=reject_hash)

        # Construir URLs absolutas
        base = getattr(settings, 'PUBLIC_BASE_URL', 'http://localhost:8000')
        approve_url = f"{base}{reverse('admin_user_activate')}?token={quote(approve_token, safe='')}"
        reject_url = f"{base}{reverse('admin_user_delete')}?token={quote(reject_token, safe='')}"

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

def _send():
    try:
        print(f"[BREVO_DEBUG] ========== INICIANDO ENVÍO CON BREVO ==========")
        print(f"[BREVO_DEBUG] Timestamp: {__import__('datetime').datetime.now()}")
        print(f"[BREVO_DEBUG] Admin emails: {admin_emails}")
        print(f"[BREVO_DEBUG] From email: {settings.DEFAULT_FROM_EMAIL}")
        print(f"[BREVO_DEBUG] Subject: {subject}")
        print(f"[BREVO_DEBUG] Text content length: {len(texto)}")
        print(f"[BREVO_DEBUG] HTML content length: {len(html)}")
        
        # Verificar configuración de Brevo
        print(f"[BREVO_DEBUG] ========== CONFIGURACIÓN BREVO ==========")
        print(f"[BREVO_DEBUG] EMAIL_BACKEND: {getattr(settings, 'EMAIL_BACKEND', 'No configurado')}")
        print(f"[BREVO_DEBUG] BREVO_API_KEY: {'***' if getattr(settings, 'ANYMAIL', {}).get('BREVO_API_KEY') else 'No configurado'}")
        print(f"[BREVO_DEBUG] DEFAULT_FROM_EMAIL: {settings.DEFAULT_FROM_EMAIL}")
        
        # Verificar variables de entorno
        print(f"[BREVO_DEBUG] ========== VARIABLES DE ENTORNO ==========")
        import os
        print(f"[BREVO_DEBUG] DJANGO_ENV: {os.getenv('DJANGO_ENV', 'No configurado')}")
        print(f"[BREVO_DEBUG] BREVO_API_KEY env: {'***' if os.getenv('BREVO_API_KEY') else 'No configurado'}")
        print(f"[BREVO_DEBUG] DEFAULT_FROM_EMAIL env: {os.getenv('DEFAULT_FROM_EMAIL', 'No configurado')}")
        
        # Verificar configuración de Anymail
        print(f"[BREVO_DEBUG] ========== CONFIGURACIÓN ANYMAIL ==========")
        anymail_config = getattr(settings, 'ANYMAIL', {})
        print(f"[BREVO_DEBUG] ANYMAIL config: {anymail_config}")
        print(f"[BREVO_DEBUG] ANYMAIL BREVO_API_KEY: {'***' if anymail_config.get('BREVO_API_KEY') else 'No configurado'}")
        
        # Verificar que Anymail esté instalado
        print(f"[BREVO_DEBUG] ========== VERIFICACIÓN ANYMAIL ==========")
        try:
            import anymail
            print(f"[BREVO_DEBUG] Anymail version: {anymail.__version__}")
            print(f"[BREVO_DEBUG] Anymail backends disponibles: {anymail.backends.__all__}")
        except ImportError as import_error:
            print(f"[BREVO_ERROR] Anymail no está instalado: {import_error}")
            raise
        
        # Verificar backend específico
        print(f"[BREVO_DEBUG] ========== VERIFICACIÓN BACKEND ==========")
        try:
            from anymail.backends.brevo import EmailBackend
            print(f"[BREVO_DEBUG] Brevo EmailBackend importado correctamente")
        except ImportError as backend_error:
            print(f"[BREVO_ERROR] Error importando Brevo backend: {backend_error}")
            raise
        
        # Usar send_mail con Brevo
        print(f"[BREVO_DEBUG] ========== ENVIANDO EMAIL VIA BREVO ==========")
        print(f"[BREVO_DEBUG] Usando Brevo API...")
        print(f"[BREVO_DEBUG] Preparando send_mail con:")
        print(f"[BREVO_DEBUG]   - subject: {subject}")
        print(f"[BREVO_DEBUG]   - from_email: {settings.DEFAULT_FROM_EMAIL}")
        print(f"[BREVO_DEBUG]   - recipient_list: {admin_emails}")
        print(f"[BREVO_DEBUG]   - html_message length: {len(html)}")
        print(f"[BREVO_DEBUG]   - fail_silently: False")
        
        # Log del contenido del email
        print(f"[BREVO_DEBUG] ========== CONTENIDO DEL EMAIL ==========")
        print(f"[BREVO_DEBUG] Subject: {subject}")
        print(f"[BREVO_DEBUG] From: {settings.DEFAULT_FROM_EMAIL}")
        print(f"[BREVO_DEBUG] To: {admin_emails}")
        print(f"[BREVO_DEBUG] Text preview: {texto[:100]}...")
        print(f"[BREVO_DEBUG] HTML preview: {html[:200]}...")
        
        # Intentar envío
        print(f"[BREVO_DEBUG] ========== EJECUTANDO SEND_MAIL ==========")
        result = send_mail(
            subject=subject,
            message=texto,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=admin_emails,
            html_message=html,
            fail_silently=False,
        )
        
        print(f"[BREVO_DEBUG] ========== RESULTADO BREVO ==========")
        print(f"[BREVO_DEBUG] Resultado send_mail: {result}")
        print(f"[BREVO_DEBUG] Tipo de resultado: {type(result)}")
        print(f"[BREVO_SUCCESS] Correo enviado via Brevo API a {len(admin_emails)} admins")
        print(f"[BREVO_DEBUG] ========== EMAIL ENVIADO EXITOSAMENTE ==========")
        
    except Exception as e:
        # Log explícito para depurar problemas de email
        print(f"[BREVO_ERROR] ========== ERROR EN ENVÍO DE EMAIL ==========")
        print(f"[BREVO_ERROR] Timestamp: {__import__('datetime').datetime.now()}")
        print(f"[BREVO_ERROR] Error enviando correo a admins: {e}")
        print(f"[BREVO_ERROR] Tipo de error: {type(e).__name__}")
        print(f"[BREVO_ERROR] Módulo del error: {type(e).__module__}")
        print(f"[BREVO_ERROR] Args del error: {e.args}")
        
        # Información adicional del error
        print(f"[BREVO_ERROR] ========== INFORMACIÓN ADICIONAL DEL ERROR ==========")
        try:
            if hasattr(e, 'errno'):
                print(f"[BREVO_ERROR] Error number: {e.errno}")
            if hasattr(e, 'strerror'):
                print(f"[BREVO_ERROR] Error string: {e.strerror}")
            if hasattr(e, 'filename'):
                print(f"[BREVO_ERROR] Error filename: {e.filename}")
            if hasattr(e, 'response'):
                print(f"[BREVO_ERROR] HTTP Response: {e.response}")
            if hasattr(e, 'status_code'):
                print(f"[BREVO_ERROR] HTTP Status Code: {e.status_code}")
        except Exception as debug_error:
            print(f"[BREVO_ERROR] Error obteniendo info adicional: {debug_error}")
        
        # Traceback completo
        import traceback
        print(f"[BREVO_ERROR] ========== TRACEBACK COMPLETO ==========")
        print(f"[BREVO_ERROR] {traceback.format_exc()}")
        print(f"[BREVO_ERROR] ========== FIN DEL ERROR ==========")
        
        # Información del sistema
        print(f"[BREVO_ERROR] ========== INFORMACIÓN DEL SISTEMA ==========")
        try:
            import sys
            print(f"[BREVO_ERROR] Python version: {sys.version}")
            print(f"[BREVO_ERROR] Django version: {__import__('django').get_version()}")
            print(f"[BREVO_ERROR] Anymail version: {__import__('anymail').__version__}")
        except Exception as sys_error:
            print(f"[BREVO_ERROR] Error obteniendo info del sistema: {sys_error}")
        
        # Re-raise para que el error se propague
        raise

        # En tests, ejecutar sincrónicamente para que mail.outbox funcione
        # En producción, usar hilo asíncrono para no bloquear
        is_testing = getattr(settings, 'TESTING', False) or 'test' in sys.argv
        
        if is_testing or is_test_backend:
            _send()
        else:
            threading.Thread(target=_send, daemon=True).start()

        if settings.EMAIL_BACKEND == 'django.core.mail.backends.console.EmailBackend':
            print(f"\n{'='*60}")
            print(f"ENLACES DE ACTIVACIÓN PARA: {instance.get_full_name()}")
            print(f"{'='*60}")
            print(f"APROBAR: {approve_url}")
            print(f"RECHAZAR: {reject_url}")
            print(f"{'='*60}\n")

    if is_test_backend:
        job()
    else:
        transaction.on_commit(job)


@receiver(post_save, sender=User)
def notify_user_verification_status(sender, instance, **kwargs):
    """
    Notifica al usuario cuando su estado de verificación cambia
    """
    if hasattr(instance, '_verification_changed'):
        if instance.is_verified:
            verifier_name = (
                instance.verified_by.get_full_name()
                if getattr(instance, 'verified_by', None) else 'un administrador'
            )

            Notification.objects.create(
                user=instance,
                notification_type='admin_verification',
                title='¡Cuenta verificada!',
                message=(
                    f'Tu cuenta ha sido verificada exitosamente por {verifier_name}. '
                    f'Ya puedes acceder a todas las funcionalidades del sistema.'
                ),
                related_object_id=instance.id,
            )
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
            Notification.objects.create(
                user=instance,
                notification_type='admin_verification',
                title='Verificación de cuenta',
                message='Tu solicitud de verificación ha sido procesada. Contacta al administrador para más información.',
                related_object_id=instance.id,
            )
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

