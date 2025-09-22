from rest_framework import serializers
from .models import Notification


class NotificationSerializer(serializers.ModelSerializer):
    """
    Serializador para el modelo de Notificación
    """
    class Meta:
        model = Notification
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']