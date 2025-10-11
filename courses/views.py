from rest_framework import viewsets, status
from rest_framework.decorators import api_view, authentication_classes, permission_classes, action
from rest_framework.authentication import TokenAuthentication
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from django.shortcuts import get_object_or_404
from datetime import datetime, timedelta

from .models import Course, CourseHistory
from .serializers import (
    CourseListSerializer, CourseDetailSerializer,
    CourseCreateUpdateSerializer, MonitorCourseSerializer,
    CourseHistorySerializer
)
from .services import CourseValidationService, CourseHistoryService
from users.permissions import IsVerifiedUser
from rooms.permissions import IsAdminUser


class CourseViewSet(viewsets.ModelViewSet):
    """
    API endpoint para gestionar cursos (CRUD completo)
    Solo administradores pueden crear, editar y eliminar
    """
    
    def get_serializer_class(self):
        """Seleccionar serializer según la acción"""
        if self.action == 'list':
            return CourseListSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return CourseCreateUpdateSerializer
        else:
            return CourseDetailSerializer
    
    def get_queryset(self):
        """Retorna cursos según el rol del usuario"""
        if self.request.user.role == 'admin':
            return Course.objects.all().select_related('room', 'schedule', 'schedule__user', 'created_by')
        else:
            # Monitores solo ven sus cursos asignados
            return Course.objects.filter(schedule__user=self.request.user).select_related('room', 'schedule', 'schedule__user')
    
    def get_permissions(self):
        """Define permisos según la acción"""
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            # Solo admins pueden crear, editar y eliminar
            permission_classes = [IsAuthenticated, IsAdminUser]
        else:
            # Usuarios verificados pueden listar y ver detalles
            permission_classes = [IsAuthenticated, IsVerifiedUser]
        
        return [permission() for permission in permission_classes]
    
    def perform_create(self, serializer):
        """Crear curso y registrar en historial"""
        course = serializer.save()
        CourseHistoryService.record_creation(course, self.request.user)
    
    def perform_update(self, serializer):
        """Actualizar curso y registrar cambios en historial"""
        # Guardar valores anteriores para el historial
        old_values = {}
        if serializer.instance:
            fields_to_track = ['name', 'description', 'status', 'start_datetime', 'end_datetime']
            for field in fields_to_track:
                old_values[field] = getattr(serializer.instance, field)
        
        course = serializer.save()
        CourseHistoryService.record_update(course, old_values, self.request.user)
    
    def perform_destroy(self, instance):
        """Eliminar curso y registrar en historial"""
        CourseHistoryService.record_deletion(instance, self.request.user)
        instance.delete()
    
    @action(detail=False, methods=['get'])
    def my_courses(self, request):
        """Obtener cursos asignados al monitor autenticado"""
        if request.user.role != 'monitor':
            return Response({
                'error': 'Solo los monitores pueden ver sus cursos asignados'
            }, status=status.HTTP_403_FORBIDDEN)
        
        courses = Course.objects.filter(
            schedule__user=request.user,
            status__in=[Course.SCHEDULED, Course.IN_PROGRESS]
        ).select_related('room', 'schedule', 'schedule__user').order_by('start_datetime')
        
        serializer = MonitorCourseSerializer(courses, many=True)
        
        return Response({
            'courses': serializer.data,
            'total_count': courses.count()
        }, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['get'])
    def upcoming(self, request):
        """Obtener cursos próximos (siguientes 7 días)"""
        now = timezone.now()
        upcoming_courses = self.get_queryset().filter(
            start_datetime__gte=now,
            start_datetime__lte=now + timedelta(days=7),
            status=Course.SCHEDULED
        ).order_by('start_datetime')
        
        serializer = self.get_serializer(upcoming_courses, many=True)
        
        return Response({
            'upcoming_courses': serializer.data,
            'total_count': upcoming_courses.count()
        }, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['get'])
    def current(self, request):
        """Obtener cursos actuales (en curso)"""
        now = timezone.now()
        current_courses = self.get_queryset().filter(
            start_datetime__lte=now,
            end_datetime__gte=now,
            status__in=[Course.SCHEDULED, Course.IN_PROGRESS]
        ).order_by('start_datetime')
        
        serializer = self.get_serializer(current_courses, many=True)
        
        return Response({
            'current_courses': serializer.data,
            'total_count': current_courses.count()
        }, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['get'])
    def history(self, request, pk=None):
        """Obtener historial de cambios de un curso"""
        course = self.get_object()
        history = CourseHistory.objects.filter(course=course).select_related('changed_by')
        
        serializer = CourseHistorySerializer(history, many=True)
        
        return Response({
            'course_name': course.name,
            'history': serializer.data,
            'total_changes': history.count()
        }, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['get'])
    def calendar_view(self, request):
        """Vista de calendario que incluye tanto turnos como cursos"""
        from schedule.models import Schedule
        from schedule.serializers import ScheduleListSerializer
        
        # Obtener parámetros de fecha
        from django.utils.dateparse import parse_date
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        
        if start_date:
            start_date = parse_date(start_date)
        else:
            start_date = timezone.now().date()
            
        if end_date:
            end_date = parse_date(end_date)
        else:
            start_date = timezone.now().date()
            end_date = start_date + timedelta(days=7)
        
        # Convertir a datetime para filtros
        start_datetime = timezone.make_aware(datetime.combine(start_date, datetime.min.time()))
        end_datetime = timezone.make_aware(datetime.combine(end_date, datetime.max.time()))
        
        # Obtener turnos en el rango de fechas
        schedules = Schedule.objects.filter(
            start_datetime__gte=start_datetime,
            start_datetime__lte=end_datetime,
            status=Schedule.ACTIVE
        ).select_related('user', 'room').order_by('start_datetime')
        
        # Obtener cursos en el rango de fechas
        courses = self.get_queryset().filter(
            start_datetime__gte=start_datetime,
            start_datetime__lte=end_datetime
        ).select_related('room', 'schedule', 'schedule__user').order_by('start_datetime')
        
        # Serializar datos
        schedule_serializer = ScheduleListSerializer(schedules, many=True)
        course_serializer = self.get_serializer(courses, many=True)
        
        # Combinar eventos para vista de calendario
        calendar_events = []
        
        # Agregar turnos como eventos
        for schedule in schedule_serializer.data:
            calendar_events.append({
                'id': f"schedule_{schedule['id']}",
                'type': 'schedule',
                'title': f"Turno - {schedule['user_full_name']}",
                'start': schedule['start_datetime'],
                'end': schedule['end_datetime'],
                'room': schedule['room_name'],
                'monitor': schedule['user_full_name'],
                'description': schedule.get('notes', ''),
                'status': schedule['status']
            })
        
        # Agregar cursos como eventos
        for course in course_serializer.data:
            calendar_events.append({
                'id': f"course_{course['id']}",
                'type': 'course',
                'title': course['name'],
                'start': course['start_datetime'],
                'end': course['end_datetime'],
                'room': course['room_name'],
                'monitor': course['monitor_name'],
                'description': course.get('description', ''),
                'status': course['status']
            })
        
        # Ordenar eventos por fecha de inicio
        calendar_events.sort(key=lambda x: x['start'])
        
        return Response({
            'calendar_events': calendar_events,
            'date_range': {
                'start_date': start_date.isoformat(),
                'end_date': end_date.isoformat()
            },
            'summary': {
                'total_events': len(calendar_events),
                'schedules_count': len(schedule_serializer.data),
                'courses_count': len(course_serializer.data)
            }
        }, status=status.HTTP_200_OK)


