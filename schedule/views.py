from rest_framework import viewsets, permissions, status
from rest_framework.decorators import api_view, authentication_classes, permission_classes, action
from rest_framework.authentication import TokenAuthentication
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.db.models import Q
from django.core.exceptions import ValidationError
from datetime import datetime, timedelta

from .models import Schedule
from .serializers import (
    ScheduleListSerializer, ScheduleDetailSerializer, 
    ScheduleCreateUpdateSerializer, MonitorScheduleSerializer
)
from .services import ScheduleValidationService, ScheduleComplianceMonitor
from users.permissions import IsVerifiedUser
from rooms.permissions import IsAdminUser
from rooms.models import Room


class ScheduleViewSet(viewsets.ModelViewSet):
    """
    API endpoint para gestionar turnos (CRUD completo)
    Solo administradores pueden crear, editar y eliminar
    """
    
    def get_serializer_class(self):
        """Seleccionar serializer según la acción"""
        if self.action == 'list':
            return ScheduleListSerializer
        elif self.action == 'retrieve':
            return ScheduleDetailSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return ScheduleCreateUpdateSerializer
        return ScheduleDetailSerializer
    
    def get_queryset(self):
        """Retorna turnos según el rol del usuario"""
        user = self.request.user
        if hasattr(user, 'role') and user.role == 'admin':
            return Schedule.objects.select_related('user', 'room', 'created_by').all()
        else:
            return Schedule.objects.select_related('room', 'created_by').filter(user=user)
    
    def get_permissions(self):
        """Define permisos según la acción"""
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [IsAuthenticated, IsAdminUser]
        else:
            permission_classes = [IsAuthenticated, IsVerifiedUser]
        
        return [permission() for permission in permission_classes]
    
    def create(self, request, *args, **kwargs):
        """Crear turno con validaciones de conflictos"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Usar el servicio de validación para crear con validaciones
        result = ScheduleValidationService.create_schedule_with_validations(
            user=serializer.validated_data['user'],
            room=serializer.validated_data['room'], 
            start_datetime=serializer.validated_data['start_datetime'],
            end_datetime=serializer.validated_data['end_datetime'],
            created_by=request.user,
            notes=serializer.validated_data.get('notes', ''),
            recurring=serializer.validated_data.get('recurring', False)
        )
        
        if not result['success']:
            return Response(
                {
                    'error': result['error'],
                    'details': result['details']
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        response_serializer = ScheduleDetailSerializer(result['schedule'])
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)
    
    def update(self, request, *args, **kwargs):
        """Actualizar turno con validaciones de conflictos"""
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        
        # Usar el servicio de validación para actualizar con validaciones
        result = ScheduleValidationService.update_schedule_with_validations(
            schedule_id=instance.id,
            **serializer.validated_data
        )
        
        if not result['success']:
            return Response(
                {
                    'error': result['error'], 
                    'details': result['details']
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        response_serializer = ScheduleDetailSerializer(result['schedule'])
        return Response(response_serializer.data)
    
    @action(detail=True, methods=['get'])
    def compliance(self, request, pk=None):
        """Verificar cumplimiento de un turno específico"""
        schedule = self.get_object()
        compliance_info = ScheduleValidationService.check_schedule_compliance(schedule)
        
        return Response({
            'schedule_id': schedule.id,
            'monitor': schedule.user.get_full_name(),
            'room': f"{schedule.room.name} ({schedule.room.code})",
            'start_datetime': schedule.start_datetime,
            'end_datetime': schedule.end_datetime,
            'compliance_info': compliance_info
        })
    
    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated, IsAdminUser])
    def check_compliance_batch(self, request):
        """Verificar cumplimiento de múltiples turnos"""
        results = ScheduleComplianceMonitor.check_overdue_schedules()
        return Response(results)
    
    @action(detail=False, methods=['get'])
    def upcoming(self, request):
        """Obtener turnos próximos (siguientes 7 días)"""
        now = timezone.now()
        end_date = now + timedelta(days=7)
        
        queryset = self.get_queryset().filter(
            start_datetime__gte=now,
            start_datetime__lte=end_date,
            status=Schedule.ACTIVE
        ).order_by('start_datetime')
        
        serializer = ScheduleListSerializer(queryset, many=True)
        return Response({
            'count': queryset.count(),
            'upcoming_schedules': serializer.data
        })
    
    @action(detail=False, methods=['get'])
    def current(self, request):
        """Obtener turnos actuales (en curso)"""
        now = timezone.now()
        
        queryset = self.get_queryset().filter(
            start_datetime__lte=now,
            end_datetime__gte=now,
            status=Schedule.ACTIVE
        )
        
        serializer = ScheduleListSerializer(queryset, many=True)
        return Response({
            'count': queryset.count(),
            'current_schedules': serializer.data
        })


@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsVerifiedUser])
def monitor_schedules_view(request):
    """
    Vista específica para que monitores vean sus turnos
    """
    try:
        # Filtros opcionales
        date_from = request.GET.get('date_from')
        date_to = request.GET.get('date_to')
        status_filter = request.GET.get('status', 'active')
        
        # Base queryset - solo turnos del monitor
        queryset = Schedule.objects.filter(user=request.user).select_related('room')
        
        # Aplicar filtros
        if date_from:
            try:
                date_from_parsed = datetime.strptime(date_from, '%Y-%m-%d').date()
                queryset = queryset.filter(start_datetime__date__gte=date_from_parsed)
            except ValueError:
                return Response({
                    'error': 'Formato de fecha inválido para date_from. Use YYYY-MM-DD'
                }, status=status.HTTP_400_BAD_REQUEST)
        
        if date_to:
            try:
                date_to_parsed = datetime.strptime(date_to, '%Y-%m-%d').date()
                queryset = queryset.filter(start_datetime__date__lte=date_to_parsed)
            except ValueError:
                return Response({
                    'error': 'Formato de fecha inválido para date_to. Use YYYY-MM-DD'
                }, status=status.HTTP_400_BAD_REQUEST)
        
        if status_filter and status_filter != 'all':
            queryset = queryset.filter(status=status_filter)
        
        # Ordenar por fecha
        queryset = queryset.order_by('start_datetime')
        
        # Separar por categorías
        now = timezone.now()
        current_schedules = queryset.filter(
            start_datetime__lte=now,
            end_datetime__gte=now,
            status=Schedule.ACTIVE
        )
        
        upcoming_schedules = queryset.filter(
            start_datetime__gt=now,
            status=Schedule.ACTIVE
        )[:10]  # Próximos 10
        
        past_schedules = queryset.filter(
            end_datetime__lt=now
        ).order_by('-start_datetime')[:20]  # Últimos 20
        
        return Response({
            'monitor': {
                'username': request.user.username,
                'full_name': request.user.get_full_name()
            },
            'summary': {
                'total_schedules': queryset.count(),
                'current_schedules': current_schedules.count(),
                'upcoming_schedules': upcoming_schedules.count(),
                'past_schedules': past_schedules.count()
            },
            'current_schedules': MonitorScheduleSerializer(current_schedules, many=True).data,
            'upcoming_schedules': MonitorScheduleSerializer(upcoming_schedules, many=True).data,
            'past_schedules': MonitorScheduleSerializer(past_schedules, many=True).data,
            'filters_applied': {
                'date_from': date_from,
                'date_to': date_to,
                'status': status_filter
            }
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({
            'error': 'Error al obtener turnos del monitor',
            'details': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAdminUser])
def admin_schedules_overview_view(request):
    """
    Vista para que admins vean resumen general de todos los turnos
    """
    try:
        now = timezone.now()
        
        # Estadísticas generales
        total_schedules = Schedule.objects.count()
        active_schedules = Schedule.objects.filter(status=Schedule.ACTIVE).count()
        current_schedules = Schedule.objects.filter(
            start_datetime__lte=now,
            end_datetime__gte=now,
            status=Schedule.ACTIVE
        ).count()
        
        # Turnos por estado
        schedules_by_status = {}
        for status_code, status_name in Schedule.STATUS_CHOICES:
            schedules_by_status[status_code] = Schedule.objects.filter(status=status_code).count()
        
        # Próximos turnos (siguientes 24 horas)
        next_24h = now + timedelta(hours=24)
        upcoming_schedules = Schedule.objects.filter(
            start_datetime__gte=now,
            start_datetime__lte=next_24h,
            status=Schedule.ACTIVE
        ).select_related('user', 'room').order_by('start_datetime')
        
        # Turnos sin cumplimiento (completados sin entradas de sala)
        non_compliant_schedules = Schedule.objects.filter(
            status=Schedule.COMPLETED,
            end_datetime__lt=now
        ).select_related('user', 'room')
        
        non_compliant_list = []
        for schedule in non_compliant_schedules:
            if not schedule.has_compliance():
                non_compliant_list.append(schedule)
        
        return Response({
            'overview': {
                'total_schedules': total_schedules,
                'active_schedules': active_schedules,
                'current_schedules': current_schedules,
                'schedules_by_status': schedules_by_status,
                'non_compliant_count': len(non_compliant_list)
            },
            'upcoming_24h': ScheduleListSerializer(upcoming_schedules, many=True).data,
            'non_compliant_schedules': ScheduleListSerializer(non_compliant_list, many=True).data,
            'generated_at': now.isoformat()
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({
            'error': 'Error al obtener resumen de turnos',
            'details': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsVerifiedUser])
def monitor_current_schedule_view(request):
    """
    Vista para obtener el turno actual del monitor (si existe)
    """
    try:
        now = timezone.now()
        
        # Buscar turno actual
        current_schedule = Schedule.objects.filter(
            user=request.user,
            start_datetime__lte=now,
            end_datetime__gte=now,
            status=Schedule.ACTIVE
        ).select_related('room').first()
        
        if current_schedule:
            return Response({
                'has_current_schedule': True,
                'current_schedule': MonitorScheduleSerializer(current_schedule).data
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                'has_current_schedule': False,
                'current_schedule': None
            }, status=status.HTTP_200_OK)
            
    except Exception as e:
        return Response({
            'error': 'Error al obtener turno actual',
            'details': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def validate_room_access_view(request):
    """
    Validar si un monitor puede acceder a una sala en un momento específico
    Tarea 2: Validación de acceso según turnos asignados
    """
    try:
        room_id = request.data.get('room_id')
        entry_time = request.data.get('entry_time')
        
        if not room_id:
            return Response({
                'error': 'room_id es requerido'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            room = Room.objects.get(id=room_id)
        except Room.DoesNotExist:
            return Response({
                'error': 'Sala no encontrada'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Parsear tiempo de entrada si se proporciona
        parsed_entry_time = None
        if entry_time:
            try:
                parsed_entry_time = datetime.fromisoformat(entry_time.replace('Z', '+00:00'))
            except ValueError:
                return Response({
                    'error': 'Formato de entry_time inválido. Use formato ISO 8601'
                }, status=status.HTTP_400_BAD_REQUEST)
        
        # Validar acceso
        try:
            validation_result = ScheduleValidationService.validate_room_access_permission(
                user=request.user,
                room=room,
                entry_time=parsed_entry_time
            )
            
            response_data = {
                'access_granted': True,
                'message': validation_result['message'],
                'room': {
                    'id': room.id,
                    'name': room.name,
                    'code': room.code
                }
            }
            
            # Agregar información del turno activo si existe
            if 'active_schedule' in validation_result and validation_result['active_schedule']:
                schedule = validation_result['active_schedule']
                response_data['active_schedule'] = {
                    'id': schedule.id,
                    'start_datetime': schedule.start_datetime,
                    'end_datetime': schedule.end_datetime,
                    'status': schedule.status
                }
            
            return Response(response_data, status=status.HTTP_200_OK)
            
        except ValidationError as e:
            return Response({
                'access_granted': False,
                'validation_error': str(e),
                'room': {
                    'id': room.id,
                    'name': room.name,
                    'code': room.code
                }
            }, status=status.HTTP_403_FORBIDDEN)
            
    except Exception as e:
        return Response({
            'error': 'Error interno al validar acceso',
            'details': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsVerifiedUser])
def monitor_schedule_compliance_view(request):
    """
    Obtener estado de cumplimiento de turnos del monitor
    """
    try:
        date_param = request.GET.get('date')
        target_date = None
        
        if date_param:
            try:
                target_date = datetime.strptime(date_param, '%Y-%m-%d').date()
            except ValueError:
                return Response({
                    'error': 'Formato de fecha inválido. Use YYYY-MM-DD'
                }, status=status.HTTP_400_BAD_REQUEST)
        
        compliance_status = ScheduleValidationService.get_monitor_schedule_status(
            user=request.user,
            date=target_date
        )
        
        return Response(compliance_status, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({
            'error': 'Error al obtener estado de cumplimiento',
            'details': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAdminUser])
def validate_schedule_conflict_view(request):
    """
    Validar conflictos de horarios antes de crear/editar un turno
    """
    try:
        user_id = request.data.get('user_id')
        room_id = request.data.get('room_id')
        start_datetime_str = request.data.get('start_datetime')
        end_datetime_str = request.data.get('end_datetime')
        exclude_schedule_id = request.data.get('exclude_schedule_id')
        
        if not all([user_id, room_id, start_datetime_str, end_datetime_str]):
            return Response({
                'error': 'user_id, room_id, start_datetime y end_datetime son requeridos'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            from users.models import User
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({
                'error': 'Usuario no encontrado'
            }, status=status.HTTP_404_NOT_FOUND)
        
        try:
            from rooms.models import Room
            room = Room.objects.get(id=room_id)
        except Room.DoesNotExist:
            return Response({
                'error': 'Sala no encontrada'
            }, status=status.HTTP_404_NOT_FOUND)
        
        try:
            start_datetime = datetime.fromisoformat(start_datetime_str.replace('Z', '+00:00'))
            end_datetime = datetime.fromisoformat(end_datetime_str.replace('Z', '+00:00'))
        except ValueError:
            return Response({
                'error': 'Formato de datetime inválido. Use formato ISO 8601'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Validar conflictos
        try:
            ScheduleValidationService.validate_schedule_conflicts(
                user=user,
                room=room,
                start_datetime=start_datetime,
                end_datetime=end_datetime,
                exclude_schedule_id=exclude_schedule_id
            )
            
            return Response({
                'conflict_found': False,
                'message': 'No hay conflictos de horario',
                'user': user.get_full_name(),
                'proposed_schedule': {
                    'start_datetime': start_datetime,
                    'end_datetime': end_datetime
                }
            }, status=status.HTTP_200_OK)
            
        except ValidationError as e:
            return Response({
                'conflict_found': True,
                'validation_error': e.message_dict if hasattr(e, 'message_dict') else str(e),
                'user': user.get_full_name(),
                'proposed_schedule': {
                    'start_datetime': start_datetime,
                    'end_datetime': end_datetime
                }
            }, status=status.HTTP_409_CONFLICT)
            
    except Exception as e:
        return Response({
            'error': 'Error interno al validar conflictos',  
            'details': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAdminUser])
def notify_schedule_non_compliance_view(request):
    """
    Manualmente disparar notificaciones por incumplimiento de turnos
    """
    try:
        schedule_id = request.data.get('schedule_id')
        
        if not schedule_id:
            return Response({
                'error': 'schedule_id es requerido'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            schedule = Schedule.objects.get(id=schedule_id)
        except Schedule.DoesNotExist:
            return Response({
                'error': 'Turno no encontrado'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Verificar cumplimiento
        compliance_info = ScheduleValidationService.check_schedule_compliance(schedule)
        
        # Enviar notificación si es necesario
        if compliance_info.get('should_notify_admin', False):
            notification_result = ScheduleValidationService.notify_admin_schedule_non_compliance(
                schedule, compliance_info
            )
            
            return Response({
                'notification_sent': notification_result['notification_sent'],
                'notifications_created': notification_result.get('notifications_created', 0),
                'compliance_info': compliance_info,
                'schedule': {
                    'id': schedule.id,
                    'monitor': schedule.user.get_full_name(),
                    'room': f"{schedule.room.name} ({schedule.room.code})",
                    'start_datetime': schedule.start_datetime,
                    'end_datetime': schedule.end_datetime
                }
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                'notification_sent': False,
                'reason': 'No se requiere notificación para este turno',
                'compliance_info': compliance_info,
                'schedule': {
                    'id': schedule.id,
                    'monitor': schedule.user.get_full_name(),
                    'room': f"{schedule.room.name} ({schedule.room.code})",
                    'start_datetime': schedule.start_datetime,
                    'end_datetime': schedule.end_datetime
                }
            }, status=status.HTTP_200_OK)
            
    except Exception as e:
        return Response({
            'error': 'Error al procesar notificación',
            'details': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)