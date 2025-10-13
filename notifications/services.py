from django.db import models
from django.utils import timezone
from django.conf import settings
from django.core.mail import send_mail
from datetime import timedelta
from .models import Notification
from rooms.models import RoomEntry
from users.models import User
import logging

logger = logging.getLogger(__name__)


class NotificationService:
    """
    Servicio para manejar la lógica de negocio de notificaciones
    """
    
    @staticmethod
    def create_notification(user, notification_type, title, message, related_object_id=None):
        """
        Crear una nueva notificación
        """
        try:
            notification = Notification.objects.create(
                user=user,
                notification_type=notification_type,
                title=title,
                message=message,
                related_object_id=related_object_id
            )
            logger.info(f"Notificación creada: {notification_type} para {user.username}")
            return notification
        except Exception as e:
            logger.error(f"Error creando notificación: {e}")
            return None
    
    @staticmethod
    def notify_excessive_hours(room_entry):
        """
        Crear notificaciones de exceso de horas para administradores
        cuando un monitor excede las 8 horas continuas
        """
        try:
            # Calcular duración actual
            from rooms.services import RoomEntryBusinessLogic
            duration_info = RoomEntryBusinessLogic.calculate_session_duration(room_entry)
            # Para entradas activas, usar current_duration_hours; para completadas, usar total_duration_hours
            total_hours = duration_info.get('total_duration_hours', 0) or duration_info.get('current_duration_hours', 0)
            
            if total_hours > 8:
                # Obtener todos los administradores
                admins = User.objects.filter(role='admin', is_active=True)
                
                if not admins.exists():
                    logger.warning(f"No hay administradores para notificar exceso de horas de {room_entry.user.username}")
                    return False
                
                excess_hours = round(total_hours - 8, 2)
                
                for admin in admins:
                    title = f"⚠️ Exceso de Horas - {room_entry.user.get_full_name()}"
                    message = (
                        f"El monitor {room_entry.user.get_full_name()} ({room_entry.user.username}) "
                        f"ha excedido las 8 horas continuas en la sala {room_entry.room.name}.\n\n"
                        f"⏰ Duración actual: {total_hours:.1f} horas\n"
                        f"⚠️ Exceso: {excess_hours:.1f} horas\n"
                        f"🏢 Sala: {room_entry.room.name}\n"
                        f"📅 Desde: {room_entry.entry_time.strftime('%d/%m/%Y %H:%M')}"
                    )
                    
                    # Crear notificación
                    NotificationService.create_notification(
                        user=admin,
                        notification_type=Notification.EXCESSIVE_HOURS,
                        title=title,
                        message=message,
                        related_object_id=room_entry.id
                    )
                    
                    # Enviar email de alerta
                    NotificationService.send_excessive_hours_email(admin, room_entry, total_hours, excess_hours)
                
                logger.warning(f"Notificaciones de exceso de horas enviadas para {room_entry.user.username}: {total_hours:.1f}h")
                return True
            else:
                logger.info(f"No se exceden las 8 horas para {room_entry.user.username}: {total_hours:.1f}h")
                return False
                
        except Exception as e:
            logger.error(f"Error notificando exceso de horas: {e}")
            return False
    
    @staticmethod
    def send_excessive_hours_email(admin, room_entry, total_hours, excess_hours):
        """
        Enviar email de alerta por exceso de horas a administradores
        """
        try:
            subject = f'[DS2] ALERTA: Exceso de Horas - {room_entry.user.get_full_name()}'
            
            # Texto plano
            text_message = (
                f"ALERTA DE EXCESO DE HORAS\n\n"
                f"El monitor {room_entry.user.get_full_name()} ({room_entry.user.username}) "
                f"ha excedido las 8 horas continuas en la sala {room_entry.room.name}.\n\n"
                f"DATOS DEL USUARIO:\n"
                f"• Nombre: {room_entry.user.get_full_name()}\n"
                f"• Username: {room_entry.user.username}\n"
                f"• Email: {room_entry.user.email}\n"
                f"• Identificación: {room_entry.user.identification}\n"
                f"• Teléfono: {room_entry.user.phone}\n\n"
                f"DATOS DE LA SESIÓN:\n"
                f"• Sala: {room_entry.room.name}\n"
                f"• Hora de entrada: {room_entry.entry_time.strftime('%d/%m/%Y %H:%M')}\n"
                f"• Duración actual: {total_hours:.1f} horas\n"
                f"• Exceso: {excess_hours:.1f} horas\n\n"
                f"Esta es una alerta automática del sistema DS2."
            )
            
            # HTML con card profesional
            html_message = f"""
<!doctype html>
<html>
  <body style="font-family:Segoe UI,Arial,sans-serif;background:#f6f7f9;padding:24px;">
    <div style="max-width:600px;margin:0 auto;background:#ffffff;border-radius:12px;box-shadow:0 6px 24px rgba(0,0,0,.08);overflow:hidden;">
      <div style="padding:20px 24px;border-bottom:1px solid #eef2f7;background:#dc2626;">
        <h2 style="margin:0;color:#ffffff;">⚠️ ALERTA: Exceso de Horas</h2>
        <p style="margin:6px 0 0;color:#fecaca;">Monitor ha excedido las 8 horas continuas</p>
      </div>
      <div style="padding:20px 24px;">
        <div style="background:#fef2f2;border:1px solid #fecaca;border-radius:8px;padding:16px;margin-bottom:20px;">
          <h3 style="margin:0 0 12px;color:#dc2626;">Datos del Usuario</h3>
          <div style="display:grid;grid-template-columns:1fr 1fr;gap:12px;">
            <div>
              <strong>Nombre:</strong><br>
              <span style="color:#374151;">{room_entry.user.get_full_name()}</span>
            </div>
            <div>
              <strong>Username:</strong><br>
              <span style="color:#374151;">{room_entry.user.username}</span>
            </div>
            <div>
              <strong>Email:</strong><br>
              <span style="color:#374151;">{room_entry.user.email}</span>
            </div>
            <div>
              <strong>Identificación:</strong><br>
              <span style="color:#374151;">{room_entry.user.identification}</span>
            </div>
            <div>
              <strong>Teléfono:</strong><br>
              <span style="color:#374151;">{room_entry.user.phone}</span>
            </div>
            <div>
              <strong>Sala:</strong><br>
              <span style="color:#374151;">{room_entry.room.name}</span>
            </div>
          </div>
        </div>
        
        <div style="background:#fef3c7;border:1px solid #f59e0b;border-radius:8px;padding:16px;margin-bottom:20px;">
          <h3 style="margin:0 0 12px;color:#d97706;">Datos de la Sesión</h3>
          <div style="display:grid;grid-template-columns:1fr 1fr;gap:12px;">
            <div>
              <strong>Hora de entrada:</strong><br>
              <span style="color:#374151;">{room_entry.entry_time.strftime('%d/%m/%Y %H:%M')}</span>
            </div>
            <div>
              <strong>Duración actual:</strong><br>
              <span style="color:#dc2626;font-weight:bold;">{total_hours:.1f} horas</span>
            </div>
            <div>
              <strong>Exceso:</strong><br>
              <span style="color:#dc2626;font-weight:bold;">{excess_hours:.1f} horas</span>
            </div>
            <div>
              <strong>Estado:</strong><br>
              <span style="color:#dc2626;font-weight:bold;">⚠️ EXCESO DETECTADO</span>
            </div>
          </div>
        </div>
        
        <div style="background:#f3f4f6;border-radius:8px;padding:16px;text-align:center;">
          <p style="margin:0;color:#6b7280;font-size:14px;">
            Esta es una alerta automática del sistema DS2.<br>
            Se recomienda contactar al monitor para verificar su estado.
          </p>
        </div>
      </div>
    </div>
    <p style="text-align:center;color:#9ca3af;font-size:12px;margin-top:16px;">DS2 • Sistema de Monitoreo</p>
  </body>
</html>
"""
            
            send_mail(
                subject=subject,
                message=text_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[admin.email],
                html_message=html_message,
                fail_silently=True,
            )
            
            logger.info(f"Email de exceso de horas enviado a {admin.email}")
            
        except Exception as e:
            logger.error(f"Error enviando email de exceso de horas: {e}")
    
    @staticmethod
    def notify_room_entry(room_entry, is_entry=True):
        """
        Notificar entrada o salida de sala
        """
        try:
            action = "entró" if is_entry else "salió"
            emoji = "🚪" if is_entry else "🚪"
            
            title = f"{emoji} {room_entry.user.get_full_name()} {action} a la sala"
            message = (
                f"El monitor {room_entry.user.get_full_name()} {action} "
                f"a la sala {room_entry.room.name}.\n\n"
                f"🏢 Sala: {room_entry.room.name}\n"
                f"👤 Monitor: {room_entry.user.get_full_name()}\n"
                f"📅 Hora: {room_entry.entry_time.strftime('%d/%m/%Y %H:%M')}"
            )
            
            # Notificar a administradores
            admins = User.objects.filter(role='admin', is_active=True)
            for admin in admins:
                NotificationService.create_notification(
                    user=admin,
                    notification_type=Notification.ROOM_ENTRY if is_entry else Notification.ROOM_EXIT,
                    title=title,
                    message=message,
                    related_object_id=room_entry.id
                )
            
            logger.info(f"Notificación de {action} enviada para {room_entry.user.username}")
            return True
            
        except Exception as e:
            logger.error(f"Error notificando entrada/salida: {e}")
            return False
    
    @staticmethod
    def check_and_notify_excessive_hours():
        """
        Verificar todas las entradas activas y notificar exceso de horas
        Esta función se puede llamar periódicamente (cada hora)
        """
        try:
            # Obtener todas las entradas activas
            active_entries = RoomEntry.objects.filter(exit_time__isnull=True)
            notifications_sent = 0
            
            for entry in active_entries:
                # Verificar si ya se envió notificación para esta entrada
                existing_notification = Notification.objects.filter(
                    notification_type=Notification.EXCESSIVE_HOURS,
                    related_object_id=entry.id,
                    created_at__gte=timezone.now() - timedelta(hours=1)  # No duplicar en 1 hora
                ).exists()
                
                if not existing_notification:
                    if NotificationService.notify_excessive_hours(entry):
                        notifications_sent += 1
            
            logger.info(f"Verificación de exceso de horas completada. Notificaciones enviadas: {notifications_sent}")
            return notifications_sent
            
        except Exception as e:
            logger.error(f"Error en verificación de exceso de horas: {e}")
            return 0
    
    @staticmethod
    def get_user_notifications_summary(user):
        """
        Obtener resumen de notificaciones para un usuario
        """
        try:
            notifications = Notification.objects.filter(user=user)
            
            return {
                'total': notifications.count(),
                'unread': notifications.filter(read=False).count(),
                'recent': notifications.order_by('-created_at')[:5],
                'by_type': notifications.values('notification_type').annotate(
                    count=models.Count('id')
                ).order_by('-count')
            }
            
        except Exception as e:
            logger.error(f"Error obteniendo resumen de notificaciones: {e}")
            return {
                'total': 0,
                'unread': 0,
                'recent': [],
                'by_type': []
            }
    
    @staticmethod
    def mark_notification_as_read(notification_id, user):
        """
        Marcar una notificación como leída
        """
        try:
            notification = Notification.objects.get(id=notification_id, user=user)
            notification.read = True
            notification.read_timestamp = timezone.now()
            notification.save()
            
            logger.info(f"Notificación {notification_id} marcada como leída por {user.username}")
            return True
            
        except Notification.DoesNotExist:
            logger.warning(f"Notificación {notification_id} no encontrada para {user.username}")
            return False
        except Exception as e:
            logger.error(f"Error marcando notificación como leída: {e}")
            return False
    
    @staticmethod
    def mark_all_as_read(user):
        """
        Marcar todas las notificaciones de un usuario como leídas
        """
        try:
            updated = Notification.objects.filter(
                user=user, 
                read=False
            ).update(
                read=True,
                read_timestamp=timezone.now()
            )
            
            logger.info(f"{updated} notificaciones marcadas como leídas para {user.username}")
            return updated
            
        except Exception as e:
            logger.error(f"Error marcando todas las notificaciones como leídas: {e}")
            return 0


