from django.utils import timezone
from django.db import transaction
from django.core.exceptions import ValidationError
from django.db.models import Q
from datetime import timedelta
from .models import Schedule
from rooms.models import RoomEntry
from notifications.models import Notification
from users.models import User


class ScheduleValidationService:
    """
    Lógica de negocio para validaciones de turnos y calendarios
    Tarea 2: Backend: Lógica y validaciones para Integración con calendarios
    """
    
    @staticmethod
    def validate_schedule_conflicts(user, room, start_datetime, end_datetime, exclude_schedule_id=None):
        """
        Validar conflictos de horario para usuario y sala
        Tarea 2: Prevenir turnos superpuestos del mismo monitor Y sala ocupada por otro monitor
        """
        # 1. Validar conflictos del mismo usuario
        user_conflict_query = Q(
            user=user,
            status=Schedule.ACTIVE
        ) & (
            Q(start_datetime__lt=end_datetime, end_datetime__gt=start_datetime)
        )
        
        # 2. Validar conflictos de sala (otro monitor en la misma sala)
        room_conflict_query = Q(
            room=room,
            status=Schedule.ACTIVE
        ) & (
            Q(start_datetime__lt=end_datetime, end_datetime__gt=start_datetime)
        )
        
        # Si estamos editando un turno, excluirlo de la búsqueda
        if exclude_schedule_id:
            user_conflict_query &= ~Q(id=exclude_schedule_id)
            room_conflict_query &= ~Q(id=exclude_schedule_id)
        
        # Verificar conflictos del usuario
        user_conflicts = Schedule.objects.filter(user_conflict_query).select_related('room')
        
        # Verificar conflictos de sala
        room_conflicts = Schedule.objects.filter(room_conflict_query).select_related('user')
        
        if user_conflicts.exists() or room_conflicts.exists():
            error_message = ""
            
            # Procesar conflictos del usuario
            if user_conflicts.exists():
                error_message = f'El monitor {user.get_full_name()} ya tiene turnos asignados que se superponen con el horario propuesto.'
            
            # Procesar conflictos de sala (más crítico)
            if room_conflicts.exists():
                conflicting_monitor = room_conflicts.first().user.get_full_name()
                error_message = f'La sala {room.name} ({room.code}) ya está ocupada por {conflicting_monitor} en el horario solicitado. No se permiten dos monitores en la misma sala simultáneamente.'
            
            raise ValidationError(error_message)
        
        return True
    
    @staticmethod
    def _get_conflict_type(new_start, new_end, existing_start, existing_end):
        """Determinar el tipo de conflicto entre turnos"""
        if new_start <= existing_start and new_end >= existing_end:
            return 'complete_overlap'  # El nuevo turno abarca completamente el existente
        elif new_start >= existing_start and new_end <= existing_end:
            return 'contained'  # El nuevo turno está contenido en el existente
        elif new_start < existing_end and new_end > existing_end:
            return 'end_overlap'  # El nuevo turno se superpone al final del existente
        elif new_start < existing_start and new_end > existing_start:
            return 'start_overlap'  # El nuevo turno se superpone al inicio del existente
        else:
            return 'partial_overlap'  # Superposición parcial
    
    @staticmethod
    def validate_room_access_permission(user, room, entry_time=None):
        """
        Validar que el usuario (monitor) solo pueda entrar en una sala si tiene un turno 
        disponible en el horario en el cual está ingresando.
        HU: "El usuario (monitor) solo podrá entrar en una sala si tiene un turno disponible 
        en el horario en el cual está ingresando"
        """
        if not entry_time:
            entry_time = timezone.now()
        
        # Buscar turnos activos que cubran el momento de entrada
        valid_schedules = Schedule.objects.filter(
            user=user,
            room=room,
            status=Schedule.ACTIVE,
            start_datetime__lte=entry_time,
            end_datetime__gte=entry_time
        )
        
        if not valid_schedules.exists():
            # Buscar turnos próximos (dentro de 20 minutos) para dar información útil
            upcoming_schedules = Schedule.objects.filter(
                user=user,
                room=room,
                status=Schedule.ACTIVE,
                start_datetime__gt=entry_time,
                start_datetime__lte=entry_time + timedelta(minutes=20)
            ).order_by('start_datetime')
            
            # Buscar turnos en otras salas en este momento
            other_room_schedules = Schedule.objects.filter(
                user=user,
                status=Schedule.ACTIVE,
                start_datetime__lte=entry_time,
                end_datetime__gte=entry_time
            ).exclude(room=room).select_related('room')
            
            error_details = {
                'access_denied': f'No tienes un turno activo para la sala {room.name} ({room.code}) en este momento.',
                'entry_time': entry_time,
                'room': room.name,
                'room_code': room.code
            }
            
            if upcoming_schedules.exists():
                next_schedule = upcoming_schedules.first()
                minutes_until = int((next_schedule.start_datetime - entry_time).total_seconds() / 60)
                error_details['upcoming_schedule'] = {
                    'start_datetime': next_schedule.start_datetime,
                    'minutes_until': minutes_until,
                    'message': f'Tu próximo turno en esta sala comienza en {minutes_until} minutos.'
                }
            
            if other_room_schedules.exists():
                current_schedule = other_room_schedules.first()
                error_details['current_schedule_different_room'] = {
                    'room': current_schedule.room.name,
                    'room_code': current_schedule.room.code,
                    'start_datetime': current_schedule.start_datetime,
                    'end_datetime': current_schedule.end_datetime,
                    'message': f'Actualmente tienes un turno activo en {current_schedule.room.name}.'
                }
            
            raise ValidationError("Acceso denegado: sin turno activo válido")
        
        return {
            'access_granted': True,
            'active_schedule': valid_schedules.first(),
            'message': 'Acceso autorizado por turno activo'
        }
    
    @staticmethod
    def check_schedule_compliance(schedule):
        """
        Comparar turnos asignados con registros de ingreso/salida.
        HU: "Comparar turnos asignados con registros de ingreso/salida"
        """
        now = timezone.now()
        
        # Solo verificar turnos que ya deberían haber comenzado
        if schedule.start_datetime > now:
            return {
                'compliance_status': 'pending',
                'message': 'Turno aún no ha comenzado',
                'schedule_id': schedule.id
            }
        
        # Buscar registros de entrada durante el turno (con margen de 20 minutos antes)
        grace_period_start = schedule.start_datetime - timedelta(minutes=20)
        grace_period_end = schedule.end_datetime + timedelta(minutes=20)
        
        room_entries = RoomEntry.objects.filter(
            user=schedule.user,
            room=schedule.room,
            entry_time__gte=grace_period_start,
            entry_time__lte=grace_period_end
        ).order_by('entry_time')
        
        if not room_entries.exists():
            # No hay registros de entrada
            minutes_late = int((now - schedule.start_datetime).total_seconds() / 60) if now > schedule.start_datetime else 0
            
            return {
                'compliance_status': 'non_compliant',
                'message': 'Monitor no se presentó al turno',
                'schedule_id': schedule.id,
                'minutes_late': minutes_late,
                'grace_period_expired': minutes_late > 20,
                'should_notify_admin': minutes_late > 20
            }
        
        # Hay registros de entrada, verificar puntualidad
        first_entry = room_entries.first()
        entry_delay = first_entry.entry_time - schedule.start_datetime
        minutes_delay = int(entry_delay.total_seconds() / 60)
        
        if minutes_delay <= 20:  # Dentro del período de gracia
            return {
                'compliance_status': 'compliant',
                'message': 'Monitor cumplió con el turno',
                'schedule_id': schedule.id,
                'entry_time': first_entry.entry_time,
                'minutes_delay': max(0, minutes_delay),
                'within_grace_period': True
            }
        else:
            return {
                'compliance_status': 'late_compliance',
                'message': 'Monitor llegó tarde pero se presentó',
                'schedule_id': schedule.id,
                'entry_time': first_entry.entry_time,
                'minutes_delay': minutes_delay,
                'within_grace_period': False,
                'should_notify_admin': True
            }
    
    @staticmethod
    def notify_admin_schedule_non_compliance(schedule, compliance_info):
        """
        Generar notificación al admin cuando un turno no se cumple.
        HU: "Generar notificación al admin cuando un turno no se cumple"
        """
        if not compliance_info.get('should_notify_admin', False):
            return {
                'notification_sent': False,
                'reason': 'No se requiere notificación'
            }
        
        admins = User.objects.filter(role='admin', is_verified=True)
        
        if not admins.exists():
            return {
                'notification_sent': False,
                'reason': 'No hay administradores verificados disponibles'
            }
        
        # Construir mensaje según el tipo de incumplimiento
        if compliance_info['compliance_status'] == 'non_compliant':
            title = "Monitor no se presentó a su turno"
            message = (
                f"🚨 INCUMPLIMIENTO DE TURNO\n\n"
                f"El monitor {schedule.user.get_full_name()} ({schedule.user.username}) "
                f"no se presentó a su turno asignado.\n\n"
                f"📋 Detalles del turno:\n"
                f"• Sala: {schedule.room.name} ({schedule.room.code})\n"
                f"• Fecha: {schedule.start_datetime.strftime('%d/%m/%Y')}\n"
                f"• Horario: {schedule.start_datetime.strftime('%H:%M')} - {schedule.end_datetime.strftime('%H:%M')}\n"
                f"• Tiempo transcurrido: {compliance_info['minutes_late']} minutos\n"
                f"• Estado: Sin registro de entrada"
            )
        elif compliance_info['compliance_status'] == 'late_compliance':
            title = "Monitor llegó tarde a su turno"
            message = (
                f"⚠️ RETRASO EN TURNO\n\n"
                f"El monitor {schedule.user.get_full_name()} ({schedule.user.username}) "
                f"llegó tarde a su turno asignado.\n\n"
                f"📋 Detalles del turno:\n"
                f"• Sala: {schedule.room.name} ({schedule.room.code})\n"
                f"• Fecha: {schedule.start_datetime.strftime('%d/%m/%Y')}\n"
                f"• Horario programado: {schedule.start_datetime.strftime('%H:%M')} - {schedule.end_datetime.strftime('%H:%M')}\n"
                f"• Hora de llegada: {compliance_info['entry_time'].strftime('%H:%M')}\n"
                f"• Retraso: {compliance_info['minutes_delay']} minutos\n"
                f"• Estado: Fuera del período de gracia (20 min)"
            )
        else:
            return {
                'notification_sent': False,
                'reason': 'Tipo de incumplimiento no reconocido'
            }
        
        # Crear notificaciones para todos los administradores
        notifications_created = 0
        for admin in admins:
            Notification.objects.create(
                user=admin,
                title=title,
                message=message,
                notification_type='schedule_non_compliance',
                related_object_id=schedule.id
            )
            notifications_created += 1
        
        return {
            'notification_sent': True,
            'notifications_created': notifications_created,
            'compliance_status': compliance_info['compliance_status'],
            'schedule_id': schedule.id
        }
    
    @staticmethod
    @transaction.atomic
    def create_schedule_with_validations(user, room, start_datetime, end_datetime, 
                                       created_by, notes='', recurring=False):
        """
        Crear turno con todas las validaciones aplicadas
        """
        try:
            # Validar conflictos de horario
            ScheduleValidationService.validate_schedule_conflicts(
                user, room, start_datetime, end_datetime
            )
            
            # Crear el turno
            schedule = Schedule.objects.create(
                user=user,
                room=room,
                start_datetime=start_datetime,
                end_datetime=end_datetime,
                notes=notes,
                recurring=recurring,
                created_by=created_by,
                status=Schedule.ACTIVE
            )
            
            return {
                'success': True,
                'schedule': schedule,
                'message': 'Turno creado exitosamente con validaciones aplicadas'
            }
            
        except ValidationError as e:
            return {
                'success': False,
                'error': 'Validación fallida',
                'details': str(e)
            }
        except Exception as e:
            return {
                'success': False,
                'error': 'Error interno al crear turno',
                'details': str(e)
            }
    
    @staticmethod
    @transaction.atomic  
    def update_schedule_with_validations(schedule_id, user=None, room=None, 
                                       start_datetime=None, end_datetime=None, **kwargs):
        """
        Actualizar turno con validaciones de conflictos
        """
        try:
            schedule = Schedule.objects.select_for_update().get(id=schedule_id)
            
            # Usar valores actuales si no se proporcionan nuevos
            new_user = user or schedule.user
            new_room = room or schedule.room
            new_start = start_datetime or schedule.start_datetime
            new_end = end_datetime or schedule.end_datetime
            
            # Validar conflictos si se cambian horarios, usuario o sala
            if (new_user != schedule.user or new_room != schedule.room or 
                new_start != schedule.start_datetime or new_end != schedule.end_datetime):
                ScheduleValidationService.validate_schedule_conflicts(
                    new_user, new_room, new_start, new_end, exclude_schedule_id=schedule_id
                )
            
            # Actualizar campos
            if user:
                schedule.user = user
            if room:
                schedule.room = room
            if start_datetime:
                schedule.start_datetime = start_datetime
            if end_datetime:
                schedule.end_datetime = end_datetime
            
            # Actualizar otros campos si se proporcionan
            for field, value in kwargs.items():
                if hasattr(schedule, field):
                    setattr(schedule, field, value)
            
            schedule.save()
            
            return {
                'success': True,
                'schedule': schedule,
                'message': 'Turno actualizado exitosamente con validaciones aplicadas'
            }
            
        except Schedule.DoesNotExist:
            return {
                'success': False,
                'error': 'Turno no encontrado',
                'details': f'No se encontró turno con ID {schedule_id}'
            }
        except ValidationError as e:
            return {
                'success': False,
                'error': 'Validación fallida',
                'details': e.message_dict if hasattr(e, 'message_dict') else str(e)
            }
        except Exception as e:
            return {
                'success': False,
                'error': 'Error interno al actualizar turno',
                'details': str(e)
            }

    @staticmethod
    def get_monitor_schedule_status(user, date=None):
        """
        Obtener estado de cumplimiento de turnos para un monitor en una fecha específica
        """
        if not date:
            date = timezone.now().date()
        
        # Obtener turnos del día
        schedules = Schedule.objects.filter(
            user=user,
            start_datetime__date=date,
            status=Schedule.ACTIVE
        ).select_related('room').order_by('start_datetime')
        
        schedule_status = []
        compliant_count = 0
        non_compliant_count = 0
        pending_count = 0
        
        for schedule in schedules:
            compliance_info = ScheduleValidationService.check_schedule_compliance(schedule)
            
            schedule_data = {
                'schedule_id': schedule.id,
                'room': schedule.room.name,
                'room_code': schedule.room.code,
                'start_datetime': schedule.start_datetime,
                'end_datetime': schedule.end_datetime,
                'compliance_info': compliance_info
            }
            
            schedule_status.append(schedule_data)
            
            if compliance_info['compliance_status'] == 'compliant':
                compliant_count += 1
            elif compliance_info['compliance_status'] in ['non_compliant', 'late_compliance']:
                non_compliant_count += 1
            else:
                pending_count += 1
        
        return {
            'date': date.isoformat(),
            'monitor': user.get_full_name(),
            'total_schedules': schedules.count(),
            'compliant': compliant_count,
            'non_compliant': non_compliant_count,
            'pending': pending_count,
            'schedules': schedule_status
        }


