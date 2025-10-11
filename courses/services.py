from django.utils import timezone
from django.core.exceptions import ValidationError
from django.db.models import Q
from datetime import timedelta

from .models import Course, CourseHistory
from schedule.models import Schedule


class CourseValidationService:
    """
    Servicio para validaciones de negocio de cursos
    """
    
    @staticmethod
    def validate_course_creation(room, monitor, schedule, start_datetime, end_datetime, exclude_course_id=None):
        """
        Validar que se puede crear/actualizar un curso con los parámetros dados
        """
        # 1. Validar que no haya solapamiento en la sala (CRITERIO: no solapen cursos en misma sala)
        CourseValidationService.validate_no_room_conflicts(
            room, start_datetime, end_datetime, exclude_course_id
        )
        
        # 2. Validar que el turno del monitor cubra completamente el curso
        CourseValidationService.validate_monitor_schedule_coverage(
            monitor, schedule, start_datetime, end_datetime
        )
        
        # 3. Validar que existan las dependencias requeridas
        CourseValidationService.validate_dependencies(room, monitor, schedule)
        
        return True
    
    @staticmethod
    def validate_no_room_conflicts(room, start_datetime, end_datetime, exclude_course_id=None):
        """
        Validar que no existan solapamientos de cursos en la misma sala
        """
        conflicts_query = Q(
            room=room,
            status__in=[Course.SCHEDULED, Course.IN_PROGRESS]
        ) & (
            Q(start_datetime__lt=end_datetime, end_datetime__gt=start_datetime)
        )
        
        if exclude_course_id:
            conflicts_query &= ~Q(id=exclude_course_id)
        
        conflicting_courses = Course.objects.filter(conflicts_query)
        
        if conflicting_courses.exists():
            conflict = conflicting_courses.first()
            raise ValidationError(
                f'Conflicto de horario: Ya existe el curso "{conflict.name}" en la sala {room.name} '
                f'de {conflict.start_datetime.strftime("%H:%M")} a {conflict.end_datetime.strftime("%H:%M")} '
                f'el {conflict.start_datetime.strftime("%d/%m/%Y")}'
            )
        
        return True
    
    @staticmethod
    def validate_monitor_schedule_coverage(monitor, schedule, start_datetime, end_datetime):
        """
        Validar que el turno del monitor cubra completamente la duración del curso
        """
        # Verificar que el schedule pertenezca al monitor
        if schedule.user != monitor:
            raise ValidationError(
                f'El turno seleccionado no pertenece al monitor {monitor.get_full_name()}'
            )
        
        # Verificar que el schedule esté activo
        if schedule.status != Schedule.ACTIVE:
            raise ValidationError(
                f'El turno seleccionado no está activo (estado: {schedule.get_status_display()})'
            )
        

        # Verificar que el turno cubra completamente el curso
        # Convertir a zona horaria local para mostrar en mensajes de error
        from django.utils import timezone
        local_tz = timezone.get_current_timezone()
        
        schedule_start_local = schedule.start_datetime.astimezone(local_tz)
        schedule_end_local = schedule.end_datetime.astimezone(local_tz)
        course_start_local = start_datetime.astimezone(local_tz)
        course_end_local = end_datetime.astimezone(local_tz)
        
        if schedule.start_datetime > start_datetime:
            raise ValidationError(
                f'El turno del monitor inicia el {schedule_start_local.strftime("%d/%m/%Y a las %H:%M")} '
                f'pero el curso inicia el {course_start_local.strftime("%d/%m/%Y a las %H:%M")}. '
                f'El turno debe cubrir completamente el curso.'
            )
        
        if schedule.end_datetime < end_datetime:
            raise ValidationError(
                f'El turno del monitor termina el {schedule_end_local.strftime("%d/%m/%Y a las %H:%M")} '
                f'pero el curso termina el {course_end_local.strftime("%d/%m/%Y a las %H:%M")}. '
                f'El turno debe cubrir completamente el curso.'
            )
        
        # Verificar que sea la misma sala
        if schedule.room != schedule.room:
            # Esta validación se hará en la vista, aquí asumimos consistencia
            pass
        
        return True
    
    @staticmethod
    def validate_dependencies(room, monitor, schedule):
        """
        Validar que existan las dependencias requeridas
        """
        # Validar que la sala esté activa
        if not room.is_active:
            raise ValidationError(f'La sala {room.name} no está activa')
        
        # Validar que el monitor esté verificado y activo
        if not monitor.is_verified:
            raise ValidationError(f'El monitor {monitor.get_full_name()} no está verificado')
        
        if not monitor.is_active:
            raise ValidationError(f'El monitor {monitor.get_full_name()} no está activo')
        
        if monitor.role != 'monitor':
            raise ValidationError(f'El usuario {monitor.get_full_name()} no es un monitor')
        
        # Validar que el schedule exista y esté activo
        if schedule.status != Schedule.ACTIVE:
            raise ValidationError(f'El turno seleccionado no está activo')
        
        return True


class CourseHistoryService:
    """
    Servicio para gestionar el historial de cambios de cursos
    """
    
    @staticmethod
    def record_change(course, action, changes, user):
        """
        Registrar un cambio en el historial del curso
        """
        return CourseHistory.objects.create(
            course=course,
            action=action,
            changes=changes,
            changed_by=user
        )
    
    @staticmethod
    def record_creation(course, user):
        """
        Registrar la creación de un curso
        """
        changes = {
            'name': course.name,
            'room': course.room.name,
            'monitor': course.monitor.get_full_name(),
            'start_datetime': course.start_datetime.isoformat(),
            'end_datetime': course.end_datetime.isoformat(),
            'status': course.status
        }
        
        return CourseHistoryService.record_change(
            course, CourseHistory.ACTION_CREATE, changes, user
        )
    
    @staticmethod
    def record_update(course, old_values, user):
        """
        Registrar la actualización de un curso
        """
        changes = {}
        
        # Comparar valores anteriores con actuales
        fields_to_track = ['name', 'description', 'status', 'start_datetime', 'end_datetime']
        
        for field in fields_to_track:
            old_value = old_values.get(field)
            new_value = getattr(course, field)
            
            if old_value != new_value:
                if hasattr(new_value, 'isoformat'):  # Para datetime
                    changes[field] = {
                        'old': old_value.isoformat() if old_value else None,
                        'new': new_value.isoformat() if new_value else None
                    }
                else:
                    changes[field] = {
                        'old': old_value,
                        'new': new_value
                    }
        
        if changes:  # Solo registrar si hay cambios
            return CourseHistoryService.record_change(
                course, CourseHistory.ACTION_UPDATE, changes, user
            )
        
        return None
    
    @staticmethod
    def record_deletion(course, user):
        """
        Registrar la eliminación de un curso
        """
        changes = {
            'name': course.name,
            'room': course.room.name,
            'monitor': course.monitor.get_full_name(),
            'start_datetime': course.start_datetime.isoformat(),
            'end_datetime': course.end_datetime.isoformat(),
            'status': course.status,
            'deleted_at': timezone.now().isoformat()
        }
        
        return CourseHistoryService.record_change(
            course, CourseHistory.ACTION_DELETE, changes, user
        )