class ExcessiveHoursChecker:
    """
    Clase especializada para verificar y manejar exceso de horas
    """
    
    @staticmethod
    def check_entry_for_excessive_hours(room_entry):
        """
        Verificar si una entrada específica excede las 8 horas
        """
        try:
            from rooms.services import RoomEntryBusinessLogic
            duration_info = RoomEntryBusinessLogic.calculate_session_duration(room_entry)
            total_hours = duration_info.get('total_duration_hours', 0)
            
            return {
                'exceeds_limit': total_hours > 8,
                'total_hours': total_hours,
                'excess_hours': max(0, total_hours - 8),
                'is_critical': total_hours > 12,  # Más de 12 horas es crítico
                'warning_threshold': total_hours > 7,  # Aviso a las 7 horas
            }
            
        except Exception as e:
            logger.error(f"Error verificando exceso de horas: {e}")
            return {
                'exceeds_limit': False,
                'total_hours': 0,
                'excess_hours': 0,
                'is_critical': False,
                'warning_threshold': False,
            }
    
    @staticmethod
    def get_monitors_with_excessive_hours():
        """
        Obtener lista de monitores que actualmente exceden las 8 horas
        """
        try:
            active_entries = RoomEntry.objects.filter(exit_time__isnull=True)
            excessive_monitors = []
            
            for entry in active_entries:
                check_result = ExcessiveHoursChecker.check_entry_for_excessive_hours(entry)
                
                if check_result['exceeds_limit']:
                    excessive_monitors.append({
                        'entry_id': entry.id,
                        'user': entry.user,
                        'room': entry.room,
                        'entry_time': entry.entry_time,
                        'total_hours': check_result['total_hours'],
                        'excess_hours': check_result['excess_hours'],
                        'is_critical': check_result['is_critical']
                    })
            
            return excessive_monitors
            
        except Exception as e:
            logger.error(f"Error obteniendo monitores con exceso de horas: {e}")
            return []

