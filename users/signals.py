from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from .models import User
from notifications.models import Notification


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


@receiver(post_save, sender=User)
def notify_user_verification_status(sender, instance, **kwargs):
    """
    Notifica al usuario cuando su estado de verificación cambia
    """
    if hasattr(instance, '_verification_changed'):
        if instance.is_verified:
            # Usuario fue verificado
            Notification.objects.create(
                user=instance,
                notification_type='admin_verification',
                title='¡Cuenta verificada!',
                message=f'Tu cuenta ha sido verificada exitosamente por {instance.verified_by.get_full_name()}. Ya puedes acceder a todas las funcionalidades del sistema.',
                related_object_id=instance.id
            )
        else:
            # Usuario fue rechazado/desverificado
            Notification.objects.create(
                user=instance,
                notification_type='admin_verification',
                title='Verificación de cuenta',
                message='Tu solicitud de verificación ha sido procesada. Contacta al administrador para más información.',
                related_object_id=instance.id
            )
        
        # Limpiar el flag
        delattr(instance, '_verification_changed')