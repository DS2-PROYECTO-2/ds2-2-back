# Schedule Services - Clean Version
from django.utils import timezone
from django.core.exceptions import ValidationError

class ScheduleValidationService:
    """
    Lógica de negocio para validaciones de turnos y calendarios
    Tarea 2: Backend: Lógica y validaciones para Integración con calendarios
    """
    
    @staticmethod
    def validate_schedule_conflicts(user, room, start_datetime, end_datetime, exclude_schedule_id=None):
        """
        Validar conflictos de horarios:
        1. Un monitor no puede estar en dos turnos al mismo tiempo
        2. Una sala no puede tener 2 monitores simultáneamente (PETICIÓN 2)
        """
        from .models import Schedule
        from django.db.models import Q
        
        # Validar conflictos de usuario (mismo monitor en diferentes salas)
        user_conflict_query = Q(
            user=user,
            status=Schedule.ACTIVE
        ) & (
            Q(start_datetime__lt=end_datetime, end_datetime__gt=start_datetime)
        )
        
        # Validar conflictos de sala (diferentes monitores en misma sala)
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
        
        # Verificar conflictos de usuario
        user_conflicts = Schedule.objects.filter(user_conflict_query).select_related('room')
        if user_conflicts.exists():
            raise ValidationError({
                'user_conflict': f'El monitor {user.username} ya tiene turnos asignados que se superponen con el horario propuesto.',
            })
        
        # Verificar conflictos de sala (PETICIÓN 2)
        room_conflicts = Schedule.objects.filter(room_conflict_query).select_related('user')
        if room_conflicts.exists():
            raise ValidationError({
                'room_conflict': f'La sala {room.name} ({room.code}) ya tiene un monitor asignado que se superpone con el horario propuesto. No se permiten 2 monitores por sala al mismo tiempo.',
            })
        
        return True
        
    @staticmethod  
    def validate_room_access_permission(user, room, access_datetime=None):
        """Validate room access based on active schedule with early access support"""
        if access_datetime is None:
            access_datetime = timezone.now()
        
        from .models import Schedule
        
        # Buscar turnos del día actual
        turnos_del_dia = Schedule.objects.filter(
            user=user,
            room=room,
            status=Schedule.ACTIVE,
            start_datetime__date=access_datetime.date()
        )
        
        if not turnos_del_dia.exists():
            raise ValidationError({
                "access_denied": f"El monitor {user.username} no tiene un turno asignado en la sala {room.name} para hoy.",
                "current_time": access_datetime,
                "room_code": room.code
            })
        
        # Buscar turno activo en el momento exacto
        active_schedule = turnos_del_dia.filter(
            start_datetime__lte=access_datetime,
            end_datetime__gte=access_datetime
        ).first()
        
        # Si no hay turno activo, buscar turno futuro (para acceso anticipado)
        if not active_schedule:
            future_schedule = turnos_del_dia.filter(
                start_datetime__gt=access_datetime
            ).order_by('start_datetime').first()
            
            if future_schedule:
                # Verificar si el acceso anticipado está permitido (máximo 10 minutos antes)
                diferencia_minutos = (future_schedule.start_datetime - access_datetime).total_seconds() / 60
                
                if diferencia_minutos <= 10:
                    return future_schedule  # Permitir acceso anticipado
                else:
                    raise ValidationError({
                        "access_denied": f"Acceso muy anticipado. El turno inicia en {diferencia_minutos:.1f} minutos. Máximo 10 minutos antes.",
                        "current_time": access_datetime,
                        "room_code": room.code,
                        "next_schedule": future_schedule.start_datetime
                    })
            else:
                raise ValidationError({
                    "access_denied": f"El monitor {user.username} no tiene un turno asignado en la sala {room.name} para el horario actual.",
                    "current_time": access_datetime,
                    "room_code": room.code
                })
        
        return active_schedule
    
    @staticmethod
    def check_schedule_compliance(schedule_id):
        """
        Verificar cumplimiento de turno con período de gracia de 5 minutos
        """
        from .models import Schedule
        from rooms.models import RoomEntry
        from datetime import timedelta
        
        try:
            schedule = Schedule.objects.get(id=schedule_id, status=Schedule.ACTIVE)
        except Schedule.DoesNotExist:
            return {'status': 'not_found', 'message': 'Turno no encontrado o no activo'}
        
        current_time = timezone.now()
        grace_period = timedelta(minutes=5)
        
        # Si el turno aún no ha comenzado
        if current_time < schedule.start_datetime:
            return {'status': 'pending', 'message': 'Turno aún no iniciado'}
        
        # Verificar si hay entrada registrada en RoomEntry
        room_entry = RoomEntry.objects.filter(
            user=schedule.user,
            room=schedule.room,
            entry_time__gte=schedule.start_datetime,
            entry_time__lte=schedule.start_datetime + grace_period
        ).first()
        
        if room_entry:
            return {
                'status': 'compliant',
                'message': 'Turno cumplido correctamente',
                'entry_time': room_entry.entry_time
            }
        
        # Si estamos dentro del período de gracia y no hay entrada
        if current_time <= schedule.start_datetime + grace_period:
            return {'status': 'grace_period', 'message': 'Dentro del período de gracia'}
        
        # Si pasó el período de gracia y no hay entrada
        return {
            'status': 'non_compliant',
            'message': 'No se registró entrada dentro del período de gracia',
            'schedule': schedule,
            'expected_start': schedule.start_datetime,
            'grace_deadline': schedule.start_datetime + grace_period,
            'current_time': current_time
        }
    
    @staticmethod
    def notify_admin_schedule_non_compliance(schedule, compliance_check_result):
        """
        Generar notificación al administrador cuando un turno no se cumple
        """
        from notifications.models import Notification
        from users.models import User
        
        # Obtener administradores
        admins = User.objects.filter(role='admin', is_active=True)
        
        if not admins.exists():
            return False
        
        # Crear mensaje de notificación
        message = f"""INCUMPLIMIENTO DE TURNO DETECTADO

Monitor: {schedule.user.get_full_name() or schedule.user.username} ({schedule.user.username})
Sala: {schedule.room.name} ({schedule.room.code})
Turno programado: {schedule.start_datetime.strftime('%Y-%m-%d %H:%M')} - {schedule.end_datetime.strftime('%Y-%m-%d %H:%M')}

El monitor no registró entrada dentro del período de gracia de 5 minutos.
Límite de gracia: {compliance_check_result['grace_deadline'].strftime('%Y-%m-%d %H:%M')}
Hora actual de verificación: {compliance_check_result['current_time'].strftime('%Y-%m-%d %H:%M')}

Se requiere seguimiento administrativo."""
        
        # Crear notificaciones para todos los administradores
        notifications_created = []
        for admin in admins:
            notification = Notification.objects.create(
                user=admin,
                title=f"Incumplimiento de Turno - {schedule.room.code}",
                message=message,
                notification_type='SCHEDULE_NON_COMPLIANCE',  # Usar tipo específico
                read=False,
                related_object_id=schedule.id
            )
            notifications_created.append(notification)
        
        return notifications_created