@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAdminUser])
def admin_courses_overview_view(request):
    """
    Vista para que admins vean resumen general de todos los cursos
    """
    now = timezone.now()
    
    # Estadísticas generales
    total_courses = Course.objects.count()
    active_courses = Course.objects.filter(status__in=[Course.SCHEDULED, Course.IN_PROGRESS]).count()
    current_courses = Course.objects.filter(
        start_datetime__lte=now,
        end_datetime__gte=now,
        status__in=[Course.SCHEDULED, Course.IN_PROGRESS]
    ).count()
    upcoming_courses = Course.objects.filter(
        start_datetime__gt=now,
        start_datetime__lte=now + timedelta(days=7),
        status=Course.SCHEDULED
    ).count()
    
    # Cursos por estado
    courses_by_status = {}
    for choice in Course.STATUS_CHOICES:
        status_key = choice[0]
        status_label = choice[1]
        count = Course.objects.filter(status=status_key).count()
        courses_by_status[status_key] = {
            'label': status_label,
            'count': count
        }
    
    # Próximos cursos (siguientes 3 días)
    next_courses = Course.objects.filter(
        start_datetime__gte=now,
        start_datetime__lte=now + timedelta(days=3),
        status=Course.SCHEDULED
    ).select_related('room', 'schedule', 'schedule__user').order_by('start_datetime')[:10]
    
    next_courses_data = CourseListSerializer(next_courses, many=True).data
    
    return Response({
        'overview': {
            'total_courses': total_courses,
            'active_courses': active_courses,
            'current_courses': current_courses,
            'upcoming_courses': upcoming_courses
        },
        'courses_by_status': courses_by_status,
        'next_courses': next_courses_data,
        'timestamp': now
    }, status=status.HTTP_200_OK)
