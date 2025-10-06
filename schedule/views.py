from rest_framework import viewsets, status
from rest_framework.decorators import api_view, authentication_classes, permission_classes, action
from rest_framework.authentication import TokenAuthentication
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from datetime import datetime, timedelta

from .models import Schedule
from .serializers import (
    ScheduleListSerializer, ScheduleDetailSerializer, 
    ScheduleCreateUpdateSerializer, MonitorScheduleSerializer
)
from users.permissions import IsVerifiedUser
from rooms.permissions import IsAdminUser


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