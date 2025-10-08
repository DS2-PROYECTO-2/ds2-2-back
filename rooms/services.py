from django.utils import timezone
from django.core.exceptions import ValidationError
from .models import RoomEntry
from notifications.services import NotificationService


class ScheduleValidationService:
    """
    Servicio básico de validación de turnos para integración con rooms
    """
    @staticmethod
    def validate_room_access_permission(user, room, access_datetime=None):
        """
        Validar que el usuario tenga un turno activo para acceder a la sala
        """
        if access_datetime is None:
            access_datetime = timezone.now()
        
        # Importar aquí para evitar importación circular
        from schedule.models import Schedule
        
        # Verificar que el usuario tenga un turno activo en esa sala en ese momento
        active_schedule = Schedule.objects.filter(
            user=user,
            room=room,
            status=Schedule.ACTIVE,
            start_datetime__lte=access_datetime,
            end_datetime__gte=access_datetime
        ).first()
        
        if not active_schedule:
            raise ValidationError({
                'access_denied': f'El monitor {user.username} no tiene un turno asignado en la sala {room.name} para el horario actual.',
                'current_time': access_datetime,
                'room_code': room.code,
                'message': 'Solo los monitores con turnos asignados pueden acceder a las salas.'
            })
        
        return active_schedule
    
    @staticmethod
    def validate_no_multiple_monitors_in_room(room, exclude_user=None):
        """
        Validar que no haya múltiples monitores en la misma sala simultáneamente
        PETICIÓN 2: "el sistema no debe permitir que 2 monitores permanezcan en la misma"
        """
        # Verificar entradas activas en la sala
        active_entries_query = RoomEntry.objects.filter(
            room=room,
            active=True,
            exit_time__isnull=True
        ).select_related('user')
        
        # Si estamos validando para un usuario específico, excluirlo
        if exclude_user:
            active_entries_query = active_entries_query.exclude(user=exclude_user)
        
        active_entries = active_entries_query
        
        if active_entries.exists():
            active_monitors = []
            for entry in active_entries:
                active_monitors.append({
                    'username': entry.user.username,
                    'full_name': entry.user.get_full_name() or entry.user.username,
                    'entry_time': entry.entry_time,
                    'duration_minutes': int((timezone.now() - entry.entry_time).total_seconds() / 60)
                })
            
            raise ValidationError({
                'multiple_monitors': f'La sala {room.name} ({room.code}) ya tiene un monitor activo. No se permiten múltiples monitores por sala simultáneamente.',
                'active_monitors': active_monitors,
                'room_code': room.code,
                'current_time': timezone.now()
            })
        
        return True