class ScheduleComplianceMonitor:
    """
    Monitor automático para verificar cumplimiento de turnos
    """
    
    @staticmethod
    def check_overdue_schedules():
        """
        Verificar turnos que han pasado su período de gracia (20 minutos) sin cumplimiento
        """
        now = timezone.now()
        grace_period_cutoff = now - timedelta(minutes=20)
        
        # Buscar turnos activos que ya deberían haber comenzado hace más de 20 minutos
        overdue_schedules = Schedule.objects.filter(
            status=Schedule.ACTIVE,
            start_datetime__lte=grace_period_cutoff
        ).select_related('user', 'room')
        
        results = {
            'checked_schedules': 0,
            'notifications_sent': 0,
            'compliant_schedules': 0,
            'non_compliant_schedules': 0,
            'details': []
        }
        
        for schedule in overdue_schedules:
            results['checked_schedules'] += 1
            
            compliance_info = ScheduleValidationService.check_schedule_compliance(schedule)
            
            if compliance_info.get('should_notify_admin', False):
                notification_result = ScheduleValidationService.notify_admin_schedule_non_compliance(
                    schedule, compliance_info
                )
                
                if notification_result['notification_sent']:
                    results['notifications_sent'] += notification_result['notifications_created']
                    results['non_compliant_schedules'] += 1
                else:
                    results['compliant_schedules'] += 1
            else:
                results['compliant_schedules'] += 1
            
            results['details'].append({
                'schedule_id': schedule.id,
                'monitor': schedule.user.get_full_name(),
                'room': schedule.room.name,
                'compliance_status': compliance_info['compliance_status'],
                'notification_sent': compliance_info.get('should_notify_admin', False)
            })
        
        return results
