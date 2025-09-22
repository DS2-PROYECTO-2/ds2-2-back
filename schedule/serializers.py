from rest_framework import serializers
from .models import Schedule


class ScheduleSerializer(serializers.ModelSerializer):
    """
    Serializador para el modelo de Turnos
    """
    class Meta:
        model = Schedule
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']