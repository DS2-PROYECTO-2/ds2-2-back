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
import threading
import logging
from .tasks import (
    send_verification_email_async,
    send_user_deletion_email_async,
    send_admin_notification_email_async
)

logger = logging.getLogger(__name__)


@receiver(post_save, sender=User)
def notify_admin_new_user_registration(sender, instance, created, **kwargs):
    """
    Envía notificación a administradores cuando un monitor se registra
    OPTIMIZADO: Emails asíncronos + batch operations
    """
    if created and instance.role == 'monitor':
        try:
            # OPTIMIZACIÓN 1: Una sola query para obtener admins
            admin_users = User.objects.filter(
                role='admin', 
                is_active=True, 
                is_verified=True
            ).only('id', 'email')  # Solo campos necesarios
            
            if not admin_users.exists():
                logger.warning("No hay administradores activos para notificar")
                return
            
            # OPTIMIZACIÓN 2: Batch creation de notificaciones
            notifications = []
            for admin in admin_users:
                notifications.append(Notification(
                    user=admin,
                    notification_type='admin_verification',
                    title=f'Nuevo monitor registrado: {instance.get_full_name()}',
                    message=f'El monitor {instance.get_full_name()} ({instance.username}) se ha registrado y requiere verificación.',
                    related_object_id=instance.id
                ))
            
            # Crear todas las notificaciones de una vez
            Notification.objects.bulk_create(notifications)
            
            # OPTIMIZACIÓN 3: Email asíncrono
            admin_emails = list(admin_users.values_list('email', flat=True))
            if admin_emails:
                # Generar tokens
                approve_token = secrets.token_urlsafe(32)
                reject_token = secrets.token_urlsafe(32)
                
                # Crear hashes
                approve_hash = hashlib.sha256(approve_token.encode()).hexdigest()
                reject_hash = hashlib.sha256(reject_token.encode()).hexdigest()
                
                # OPTIMIZACIÓN 4: Batch creation de ApprovalLinks
                approval_links = [
                    ApprovalLink(user=instance, action=ApprovalLink.APPROVE, token_hash=approve_hash),
                    ApprovalLink(user=instance, action=ApprovalLink.REJECT, token_hash=reject_hash)
                ]
                ApprovalLink.objects.bulk_create(approval_links)

                # URLs
                base = getattr(settings, "PUBLIC_BASE_URL", "http://localhost:8000")
                approve_url = f"{base}{reverse('admin_user_activate')}?token={quote(approve_token, safe='')}"
                reject_url = f"{base}{reverse('admin_user_delete')}?token={quote(reject_token, safe='')}"

                # SOLUCIÓN TEMPORAL: Email síncrono para garantizar envío
                try:
                    send_admin_notification_email_async(
                        admin_emails,
                        instance.get_full_name(),
                        instance.username,
                        instance.identification,
                        approve_url,
                        reject_url
                    )
                    logger.info(f"Email de notificación enviado a {len(admin_emails)} administradores")
                except Exception as e:
                    logger.error(f"Error enviando email de notificación: {e}")
                
                # Solo mostrar enlaces en consola si está en modo consola
                if settings.EMAIL_BACKEND == 'django.core.mail.backends.console.EmailBackend':
                    print(f"\n{'='*60}")
                    print(f"ENLACES DE ACTIVACIÓN PARA: {instance.get_full_name()}")
                    print(f"{'='*60}")
                    print(f"APROBAR: {approve_url}")
                    print(f"RECHAZAR: {reject_url}")
                    print(f"{'='*60}\n")
                    
        except Exception as e:
            logger.error(f"Error en notify_admin_new_user_registration: {e}")


@receiver(post_save, sender=User)
def notify_admin_registration(sender, instance, created, **kwargs):
    """
    Signal optimizado para registro de administradores
    OPTIMIZADO: Solo notificación básica, sin emails pesados
    """
    if created and instance.role == 'admin':
        try:
            # OPTIMIZACIÓN: Solo crear notificación básica para admins
            # No enviar emails pesados para admins (se auto-verifican)
            logger.info(f"Administrador {instance.username} registrado exitosamente")
            
        except Exception as e:
            logger.error(f"Error en notify_admin_registration: {e}")


@receiver(post_save, sender=User)
def notify_user_verification_status(sender, instance, **kwargs):
    """
    Notifica al usuario cuando su estado de verificación cambia
    OPTIMIZADO: Emails asíncronos + manejo de errores mejorado
    """
    if hasattr(instance, '_verification_changed'):
        try:
            if instance.is_verified:
                # Nombre del verificador tolerante a None
                verifier_name = (
                    instance.verified_by.get_full_name()
                    if getattr(instance, "verified_by", None) else
                    "un administrador"
                )

                # OPTIMIZACIÓN: Crear notificación directamente
                Notification.objects.create(
                    user=instance,
                    notification_type='admin_verification',
                    title='¡Cuenta verificada!',
                    message=f'Tu cuenta ha sido verificada exitosamente por {verifier_name}. Ya puedes acceder a todas las funcionalidades del sistema.',
                    related_object_id=instance.id
                )
                
                # SOLUCIÓN TEMPORAL: Email síncrono para garantizar envío
                try:
                    send_verification_email_async(
                        instance.email,
                        instance.get_full_name(),
                        verifier_name,
                        is_verified=True
                    )
                    logger.info(f"Email de verificación enviado a {instance.email}")
                except Exception as e:
                    logger.error(f"Error enviando email de verificación: {e}")
                
            else:
                # Rechazo / desverificación
                Notification.objects.create(
                    user=instance,
                    notification_type='admin_verification',
                    title='Verificación de cuenta',
                    message='Tu solicitud de verificación ha sido procesada. Contacta al administrador para más información.',
                    related_object_id=instance.id
                )
                
                # SOLUCIÓN TEMPORAL: Email síncrono para garantizar envío
                try:
                    send_verification_email_async(
                        instance.email,
                        instance.get_full_name(),
                        is_verified=False
                    )
                    logger.info(f"Email de desverificación enviado a {instance.email}")
                except Exception as e:
                    logger.error(f"Error enviando email de desverificación: {e}")

            # Limpiar el flag
            delattr(instance, '_verification_changed')
            
        except Exception as e:
            logger.error(f"Error en notify_user_verification_status: {e}")


@receiver(post_delete, sender=User)
def notify_user_on_delete(sender, instance, **kwargs):
    """
    Envía correo al usuario cuando su cuenta es eliminada
    OPTIMIZADO: Email asíncrono + manejo de errores mejorado
    """
    if instance.email:
        try:
            # SOLUCIÓN TEMPORAL: Email síncrono para garantizar envío
            try:
                send_user_deletion_email_async(
                    instance.email,
                    instance.get_full_name()
                )
                logger.info(f"Email de eliminación enviado a {instance.email}")
            except Exception as e:
                logger.error(f"Error enviando email de eliminación: {e}")
            
        except Exception as e:
            logger.error(f"Error en notify_user_on_delete: {e}")