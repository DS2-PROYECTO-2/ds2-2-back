from rest_framework import serializers
from .models import Room


class RoomSerializer(serializers.ModelSerializer):
    """
    Serializador para el modelo de Sala (Sprint 1)
    """
    class Meta:
        model = Room
        fields = [
            'id', 'name', 'code', 'capacity', 'description', 
            'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']