from django.db import models
from django.utils import timezone
from django.conf import settings
from django.core.mail import send_mail
from datetime import timedelta
from .models import Notification
from rooms.models import RoomEntry
from users.models import User
import logging

logger = logging.getLogger(__name__)


class NotificationService:
    """
    Servicio para manejar la lógica de negocio de notificaciones
    """
    
    @staticmethod
    def create_notification(user, notification_type, title, message, related_object_id=None):
        """
        Crear una nueva notificación
        """
        try:
            notification = Notification.objects.create(
                user=user,
                notification_type=notification_type,
                title=title,
                message=message,
                related_object_id=related_object_id
            )
            logger.info(f"Notificación creada: {notification_type} para {user.username}")
            return notification
        except Exception as e:
            logger.error(f"Error creando notificación: {e}")
            return None
    
    @staticmethod
    def notify_excessive_hours(room_entry):
        """
        Crear notificaciones de exceso de horas para administradores
        cuando un monitor excede las 8 horas continuas
        """
        try:
            # Calcular duración actual
            from rooms.services import RoomEntryBusinessLogic
            duration_info = RoomEntryBusinessLogic.calculate_session_duration(room_entry)
            # Para entradas activas, usar current_duration_hours; para completadas, usar total_duration_hours
            total_hours = duration_info.get('total_duration_hours', 0) or duration_info.get('current_duration_hours', 0)
            
            if total_hours > 8:
                # Obtener todos los administradores
                admins = User.objects.filter(role='admin', is_active=True)
                
                if not admins.exists():
                    logger.warning(f"No hay administradores para notificar exceso de horas de {room_entry.user.username}")
                    return False
                
                excess_hours = round(total_hours - 8, 2)
                
                for admin in admins:
                    title = f"⚠️ Exceso de Horas - {room_entry.user.get_full_name()}"
                    message = (
                        f"El monitor {room_entry.user.get_full_name()} ({room_entry.user.username}) "
                        f"ha excedido las 8 horas continuas en la sala {room_entry.room.name}.\n\n"
                        f"⏰ Duración actual: {total_hours:.1f} horas\n"
                        f"⚠️ Exceso: {excess_hours:.1f} horas\n"
                        f"🏢 Sala: {room_entry.room.name}\n"
                        f"📅 Desde: {room_entry.entry_time.strftime('%d/%m/%Y %H:%M')}"
                    )
                    
                    # Crear notificación
                    NotificationService.create_notification(
                        user=admin,
                        notification_type=Notification.EXCESSIVE_HOURS,
                        title=title,
                        message=message,
                        related_object_id=room_entry.id
                    )
                    
                    # Enviar email de alerta
                    NotificationService.send_excessive_hours_email(admin, room_entry, total_hours, excess_hours)
                
                logger.warning(f"Notificaciones de exceso de horas enviadas para {room_entry.user.username}: {total_hours:.1f}h")
                return True
            else:
                logger.info(f"No se exceden las 8 horas para {room_entry.user.username}: {total_hours:.1f}h")
                return False
                
        except Exception as e:
            logger.error(f"Error notificando exceso de horas: {e}")
            return False
    
    @staticmethod
    def send_excessive_hours_email(admin, room_entry, total_hours, excess_hours):
        """
        Enviar email de alerta por exceso de horas a administradores
        """
        try:
            subject = f'[DS2] ALERTA: Exceso de Horas - {room_entry.user.get_full_name()}'
            
            # Texto plano
            text_message = (
                f"ALERTA DE EXCESO DE HORAS\n\n"
                f"El monitor {room_entry.user.get_full_name()} ({room_entry.user.username}) "
                f"ha excedido las 8 horas continuas en la sala {room_entry.room.name}.\n\n"
                f"DATOS DEL USUARIO:\n"
                f"• Nombre: {room_entry.user.get_full_name()}\n"
                f"• Username: {room_entry.user.username}\n"
                f"• Email: {room_entry.user.email}\n"
                f"• Identificación: {room_entry.user.identification}\n"
                f"• Teléfono: {room_entry.user.phone}\n\n"
                f"DATOS DE LA SESIÓN:\n"
                f"• Sala: {room_entry.room.name}\n"
                f"• Hora de entrada: {room_entry.entry_time.strftime('%d/%m/%Y %H:%M')}\n"
                f"• Duración actual: {total_hours:.1f} horas\n"
                f"• Exceso: {excess_hours:.1f} horas\n\n"
                f"Esta es una alerta automática del sistema DS2."
            )
            
            # HTML con card profesional
            html_message = f"""
<!doctype html>
<html>
  <body style="font-family:Segoe UI,Arial,sans-serif;background:#f6f7f9;padding:24px;">
    <div style="max-width:600px;margin:0 auto;background:#ffffff;border-radius:12px;box-shadow:0 6px 24px rgba(0,0,0,.08);overflow:hidden;">
      <div style="padding:20px 24px;border-bottom:1px solid #eef2f7;background:#dc2626;">
        <h2 style="margin:0;color:#ffffff;">⚠️ ALERTA: Exceso de Horas</h2>
        <p style="margin:6px 0 0;color:#fecaca;">Monitor ha excedido las 8 horas continuas</p>
      </div>
      <div style="padding:20px 24px;">
        <div style="background:#fef2f2;border:1px solid #fecaca;border-radius:8px;padding:16px;margin-bottom:20px;">
          <h3 style="margin:0 0 12px;color:#dc2626;">Datos del Usuario</h3>
          <div style="display:grid;grid-template-columns:1fr 1fr;gap:12px;">
            <div>
              <strong>Nombre:</strong><br>
              <span style="color:#374151;">{room_entry.user.get_full_name()}</span>
            </div>
            <div>
              <strong>Username:</strong><br>
              <span style="color:#374151;">{room_entry.user.username}</span>
            </div>
            <div>
              <strong>Email:</strong><br>
              <span style="color:#374151;">{room_entry.user.email}</span>
            </div>
            <div>
              <strong>Identificación:</strong><br>
              <span style="color:#374151;">{room_entry.user.identification}</span>
            </div>
            <div>
              <strong>Teléfono:</strong><br>
              <span style="color:#374151;">{room_entry.user.phone}</span>
            </div>
            <div>
              <strong>Sala:</strong><br>
              <span style="color:#374151;">{room_entry.room.name}</span>
            </div>
          </div>
        </div>
        
        <div style="background:#fef3c7;border:1px solid #f59e0b;border-radius:8px;padding:16px;margin-bottom:20px;">
          <h3 style="margin:0 0 12px;color:#d97706;">Datos de la Sesión</h3>
          <div style="display:grid;grid-template-columns:1fr 1fr;gap:12px;">
            <div>
              <strong>Hora de entrada:</strong><br>
              <span style="color:#374151;">{room_entry.entry_time.strftime('%d/%m/%Y %H:%M')}</span>
            </div>
            <div>
              <strong>Duración actual:</strong><br>
              <span style="color:#dc2626;font-weight:bold;">{total_hours:.1f} horas</span>
            </div>
            <div>
              <strong>Exceso:</strong><br>
              <span style="color:#dc2626;font-weight:bold;">{excess_hours:.1f} horas</span>
            </div>
            <div>
              <strong>Estado:</strong><br>
              <span style="color:#dc2626;font-weight:bold;">⚠️ EXCESO DETECTADO</span>
            </div>
          </div>
        </div>
        
        <div style="background:#f3f4f6;border-radius:8px;padding:16px;text-align:center;">
          <p style="margin:0;color:#6b7280;font-size:14px;">
            Esta es una alerta automática del sistema DS2.<br>
            Se recomienda contactar al monitor para verificar su estado.
          </p>
        </div>
      </div>
    </div>
    <p style="text-align:center;color:#9ca3af;font-size:12px;margin-top:16px;">DS2 • Sistema de Monitoreo</p>
  </body>
</html>
"""
            
            send_mail(
                subject=subject,
                message=text_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[admin.email],
                html_message=html_message,
                fail_silently=True,
            )
            
            logger.info(f"Email de exceso de horas enviado a {admin.email}")
            
        except Exception as e:
            logger.error(f"Error enviando email de exceso de horas: {e}")
    
    @staticmethod
    def notify_room_entry(room_entry, is_entry=True):
        """
        Notificar entrada o salida de sala
        """
        try:
            action = "entró" if is_entry else "salió"
            emoji = "🚪" if is_entry else "🚪"
            
            title = f"{emoji} {room_entry.user.get_full_name()} {action} a la sala"
            message = (
                f"El monitor {room_entry.user.get_full_name()} {action} "
                f"a la sala {room_entry.room.name}.\n\n"
                f"🏢 Sala: {room_entry.room.name}\n"
                f"👤 Monitor: {room_entry.user.get_full_name()}\n"
                f"📅 Hora: {room_entry.entry_time.strftime('%d/%m/%Y %H:%M')}"
            )
            
            # Notificar a administradores
            admins = User.objects.filter(role='admin', is_active=True)
            for admin in admins:
                NotificationService.create_notification(
                    user=admin,
                    notification_type=Notification.ROOM_ENTRY if is_entry else Notification.ROOM_EXIT,
                    title=title,
                    message=message,
                    related_object_id=room_entry.id
                )
            
            logger.info(f"Notificación de {action} enviada para {room_entry.user.username}")
            return True
            
        except Exception as e:
            logger.error(f"Error notificando entrada/salida: {e}")
            return False
    
    @staticmethod
    def check_and_notify_excessive_hours():
        """
        Verificar todas las entradas activas y notificar exceso de horas
        Esta función se puede llamar periódicamente (cada hora)
        """
        try:
            # Obtener todas las entradas activas
            active_entries = RoomEntry.objects.filter(exit_time__isnull=True)
            notifications_sent = 0
            
            for entry in active_entries:
                # Verificar si ya se envió notificación para esta entrada
                existing_notification = Notification.objects.filter(
                    notification_type=Notification.EXCESSIVE_HOURS,
                    related_object_id=entry.id,
                    created_at__gte=timezone.now() - timedelta(hours=1)  # No duplicar en 1 hora
                ).exists()
                
                if not existing_notification:
                    if NotificationService.notify_excessive_hours(entry):
                        notifications_sent += 1
            
            logger.info(f"Verificación de exceso de horas completada. Notificaciones enviadas: {notifications_sent}")
            return notifications_sent
            
        except Exception as e:
            logger.error(f"Error en verificación de exceso de horas: {e}")
            return 0
    
    @staticmethod
    def get_user_notifications_summary(user):
        """
        Obtener resumen de notificaciones para un usuario
        """
        try:
            notifications = Notification.objects.filter(user=user)
            
            return {
                'total': notifications.count(),
                'unread': notifications.filter(read=False).count(),
                'recent': notifications.order_by('-created_at')[:5],
                'by_type': notifications.values('notification_type').annotate(
                    count=models.Count('id')
                ).order_by('-count')
            }
            
        except Exception as e:
            logger.error(f"Error obteniendo resumen de notificaciones: {e}")
            return {
                'total': 0,
                'unread': 0,
                'recent': [],
                'by_type': []
            }
    
    @staticmethod
    def mark_notification_as_read(notification_id, user):
        """
        Marcar una notificación como leída
        """
        try:
            notification = Notification.objects.get(id=notification_id, user=user)
            notification.read = True
            notification.read_timestamp = timezone.now()
            notification.save()
            
            logger.info(f"Notificación {notification_id} marcada como leída por {user.username}")
            return True
            
        except Notification.DoesNotExist:
            logger.warning(f"Notificación {notification_id} no encontrada para {user.username}")
            return False
        except Exception as e:
            logger.error(f"Error marcando notificación como leída: {e}")
            return False
    
    @staticmethod
    def mark_all_as_read(user):
        """
        Marcar todas las notificaciones de un usuario como leídas
        """
        try:
            updated = Notification.objects.filter(
                user=user, 
                read=False
            ).update(
                read=True,
                read_timestamp=timezone.now()
            )
            
            logger.info(f"{updated} notificaciones marcadas como leídas para {user.username}")
            return updated
            
        except Exception as e:
            logger.error(f"Error marcando todas las notificaciones como leídas: {e}")
            return 0