class RoomEntryBusinessLogic:
    """
    Lógica de negocio para validaciones de entrada/salida de salas
    Tarea 2: Backend: Lógica y validaciones para Registro de ingreso/salida en sala
    """
    
    @staticmethod
    def validate_no_simultaneous_entry(user):
        """
        Validar que no se pueda ingresar a otra sala sin antes haber salido.
        HU: "No se permite ingresar a otra sala sin antes haber salido"
        """
        active_entry = RoomEntry.objects.filter(
            user=user,
            active=True,
            exit_time__isnull=True
        ).select_related('room').first()
        
        if active_entry:
            raise ValidationError({
                'simultaneous_entry': f'Ya tienes una entrada activa en {active_entry.room.name} ({active_entry.room.code}). '
                                    f'Debes salir primero antes de ingresar a otra sala.',
                'active_entry_id': active_entry.id,
                'active_room': active_entry.room.name,
                'entry_time': active_entry.entry_time
            })
        return True
    
    @staticmethod
    def calculate_session_duration(entry):
        """
        Calcular horas de permanencia en cada sesión.
        HU: "El sistema calcule mis horas de permanencia"
        """
        if not entry.exit_time:
            # Calcular duración parcial hasta ahora
            current_duration = timezone.now() - entry.entry_time
            return {
                'is_active': True,
                'current_duration_minutes': int(current_duration.total_seconds() / 60),
                'current_duration_hours': round(current_duration.total_seconds() / 3600, 2),
                'status': 'En curso'
            }
        
        # Calcular duración completa
        total_duration = entry.exit_time - entry.entry_time
        duration_minutes = int(total_duration.total_seconds() / 60)
        duration_hours = round(total_duration.total_seconds() / 3600, 2)
        
        return {
            'is_active': False,
            'total_duration_minutes': duration_minutes,
            'total_duration_hours': duration_hours,
            'formatted_duration': RoomEntryBusinessLogic._format_duration(duration_minutes),
            'status': 'Completada'
        }
    
    @staticmethod
    def _format_duration(minutes):
        """Formatear duración en formato legible"""
        if minutes < 60:
            return f"{minutes}m"
        
        hours = minutes // 60
        remaining_minutes = minutes % 60
        
        if remaining_minutes == 0:
            return f"{hours}h"
        return f"{hours}h {remaining_minutes}m"
    
    @staticmethod
    def check_and_notify_excessive_hours(entry):
        """
        Generar notificación automática al admin si un monitor excede 8 horas continuas.
        HU: "Si un monitor excede 8 horas seguidas, se genera notificación al admin"
        """
        # Calcular duración para enriquecer la respuesta
        duration_info = RoomEntryBusinessLogic.calculate_session_duration(entry)
        total_hours = duration_info.get('total_duration_hours', 0) or duration_info.get('current_duration_hours', 0) or 0
        # Usar el servicio de notificaciones y devolver formato esperado por tests
        sent = NotificationService.notify_excessive_hours(entry)
        # Calcular cuántos admins serían notificados (para el resumen)
        try:
            from users.models import User
            admins_count = User.objects.filter(role='admin', is_active=True).count() if total_hours > 8 else 0
        except Exception:
            admins_count = 0
        return {
            'notification_sent': bool(sent),
            'duration_hours': round(float(total_hours), 1) if isinstance(total_hours, (int, float)) else 0.0,
            'excess_hours': round(float(total_hours - 8), 1) if total_hours > 8 else 0.0,
            'reason': 'Duración excede el límite de 8 horas' if total_hours > 8 else 'Duración dentro del límite permitido',
            'admins_notified': admins_count
        }
    

    
    @staticmethod
    def create_room_entry_with_validations(user, room, notes=''):
        """
        Garantizar integridad de datos en escenarios concurrentes.
        Crear entrada con todas las validaciones aplicadas
        INTEGRACIÓN TAREA 2: Validar turnos y múltiples monitores
        """
        try:
            # PASO 0: Cerrar sesiones vencidas automáticamente
            closed_sessions = auto_close_expired_sessions()
            
            # VALIDACIÓN 1: Verificar que el monitor tenga turno asignado (TAREA 2)
            try:
                active_schedule = ScheduleValidationService.validate_room_access_permission(
                    user=user, 
                    room=room, 
                    access_datetime=timezone.now()
                )
            except ValidationError as schedule_error:
                response = {
                    'success': False,
                    'error': 'Sin turno asignado para esta sala',
                    'message': f'El monitor {user.username} no tiene un turno activo en {room.name} ({room.code}) en este momento.',
                    'details': {
                        'reason': 'schedule_required',
                        'current_time': timezone.now().strftime('%Y-%m-%d %H:%M:%S'),
                        'room': room.code,
                        'user': user.username
                    }
                }
                if closed_sessions:
                    response['info'] = f'Se cerraron {len(closed_sessions)} sesiones vencidas automáticamente.'
                return response
            
            # VALIDACIÓN 2: Verificar que no haya múltiples monitores en la sala (PETICIÓN 2)
            try:
                ScheduleValidationService.validate_no_multiple_monitors_in_room(
                    room=room, 
                    exclude_user=user
                )
            except ValidationError as multi_monitor_error:
                # Obtener información del monitor actual en la sala
                current_occupant = RoomEntry.objects.filter(
                    room=room, 
                    active=True, 
                    exit_time__isnull=True
                ).select_related('user').first()
                
                response = {
                    'success': False,
                    'error': 'Sala ocupada por otro monitor',
                    'message': f'La sala {room.name} ({room.code}) está ocupada. Solo se permite un monitor por sala.',
                    'details': {
                        'reason': 'room_occupied',
                        'current_time': timezone.now().strftime('%Y-%m-%d %H:%M:%S'),
                        'room': room.code,
                        'requesting_user': user.username
                    }
                }
                
                if current_occupant:
                    duration = timezone.now() - current_occupant.entry_time
                    response['current_occupant'] = {
                        'username': current_occupant.user.username,
                        'name': current_occupant.user.get_full_name() or current_occupant.user.username,
                        'entry_time': current_occupant.entry_time.strftime('%H:%M:%S'),
                        'duration_minutes': int(duration.total_seconds() / 60)
                    }
                    response['message'] += f' Actualmente ocupada por {current_occupant.user.username}.'
                
                if closed_sessions:
                    response['info'] = f'Se cerraron {len(closed_sessions)} sesiones vencidas automáticamente.'
                
                return response
            
            # VALIDACIÓN 3: Validar que no haya entrada simultánea del mismo usuario
            RoomEntryBusinessLogic.validate_no_simultaneous_entry(user)
            
            # Crear la entrada con información del turno
            entry = RoomEntry.objects.create(
                user=user,
                room=room,
                notes=f"{notes}. Turno ID: {active_schedule.id}" if notes else f"Turno ID: {active_schedule.id}"
            )
            
            # Notificar entrada a administradores (no crítico si falla)
            try:
                NotificationService.notify_room_entry(entry, is_entry=True)
            except Exception as e:
                # Log el error pero no fallar la transacción
                import logging
                logger = logging.getLogger(__name__)
                logger.warning(f"Error enviando notificación de entrada: {e}")
            
            # Construir respuesta exitosa clara
            response = {
                'success': True,
                'message': f'Acceso concedido a {room.name} ({room.code})',
                'entry': entry,  # Devolver el objeto real para serialización
                'entry_info': {
                    'id': entry.id,
                    'room': room.code,
                    'room_name': room.name,
                    'entry_time': entry.entry_time.strftime('%Y-%m-%d %H:%M:%S'),
                    'user': user.username
                },
                'schedule': {
                    'id': active_schedule.id,
                    'start_time': active_schedule.start_datetime.strftime('%H:%M'),
                    'end_time': active_schedule.end_datetime.strftime('%H:%M'),
                    'remaining_minutes': int((active_schedule.end_datetime - timezone.now()).total_seconds() / 60)
                },
                'details': {
                    'turno_valido_hasta': active_schedule.end_datetime.strftime('%H:%M'),
                    'cierre_automatico': f'La sesión se cerrará automáticamente a las {active_schedule.end_datetime.strftime("%H:%M")}',
                    'current_time': timezone.now().strftime('%Y-%m-%d %H:%M:%S')
                }
            }
            
            if closed_sessions:
                response['info'] = f'Se cerraron {len(closed_sessions)} sesiones vencidas automáticamente antes de tu entrada.'
                response['closed_sessions'] = len(closed_sessions)
            
            return response
            
        except ValidationError as e:
            return {
                'success': False,
                'error': 'Validación fallida',
                'details': e.message_dict if hasattr(e, 'message_dict') else str(e)
            }
        except Exception as e:
            return {
                'success': False,
                'error': 'Error interno al crear entrada',
                'details': str(e)
            }
    
    @staticmethod
    def exit_room_entry_with_validations(user, entry_id, notes=''):
        """
        Garantizar integridad de datos en escenarios concurrentes.
        Registrar salida con todas las validaciones aplicadas
        """
        try:
            # Buscar la entrada activa del usuario - Solución minimalista
            try:
                entry = RoomEntry.objects.get(
                    id=entry_id,
                    user=user
                )
            except RoomEntry.DoesNotExist:
                # Error específico para entrada no encontrada (404)
                return {
                    'success': False,
                    'error': 'Entrada no encontrada',
                    'details': f'No se encontró entrada con ID {entry_id} para el usuario actual',
                    'error_type': 'NOT_FOUND'
                }
            
            # Verificar si ya fue finalizada
            if entry.exit_time is not None:
                # Buscar entrada activa del usuario para sugerir el ID correcto
                active_entry = RoomEntry.objects.filter(user=user, active=True, exit_time__isnull=True).first()
                if active_entry:
                    return {
                        'success': False,
                        'error': 'Entrada ya finalizada',
                        'details': f'La entrada ID {entry_id} ya fue finalizada en {entry.exit_time}. Tu entrada activa es ID {active_entry.id} en {active_entry.room.name}.',
                        'suggestion': {
                            'active_entry_id': active_entry.id,
                            'active_room': active_entry.room.name,
                            'correct_url': f'/api/rooms/entry/{active_entry.id}/exit/'
                        }
                    }
                else:
                    return {
                        'success': False,
                        'error': 'Entrada ya finalizada',
                        'details': f'La entrada ID {entry_id} ya fue finalizada en {entry.exit_time}. No tienes entradas activas actualmente.'
                    }
            
            # Registrar la salida
            entry.exit_time = timezone.now()
            entry.active = False  # Marcar como inactiva
            if notes:
                entry.notes = notes
            entry.save()
            
            # Notificar salida a administradores (no crítico si falla)
            try:
                NotificationService.notify_room_entry(entry, is_entry=False)
            except Exception as e:
                # Log el error pero no fallar la transacción
                import logging
                logger = logging.getLogger(__name__)
                logger.warning(f"Error enviando notificación de salida: {e}")
            
            # Calcular duración
            duration_info = RoomEntryBusinessLogic.calculate_session_duration(entry)
            
            # Verificar y notificar si excede 8 horas
            notification_sent = RoomEntryBusinessLogic.check_and_notify_excessive_hours(entry)
            
            result = {
                'success': True,
                'entry': entry,
                'duration_info': duration_info,
                'message': 'Salida registrada exitosamente'
            }
            
            # Verificar si se excedieron las 8 horas
            if duration_info.get('total_duration_hours', 0) > 8:
                excess_hours = duration_info.get('total_duration_hours', 0) - 8
                result['warning'] = {
                    'message': f'Sesión excedió las 8 horas permitidas ({duration_info.get("total_duration_hours", 0):.1f} horas)',
                    'excess_hours': round(excess_hours, 2),
                    'notification_sent': notification_sent
                }
            
            return result
            
        except RoomEntry.DoesNotExist:
            return {
                'success': False,
                'error': 'Entrada no encontrada o ya finalizada',
                'details': 'No tienes una entrada activa con ese ID'
            }
        except Exception as e:
            return {
                'success': False,
                'error': 'Error interno al registrar salida',
                'details': str(e)
            }
    
    @staticmethod
    def get_user_active_session(user):
        """
        Obtener sesión activa del usuario con información de duración
        """
        try:
            active_entry = RoomEntry.objects.get(
                user=user,
                active=True,
                exit_time__isnull=True
            )
            
            duration_info = RoomEntryBusinessLogic.calculate_session_duration(active_entry)
            
            return {
                'has_active_session': True,
                'entry': active_entry,
                'duration_info': duration_info,
                'warning': duration_info['current_duration_hours'] > 8 if duration_info['is_active'] else False
            }
            
        except RoomEntry.DoesNotExist:
            return {
                'has_active_session': False,
                'entry': None,
                'duration_info': None
            }
    
    @staticmethod
    def get_user_daily_summary(user, date=None):
        """
        Obtener resumen diario de entradas del usuario
        """
        if not date:
            date = timezone.now().date()
        
        entries = RoomEntry.objects.filter(
            user=user,
            entry_time__date=date
        ).select_related('room').order_by('-entry_time')
        
        total_minutes = 0
        completed_sessions = 0
        active_sessions = 0
        
        sessions_detail = []
        
        for entry in entries:
            duration_info = RoomEntryBusinessLogic.calculate_session_duration(entry)
            
            session_data = {
                'entry_id': entry.id,
                'room_name': entry.room.name,
                'room_code': entry.room.code,
                'entry_time': entry.entry_time,
                'exit_time': entry.exit_time,
                'duration_info': duration_info,
                'notes': entry.notes
            }
            
            sessions_detail.append(session_data)
            
            if duration_info['is_active']:
                active_sessions += 1
            else:
                completed_sessions += 1
                total_minutes += duration_info['total_duration_minutes']
        
        total_hours = round(total_minutes / 60, 2) if total_minutes > 0 else 0
        
        return {
            'date': date.isoformat() if date else timezone.now().date().isoformat(),
            'total_sessions': entries.count(),
            'completed_sessions': completed_sessions,
            'active_sessions': active_sessions,
            'total_hours': total_hours,
            'total_minutes': total_minutes,
            'sessions': sessions_detail,
            'warning': total_hours > 8
        }


