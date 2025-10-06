"""
Sistema de tareas automáticas para verificación de cumplimiento de turnos
Tarea 2: Notificaciones automáticas a administradores
"""
from django.utils import timezone
from datetime import timedelta
from .services import ScheduleComplianceMonitor, ScheduleValidationService
from .models import Schedule
import logging

logger = logging.getLogger(__name__)


def check_and_notify_overdue_schedules():
    """
    Verificar turnos vencidos y enviar notificaciones automáticas
    Se ejecuta cada 15 minutos para verificar incumplimientos
    """
    try:
        logger.info("Iniciando verificación de turnos vencidos...")
        
        # Verificar turnos vencidos
        results = ScheduleComplianceMonitor.check_overdue_schedules()
        
        logger.info(f"Verificación completada: {results['checked_schedules']} turnos verificados, "
                   f"{results['notifications_sent']} notificaciones enviadas")
        
        # Si hay turnos no conformes, registrar en log
        if results['non_compliant_schedules'] > 0:
            logger.warning(f"Se encontraron {results['non_compliant_schedules']} turnos no conformes")
            
            for detail in results['details']:
                if detail['notification_sent']:
                    logger.warning(f"Notificación enviada: Turno {detail['schedule_id']} - "
                                 f"{detail['monitor']} en {detail['room']}")
        
        return results
        
    except Exception as e:
        logger.error(f"Error en verificación de turnos: {str(e)}")
        return None


def monitor_active_schedules():
    """
    Monitorear turnos activos que están cerca del período de gracia
    """
    try:
        now = timezone.now()
        # Turnos que empezaron hace entre 15 y 25 minutos
        warning_time_start = now - timedelta(minutes=25)
        warning_time_end = now - timedelta(minutes=15)
        
        at_risk_schedules = Schedule.objects.filter(
            status=Schedule.ACTIVE,
            start_datetime__gte=warning_time_start,
            start_datetime__lte=warning_time_end
        ).select_related('user', 'room')
        
        potential_issues = []
        
        for schedule in at_risk_schedules:
            compliance_info = ScheduleValidationService.check_schedule_compliance(schedule)
            
            if compliance_info['compliance_status'] == 'pending':
                potential_issues.append({
                    'schedule_id': schedule.id,
                    'monitor': schedule.user.get_full_name(),
                    'room': schedule.room.name,
                    'start_time': schedule.start_datetime,
                    'minutes_since_start': (now - schedule.start_datetime).total_seconds() / 60
                })
        
        if potential_issues:
            logger.info(f"Turnos en riesgo de incumplimiento: {len(potential_issues)}")
            
        return potential_issues
        
    except Exception as e:
        logger.error(f"Error monitoreando turnos activos: {str(e)}")
        return []


def daily_compliance_summary():
    """
    Generar resumen diario de cumplimiento para administradores
    """
    try:
        from users.models import User
        from notifications.models import Notification
        
        now = timezone.now()
        today = now.date()
        
        # Obtener turnos del día
        today_schedules = Schedule.objects.filter(
            start_datetime__date=today,
            status=Schedule.ACTIVE
        ).select_related('user', 'room')
        
        if not today_schedules.exists():
            logger.info("No hay turnos programados para hoy")
            return
        
        # Calcular estadísticas
        total_schedules = today_schedules.count()
        compliant_count = 0
        non_compliant_count = 0
        pending_count = 0
        
        for schedule in today_schedules:
            compliance_info = ScheduleValidationService.check_schedule_compliance(schedule)
            
            if compliance_info['compliance_status'] == 'compliant':
                compliant_count += 1
            elif compliance_info['compliance_status'] in ['non_compliant', 'late_compliance']:
                non_compliant_count += 1
            else:
                pending_count += 1
        
        # Enviar resumen a administradores si hay incumplimientos
        if non_compliant_count > 0:
            admins = User.objects.filter(role='admin', is_verified=True)
            
            title = f"Resumen de cumplimiento diario - {today.strftime('%d/%m/%Y')}"
            message = (
                f"📊 RESUMEN DE CUMPLIMIENTO\n\n"
                f"📅 Fecha: {today.strftime('%d/%m/%Y')}\n"
                f"📋 Total de turnos: {total_schedules}\n"
                f"✅ Cumplidos: {compliant_count}\n"
                f"❌ No cumplidos: {non_compliant_count}\n"
                f"⏳ Pendientes: {pending_count}\n\n"
                f"Tasa de cumplimiento: {(compliant_count/total_schedules)*100:.1f}%"
            )
            
            for admin in admins:
                Notification.objects.create(
                    user=admin,
                    title=title,
                    message=message,
                    notification_type='schedule_non_compliance'
                )
        
        logger.info(f"Resumen diario generado: {compliant_count}/{total_schedules} turnos cumplidos")
        
    except Exception as e:
        logger.error(f"Error generando resumen diario: {str(e)}")