class ScheduleComplianceMonitor:
    """
    Monitor automatizado para verificar cumplimiento de turnos
    """
    
    @staticmethod
    def check_overdue_schedules():
        """
        Verificar turnos vencidos y generar notificaciones automáticas
        Ejecutar cada hora mediante cron job o celery
        """
        from .models import Schedule
        from notifications.models import Notification
        from datetime import timedelta
        
        current_time = timezone.now()
        grace_period = timedelta(minutes=5)
        
        # Buscar turnos que deberían haber comenzado hace más de 5 minutos
        overdue_schedules = Schedule.objects.filter(
            status=Schedule.ACTIVE,
            start_datetime__lt=current_time - grace_period,
            start_datetime__gte=current_time - timedelta(hours=24)  # Solo revisar últimas 24 horas
        ).select_related('user', 'room')
        
        notifications_generated = []
        
        for schedule in overdue_schedules:
            # Verificar cumplimiento
            compliance_result = ScheduleValidationService.check_schedule_compliance(schedule.id)
            
            if compliance_result['status'] == 'non_compliant':
                # Verificar si ya se generó notificación para este turno
                existing_notification = Notification.objects.filter(
                    notification_type='SCHEDULE_NON_COMPLIANCE',
                    related_object_id=schedule.id
                ).exists()
                
                if not existing_notification:
                    # Generar notificación
                    notifications = ScheduleValidationService.notify_admin_schedule_non_compliance(
                        schedule, compliance_result
                    )
                    
                    if notifications:
                        notifications_generated.extend(notifications)
        
        return {
            'checked_schedules': len(overdue_schedules),
            'notifications_generated': len(notifications_generated),
            'notifications': notifications_generated
        }
    
    @staticmethod
    def validate_no_multiple_monitors_in_room(room, exclude_user=None):
        """
        Validar que no haya múltiples monitores activos en la misma sala
        PETICIÓN 2: Solo un monitor por sala
        """
        from rooms.models import RoomEntry
        
        # Buscar entradas activas en la sala
        active_entries = RoomEntry.objects.filter(
            room=room,
            active=True,
            exit_time__isnull=True
        ).select_related('user')
        
        # Si hay un usuario a excluir, filtrarlo
        if exclude_user:
            active_entries = active_entries.exclude(user=exclude_user)
        
        if active_entries.exists():
            current_monitor = active_entries.first()
            raise ValidationError({
                'room_occupied': f'La sala {room.name} ({room.code}) ya está ocupada por {current_monitor.user.username}.',
                'current_occupant': current_monitor.user.username,
                'room_code': room.code
            })

