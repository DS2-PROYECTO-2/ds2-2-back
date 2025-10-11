from rest_framework import serializers
from django.utils import timezone
from .models import Course, CourseHistory
from .services import CourseValidationService


class CourseListSerializer(serializers.ModelSerializer):
    """
    Serializador para listar cursos (información básica)
    """
    monitor_name = serializers.CharField(source='monitor.get_full_name', read_only=True)
    monitor_username = serializers.CharField(source='monitor.username', read_only=True)
    room_name = serializers.CharField(source='room.name', read_only=True)
    room_code = serializers.CharField(source='room.code', read_only=True)
    duration_hours = serializers.ReadOnlyField()
    is_current = serializers.ReadOnlyField()
    is_upcoming = serializers.ReadOnlyField()
    
    class Meta:
        model = Course
        fields = [
            'id', 'name', 'start_datetime', 'end_datetime', 'status',
            'monitor_name', 'monitor_username', 'room_name', 'room_code',
            'duration_hours', 'is_current', 'is_upcoming', 'created_at'
        ]


class CourseDetailSerializer(serializers.ModelSerializer):
    """
    Serializador para detalle de curso (información completa)
    """
    monitor_name = serializers.CharField(source='monitor.get_full_name', read_only=True)
    monitor_username = serializers.CharField(source='monitor.username', read_only=True)
    room_name = serializers.CharField(source='room.name', read_only=True)
    room_code = serializers.CharField(source='room.code', read_only=True)
    room_description = serializers.CharField(source='room.description', read_only=True)
    schedule_id = serializers.IntegerField(source='schedule.id', read_only=True)
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)
    duration_hours = serializers.ReadOnlyField()
    is_current = serializers.ReadOnlyField()
    is_upcoming = serializers.ReadOnlyField()
    is_active = serializers.ReadOnlyField()
    
    class Meta:
        model = Course
        fields = [
            'id', 'name', 'description', 'room', 'schedule', 
            'start_datetime', 'end_datetime', 'status',
            'monitor_name', 'monitor_username', 'room_name', 'room_code', 'room_description',
            'schedule_id', 'created_by_name', 'duration_hours',
            'is_current', 'is_upcoming', 'is_active', 'created_at', 'updated_at'
        ]


class CourseCreateUpdateSerializer(serializers.ModelSerializer):
    """
    Serializador para crear y actualizar cursos (solo admins)
    """
    
    class Meta:
        model = Course
        fields = [
            'id', 'name', 'description', 'room', 'schedule',
            'start_datetime', 'end_datetime', 'status', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def validate(self, data):
        """Validaciones personalizadas usando el servicio de validación"""
        # Validar que el schedule tenga un monitor verificado
        if 'schedule' in data:
            schedule = data['schedule']
            if not schedule.user or schedule.user.role != 'monitor' or not schedule.user.is_verified:
                raise serializers.ValidationError({
                    'schedule': 'El turno debe tener asignado un monitor verificado.'
                })
        
        # Validar fechas
        if 'start_datetime' in data and 'end_datetime' in data:
            start = data['start_datetime']
            end = data['end_datetime']
            
            if end <= start:
                raise serializers.ValidationError({
                    'end_datetime': 'La fecha de fin debe ser posterior a la fecha de inicio.'
                })
        
        # Usar el servicio de validación para validaciones de negocio
        if all(key in data for key in ['room', 'schedule', 'start_datetime', 'end_datetime']):
            try:
                CourseValidationService.validate_course_creation(
                    room=data['room'],
                    monitor=data['schedule'].user,  # Obtener monitor del schedule
                    schedule=data['schedule'],
                    start_datetime=data['start_datetime'],
                    end_datetime=data['end_datetime'],
                    exclude_course_id=self.instance.id if self.instance else None
                )
            except Exception as e:
                raise serializers.ValidationError(str(e))
        
        return data
    
    def create(self, validated_data):
        """Crear curso asignando el admin que lo crea"""
        validated_data['created_by'] = self.context['request'].user
        return super().create(validated_data)


class MonitorCourseSerializer(serializers.ModelSerializer):
    """
    Serializador para que los monitores vean sus cursos asignados
    """
    room_name = serializers.CharField(source='room.name', read_only=True)
    room_code = serializers.CharField(source='room.code', read_only=True)
    room_description = serializers.CharField(source='room.description', read_only=True)
    duration_hours = serializers.ReadOnlyField()
    is_current = serializers.ReadOnlyField()
    is_upcoming = serializers.ReadOnlyField()
    
    class Meta:
        model = Course
        fields = [
            'id', 'name', 'description', 'start_datetime', 'end_datetime', 'status',
            'room_name', 'room_code', 'room_description', 'duration_hours',
            'is_current', 'is_upcoming', 'created_at'
        ]


class CourseHistorySerializer(serializers.ModelSerializer):
    """
    Serializador para el historial de cambios de cursos
    """
    changed_by_name = serializers.CharField(source='changed_by.get_full_name', read_only=True)
    action_display = serializers.CharField(source='get_action_display', read_only=True)
    
    class Meta:
        model = CourseHistory
        fields = [
            'id', 'action', 'action_display', 'changes', 
            'changed_by_name', 'timestamp'
        ]