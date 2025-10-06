from rest_framework import serializers
from django.utils import timezone
from .models import Schedule
from users.models import User
from rooms.models import Room


class ScheduleListSerializer(serializers.ModelSerializer):
    """
    Serializador para listar turnos (información básica)
    """
    user_full_name = serializers.CharField(source='user.get_full_name', read_only=True)
    user_username = serializers.CharField(source='user.username', read_only=True)
    room_name = serializers.CharField(source='room.name', read_only=True)
    room_code = serializers.CharField(source='room.code', read_only=True)
    duration_hours = serializers.ReadOnlyField()
    is_current = serializers.ReadOnlyField()
    is_upcoming = serializers.ReadOnlyField()
    
    class Meta:
        model = Schedule
        fields = [
            'id', 'start_datetime', 'end_datetime', 'status', 'recurring', 'notes',
            'user_full_name', 'user_username', 'room_name', 'room_code',
            'duration_hours', 'is_current', 'is_upcoming', 'created_at', 'updated_at'
        ]


class ScheduleDetailSerializer(serializers.ModelSerializer):
    """
    Serializador para detalle de turno (información completa)
    """
    user_details = serializers.SerializerMethodField()
    room_details = serializers.SerializerMethodField()
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)
    duration_hours = serializers.ReadOnlyField()
    is_current = serializers.ReadOnlyField()
    is_upcoming = serializers.ReadOnlyField()
    has_compliance = serializers.ReadOnlyField()
    room_entries = serializers.SerializerMethodField()
    
    class Meta:
        model = Schedule
        fields = [
            'id', 'start_datetime', 'end_datetime', 'status', 'recurring', 'notes',
            'user_details', 'room_details', 'created_by_name', 'duration_hours',
            'is_current', 'is_upcoming', 'has_compliance', 'room_entries',
            'created_at', 'updated_at'
        ]
    
    def get_user_details(self, obj):
        return {
            'id': obj.user.id,
            'username': obj.user.username,
            'full_name': obj.user.get_full_name(),
            'email': obj.user.email,
            'phone': obj.user.phone
        }
    
    def get_room_details(self, obj):
        return {
            'id': obj.room.id,
            'name': obj.room.name,
            'code': obj.room.code,
            'capacity': obj.room.capacity,
            'description': obj.room.description
        }
    
    def get_room_entries(self, obj):
        entries = obj.get_room_entries()
        return [{
            'id': entry.id,
            'entry_time': entry.entry_time,
            'exit_time': entry.exit_time,
            'notes': entry.notes
        } for entry in entries]


class ScheduleCreateUpdateSerializer(serializers.ModelSerializer):
    """
    Serializador para crear y actualizar turnos (solo admins)
    """
    
    class Meta:
        model = Schedule
        fields = [
            'user', 'room', 'start_datetime', 'end_datetime', 
            'status', 'recurring', 'notes'
        ]
    
    def validate(self, data):
        """Validaciones personalizadas"""
        start_datetime = data.get('start_datetime')
        end_datetime = data.get('end_datetime')
        user = data.get('user')
        
        # Validar fechas
        if start_datetime and end_datetime:
            if end_datetime <= start_datetime:
                raise serializers.ValidationError({
                    'end_datetime': 'La fecha de fin debe ser posterior a la fecha de inicio.'
                })
            
            # Validar duración máxima
            duration = end_datetime - start_datetime
            if duration.total_seconds() > 12 * 3600:  # 12 horas
                raise serializers.ValidationError({
                    'end_datetime': 'Un turno no puede exceder 12 horas de duración.'
                })
            
            # Validar que no sea en el pasado (solo para creación)
            if not self.instance and start_datetime < timezone.now():
                raise serializers.ValidationError({
                    'start_datetime': 'No se pueden crear turnos en fechas pasadas.'
                })
        
        # Validar que el usuario sea monitor
        if user and hasattr(user, 'role') and user.role != 'monitor':
            raise serializers.ValidationError({
                'user': 'Solo se pueden asignar turnos a usuarios con rol de monitor.'
            })
        
        # Validar que el usuario esté verificado
        if user and not user.is_verified:
            raise serializers.ValidationError({
                'user': 'Solo se pueden asignar turnos a monitores verificados.'
            })
        
        return data
    
    def validate_user(self, value):
        """Validar que el usuario sea un monitor verificado"""
        if not hasattr(value, 'role') or value.role != 'monitor':
            raise serializers.ValidationError('Solo se pueden asignar turnos a monitores.')
        
        if not value.is_verified:
            raise serializers.ValidationError('Solo se pueden asignar turnos a monitores verificados.')
        
        return value
    
    def create(self, validated_data):
        """Crear turno asignando el admin que lo crea"""
        validated_data['created_by'] = self.context['request'].user
        return super().create(validated_data)


class MonitorScheduleSerializer(serializers.ModelSerializer):
    """
    Serializador para que los monitores vean sus propios turnos
    """
    room_name = serializers.CharField(source='room.name', read_only=True)
    room_code = serializers.CharField(source='room.code', read_only=True)
    room_description = serializers.CharField(source='room.description', read_only=True)
    duration_hours = serializers.ReadOnlyField()
    is_current = serializers.ReadOnlyField()
    is_upcoming = serializers.ReadOnlyField()
    has_compliance = serializers.ReadOnlyField()
    
    class Meta:
        model = Schedule
        fields = [
            'id', 'start_datetime', 'end_datetime', 'status', 'recurring', 'notes',
            'room_name', 'room_code', 'room_description', 'duration_hours',
            'is_current', 'is_upcoming', 'has_compliance', 'created_at'
        ]