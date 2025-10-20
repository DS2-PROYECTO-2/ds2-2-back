from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from django.core.mail import send_mail
from .models import EquipmentReport
from notifications.services import NotificationService
from notifications.models import Notification
from users.models import User
from users.email_utils import send_email_unified
import logging

logger = logging.getLogger(__name__)


@receiver(post_save, sender=EquipmentReport)
def notify_admins_on_equipment_report(sender, instance, created, **kwargs):
    """
    Señal que se ejecuta cuando se crea un nuevo reporte de equipo.
    Notifica a todos los administradores via notificación y email.
    """
    if created:  # Solo cuando se crea un nuevo reporte
        try:
            # Obtener todos los administradores activos
            admins = User.objects.filter(role='admin', is_active=True)
            
            if not admins.exists():
                logger.warning("No hay administradores para notificar sobre reporte de equipo")
                return
            
            # Información del reporte
            equipment = instance.equipment
            reporter = instance.reported_by
            issue_description = instance.issue_description
            
            # Crear notificaciones para cada administrador
            for admin in admins:
                # Crear notificación en el sistema
                title = f"Reporte de Falla - {equipment.name}"
                message = (
                    f"El monitor {reporter.get_full_name()} reportó una falla en el equipo {equipment.name}.\n\n"
                    f"🏢 Sala: {equipment.room.name}\n"
                    f"🔧 Equipo: {equipment.name} ({equipment.serial_number})\n"
                    f"👤 Reportado por: {reporter.get_full_name()}\n"
                    f"📝 Descripción: {issue_description}\n"
                    f"📅 Fecha: {instance.reported_date.strftime('%d/%m/%Y %H:%M')}"
                )
                
                # Crear notificación
                NotificationService.create_notification(
                    user=admin,
                    notification_type=Notification.EQUIPMENT_REPORT,
                    title=title,
                    message=message,
                    related_object_id=instance.id
                )
                
                # Enviar email de notificación
                send_equipment_report_email(admin, instance)
            
            logger.info(f"Notificaciones de reporte de equipo enviadas para {equipment.name}")
            
        except Exception as e:
            logger.error(f"Error notificando reporte de equipo: {e}")


def send_equipment_report_email(admin, equipment_report):
    """
    Enviar email de notificación de reporte de equipo a administradores
    """
    try:
        equipment = equipment_report.equipment
        reporter = equipment_report.reported_by
        
        subject = f'[DS2] Reporte de Falla - {equipment.name}'
        
        # Texto plano
        text_message = (
            f"REPORTE DE FALLA DE EQUIPO\n\n"
            f"Se ha reportado una falla en el equipo {equipment.name}.\n\n"
            f"DATOS DEL EQUIPO:\n"
            f"• Equipo: {equipment.name}\n"
            f"• Número de Serie: {equipment.serial_number}\n"
            f"• Sala: {equipment.room.name}\n"
            f"• Estado Actual: {equipment.get_status_display()}\n\n"
            f"DATOS DEL REPORTE:\n"
            f"• Reportado por: {reporter.get_full_name()}\n"
            f"• Username: {reporter.username}\n"
            f"• Email: {reporter.email}\n"
            f"• Teléfono: {reporter.phone}\n"
            f"• Fecha del reporte: {equipment_report.reported_date.strftime('%d/%m/%Y %H:%M')}\n\n"
            f"DESCRIPCIÓN DEL PROBLEMA:\n"
            f"{equipment_report.issue_description}\n\n"
            f"Por favor, revise el reporte en el sistema DS2."
        )
        
        # HTML con card profesional
        html_message = f"""
<!doctype html>
<html>
  <body style="font-family:Segoe UI,Arial,sans-serif;background:#f6f7f9;padding:24px;">
    <div style="max-width:600px;margin:0 auto;background:#ffffff;border-radius:12px;box-shadow:0 6px 24px rgba(0,0,0,.08);overflow:hidden;">
      <div style="padding:20px 24px;border-bottom:1px solid #eef2f7;background:#f59e0b;">
        <h2 style="margin:0;color:#ffffff;">Reporte de Falla de Equipo</h2>
        <p style="margin:6px 0 0;color:#fef3c7;">Nuevo reporte de problema técnico</p>
      </div>
      <div style="padding:20px 24px;">
        <div style="background:#fef3c7;border:1px solid #f59e0b;border-radius:8px;padding:16px;margin-bottom:20px;">
          <h3 style="margin:0 0 12px;color:#d97706;">Datos del Equipo</h3>
          <div style="display:grid;grid-template-columns:1fr 1fr;gap:12px;">
            <div>
              <strong>Equipo:</strong><br>
              <span style="color:#374151;">{equipment.name}</span>
            </div>
            <div>
              <strong>Número de Serie:</strong><br>
              <span style="color:#374151;">{equipment.serial_number}</span>
            </div>
            <div>
              <strong>Sala:</strong><br>
              <span style="color:#374151;">{equipment.room.name}</span>
            </div>
            <div>
              <strong>Estado Actual:</strong><br>
              <span style="color:#374151;">{equipment.get_status_display()}</span>
            </div>
          </div>
        </div>
        
        <div style="background:#fef2f2;border:1px solid #fecaca;border-radius:8px;padding:16px;margin-bottom:20px;">
          <h3 style="margin:0 0 12px;color:#dc2626;">Datos del Reporte</h3>
          <div style="display:grid;grid-template-columns:1fr 1fr;gap:12px;">
            <div>
              <strong>Reportado por:</strong><br>
              <span style="color:#374151;">{reporter.get_full_name()}</span>
            </div>
            <div>
              <strong>Username:</strong><br>
              <span style="color:#374151;">{reporter.username}</span>
            </div>
            <div>
              <strong>Email:</strong><br>
              <span style="color:#374151;">{reporter.email}</span>
            </div>
            <div>
              <strong>Teléfono:</strong><br>
              <span style="color:#374151;">{reporter.phone}</span>
            </div>
            <div>
              <strong>Fecha del reporte:</strong><br>
              <span style="color:#374151;">{equipment_report.reported_date.strftime('%d/%m/%Y %H:%M')}</span>
            </div>
          </div>
        </div>
        
        <div style="background:#f3f4f6;border-radius:8px;padding:16px;margin-bottom:20px;">
          <h3 style="margin:0 0 12px;color:#374151;">Descripción del Problema</h3>
          <div style="background:#ffffff;border:1px solid #d1d5db;border-radius:6px;padding:12px;">
            <p style="margin:0;color:#374151;white-space:pre-line;">{equipment_report.issue_description}</p>
          </div>
        </div>
        
        <div style="background:#dbeafe;border:1px solid #3b82f6;border-radius:8px;padding:16px;text-align:center;">
          <p style="margin:0;color:#1e40af;font-size:14px;">
            <strong>Acción Requerida:</strong> Por favor, revise el reporte en el sistema DS2 y tome las medidas necesarias.
          </p>
        </div>
      </div>
    </div>
    <p style="text-align:center;color:#9ca3af;font-size:12px;margin-top:16px;">DS2 • Sistema de Monitoreo</p>
  </body>
</html>
"""
        
        send_email_unified(
            to=admin.email,
            subject=subject,
            text_content=text_message,
            html_content=html_message
        )
        
        logger.info(f"Email de reporte de equipo enviado a {admin.email}")
        
    except Exception as e:
        logger.error(f"Error enviando email de reporte de equipo: {e}")