class ExcessiveHoursChecker:
    """
    Clase especializada para verificar y manejar exceso de horas
    """
    
    @staticmethod
    def check_entry_for_excessive_hours(room_entry):
        """
        Verificar si una entrada específica excede las 8 horas
        """
        try:
            from rooms.services import RoomEntryBusinessLogic
            duration_info = RoomEntryBusinessLogic.calculate_session_duration(room_entry)
            total_hours = duration_info.get('total_duration_hours', 0)
            
            return {
                'exceeds_limit': total_hours > 8,
                'total_hours': total_hours,
                'excess_hours': max(0, total_hours - 8),
                'is_critical': total_hours > 12,  # Más de 12 horas es crítico
                'warning_threshold': total_hours > 7,  # Aviso a las 7 horas
            }
            
        except Exception as e:
            logger.error(f"Error verificando exceso de horas: {e}")
            return {
                'exceeds_limit': False,
                'total_hours': 0,
                'excess_hours': 0,
                'is_critical': False,
                'warning_threshold': False,
            }
    
    @staticmethod
    def get_monitors_with_excessive_hours():
        """
        Obtener lista de monitores que actualmente exceden las 8 horas
        """
        try:
            active_entries = RoomEntry.objects.filter(exit_time__isnull=True)
            excessive_monitors = []
            
            for entry in active_entries:
                check_result = ExcessiveHoursChecker.check_entry_for_excessive_hours(entry)
                
                if check_result['exceeds_limit']:
                    excessive_monitors.append({
                        'entry_id': entry.id,
                        'user': entry.user,
                        'room': entry.room,
                        'entry_time': entry.entry_time,
                        'total_hours': check_result['total_hours'],
                        'excess_hours': check_result['excess_hours'],
                        'is_critical': check_result['is_critical']
                    })
            
            return excessive_monitors
            
        except Exception as e:
            logger.error(f"Error obteniendo monitores con exceso de horas: {e}")
            return []