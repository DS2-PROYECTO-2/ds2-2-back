from django.utils import timezone
from django.db import transaction
from django.core.exceptions import ValidationError
from datetime import timedelta
from .models import RoomEntry
from notifications.models import Notification
from users.models import User


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
        if not entry.exit_time:
            return {'notification_sent': False, 'reason': 'Sesión aún activa'}
        
        duration_info = RoomEntryBusinessLogic.calculate_session_duration(entry)
        duration_hours = duration_info.get('total_duration_hours', 0)
        
        if duration_hours > 8.0:
            # Generar notificación
            admins = User.objects.filter(role='admin', is_verified=True)
            
            if admins.exists():
                notification_message = (
                    f"⚠️ ALERTA: El monitor {entry.user.get_full_name()} ({entry.user.username}) "
                    f"ha excedido las 8 horas permitidas en la sala {entry.room.name}.\n\n"
                    f"📊 Detalles de la sesión:\n"
                    f"• Sala: {entry.room.name} ({entry.room.code})\n"
                    f"• Entrada: {entry.entry_time.strftime('%d/%m/%Y a las %H:%M')}\n"
                    f"• Salida: {entry.exit_time.strftime('%d/%m/%Y a las %H:%M')}\n"
                    f"• Duración total: {duration_info['formatted_duration']} ({duration_hours} horas)\n"
                    f"• Exceso: {round(duration_hours - 8, 2)} horas adicionales"
                )
                
                for admin in admins:
                    Notification.objects.create(
                        user=admin,
                        title="Monitor excedió 8 horas continuas",
                        message=notification_message,
                        notification_type='excessive_hours',
                        related_object_id=entry.id
                    )
                
                return {
                    'notification_sent': True,
                    'duration_hours': duration_hours,
                    'excess_hours': round(duration_hours - 8, 2),
                    'admins_notified': admins.count()
                }
            else:
                return {
                    'notification_sent': False,
                    'reason': 'No hay administradores verificados disponibles',
                    'duration_hours': duration_hours
                }
        
        return {
            'notification_sent': False,
            'reason': 'Duración dentro del límite permitido',
            'duration_hours': duration_hours
        }
    
    @staticmethod
    @transaction.atomic
    def create_room_entry_with_validations(user, room, notes=''):
        """
        Garantizar integridad de datos en escenarios concurrentes.
        Crear entrada con todas las validaciones aplicadas
        """
        try:
            # Validar que no haya entrada simultánea
            RoomEntryBusinessLogic.validate_no_simultaneous_entry(user)
            
            # Crear la entrada
            entry = RoomEntry.objects.create(
                user=user,
                room=room,
                notes=notes
            )
            
            return {
                'success': True,
                'entry': entry,
                'message': 'Entrada registrada exitosamente con validaciones aplicadas'
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
                'error': 'Error interno al crear entrada',
                'details': str(e)
            }
    
    @staticmethod
    @transaction.atomic
    def exit_room_entry_with_validations(user, entry_id, notes=''):
        """
        Garantizar integridad de datos en escenarios concurrentes.
        Registrar salida con todas las validaciones aplicadas
        """
        try:
            # Buscar la entrada activa del usuario - Solución minimalista
            try:
                entry = RoomEntry.objects.select_for_update().get(
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
                active_entry = RoomEntry.objects.filter(user=user, exit_time__isnull=True).first()
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
            if notes:
                entry.notes = notes
            entry.save()
            
            # Calcular duración
            duration_info = RoomEntryBusinessLogic.calculate_session_duration(entry)
            
            # Verificar y notificar si excede 8 horas
            notification_result = RoomEntryBusinessLogic.check_and_notify_excessive_hours(entry)
            
            result = {
                'success': True,
                'entry': entry,
                'duration_info': duration_info,
                'message': 'Salida registrada exitosamente'
            }
            
            if notification_result['notification_sent']:
                result['warning'] = {
                    'message': f'Sesión excedió las 8 horas permitidas ({notification_result["duration_hours"]} horas)',
                    'excess_hours': notification_result['excess_hours'],
                    'admins_notified': notification_result['admins_notified']
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