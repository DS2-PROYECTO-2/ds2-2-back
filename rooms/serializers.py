from rest_framework import serializers
from .models import Room, RoomEntry


class RoomSerializer(serializers.ModelSerializer):
    """
    Serializer para el modelo Room
    """
    class Meta:
        model = Room
        fields = ['id', 'name', 'code', 'capacity', 'description', 'is_active', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class RoomEntrySerializer(serializers.ModelSerializer):
    """
    Serializer para el modelo RoomEntry
    """
    class Meta:
        model = RoomEntry
        fields = ['id', 'user', 'room', 'entry_time', 'exit_time', 'notes', 'created_at', 'updated_at']
        read_only_fields = ['id', 'entry_time', 'created_at', 'updated_at']
        # Agregar métodos para calcular duración, validar simultaneidad, etc.