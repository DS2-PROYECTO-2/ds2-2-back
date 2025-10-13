from rest_framework import serializers
from django.utils import timezone
from .models import Room, RoomEntry


class RoomSerializer(serializers.ModelSerializer):
    """
    Serializador para el modelo de Sala (Sprint 1)
    """
    occupants_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Room
        fields = [
            'id', 'name', 'code', 'capacity', 'description', 
            'is_active', 'created_at', 'updated_at', 'occupants_count'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_occupants_count(self, obj):
        """Número actual de ocupantes en la sala"""
        return RoomEntry.objects.filter(room=obj, exit_time__isnull=True).count()


class RoomCreateUpdateSerializer(serializers.ModelSerializer):
    """
    Serializador específico para crear/actualizar salas - solo administradores
    """
    
    class Meta:
        model = Room
        fields = ['name', 'code', 'capacity', 'description', 'is_active']
    
    def validate_name(self, value):
        """Validar que el nombre de la sala sea único"""
        # En actualización, excluir la instancia actual
        if self.instance:
            if Room.objects.filter(name=value).exclude(id=self.instance.id).exists():
                raise serializers.ValidationError("Ya existe una sala con este nombre.")
        else:
            if Room.objects.filter(name=value).exists():
                raise serializers.ValidationError("Ya existe una sala con este nombre.")
        return value
    
    def validate_code(self, value):
        """Validar que el código de la sala sea único"""
        if self.instance:
            if Room.objects.filter(code=value).exclude(id=self.instance.id).exists():
                raise serializers.ValidationError("Ya existe una sala con este código.")
        else:
            if Room.objects.filter(code=value).exists():
                raise serializers.ValidationError("Ya existe una sala con este código.")
        return value
    
    def validate_capacity(self, value):
        """Validar que la capacidad sea válida"""
        if value < 1:
            raise serializers.ValidationError("La capacidad debe ser mayor a 0.")
        if value > 1000:
            raise serializers.ValidationError("La capacidad no puede ser mayor a 1000.")
        return value


class RoomEntrySerializer(serializers.ModelSerializer):
    """
    Serializador para el modelo de Registro de Entrada/Salida (Sprint 2)
    """
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    user_username = serializers.CharField(source='user.username', read_only=True)
    room_name = serializers.CharField(source='room.name', read_only=True)
    room_code = serializers.CharField(source='room.code', read_only=True)
    user_identification = serializers.CharField(source='user.identification', read_only=True)
    duration_hours = serializers.ReadOnlyField()
    duration_minutes = serializers.ReadOnlyField()
    duration_formatted = serializers.CharField(source='get_duration_formatted', read_only=True)
    is_active = serializers.ReadOnlyField()
    
    class Meta:
        model = RoomEntry
        fields = [
            'id', 'user', 'room', 'user_name', 'user_username',
            'room_name', 'room_code', 'user_identification', 'entry_time', 'exit_time',
            'duration_hours', 'duration_minutes', 'duration_formatted',
            'is_active', 'notes', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'entry_time', 'duration_hours', 'duration_minutes',
            'duration_formatted', 'is_active', 'created_at', 'updated_at'
        ]


class RoomEntryCreateSerializer(serializers.ModelSerializer):
    """
    Serializador específico para crear entradas (solo requiere room)
    """
    class Meta:
        model = RoomEntry
        fields = ['room', 'notes']
    
    def create(self, validated_data):
        # El usuario se asigna automáticamente desde request.user
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class RoomEntryExitSerializer(serializers.ModelSerializer):
    """
    Serializador específico para registrar salida
    """
    class Meta:
        model = RoomEntry
        fields = ['notes']
    
    def update(self, instance, validated_data):
        # Solo actualizar si no tiene exit_time previo
        if not instance.exit_time:
            instance.exit_time = timezone.now()
            # Actualizar notes si se proporcionan
            if 'notes' in validated_data:
                instance.notes = validated_data['notes']
            instance.save()
        return instance


# Serializers adicionales para reportes y estadísticas

class TurnComparisonSerializer(serializers.Serializer):
    """
    Serializador para comparación de turnos vs registros
    """
    usuario = serializers.CharField()
    turno = serializers.CharField()
    registro = serializers.CharField()
    diferencia = serializers.IntegerField()
    diferencia_formateada = serializers.CharField()
    estado = serializers.CharField()
    notas = serializers.CharField()
    sala = serializers.CharField()
    fecha = serializers.CharField()


class EntryValidationSerializer(serializers.Serializer):
    """
    Serializador para validación de acceso anticipado
    """
    permitido = serializers.BooleanField()
    diferencia = serializers.FloatField()
    mensaje = serializers.CharField()