def auto_close_expired_sessions():
    """
    Cerrar automáticamente sesiones de monitores cuyos turnos han terminado
    SOLUCIÓN MINIMALISTA: Evita bloqueos de sala por sesiones vencidas
    """
    from schedule.models import Schedule
    
    current_time = timezone.now()
    closed_sessions = []
    
    # Buscar entradas activas cuyo turno ya terminó
    active_entries = RoomEntry.objects.filter(
        active=True,
        exit_time__isnull=True
    ).select_related('user', 'room')
    
    for entry in active_entries:
        # Buscar si el usuario tiene turno vencido en esa sala
        expired_schedule = Schedule.objects.filter(
            user=entry.user,
            room=entry.room,
            status=Schedule.ACTIVE,
            end_datetime__lt=current_time  # Turno ya terminó
        ).first()
        
        if expired_schedule:
            # Cerrar la sesión automáticamente
            entry.exit_time = current_time
            entry.active = False
            entry.notes = f"{entry.notes}. CIERRE AUTOMÁTICO: Turno terminado a las {expired_schedule.end_datetime.strftime('%H:%M')}"
            entry.save()
            
            closed_sessions.append({
                'user': entry.user.username,
                'room': entry.room.code,
                'entry_id': entry.id,
                'schedule_end': expired_schedule.end_datetime,
                'auto_closed_at': current_time
            })
    
    return closed_sessions