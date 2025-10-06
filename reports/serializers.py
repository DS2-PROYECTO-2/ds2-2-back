from rest_framework import serializers
from .models import Report


class ReportSerializer(serializers.ModelSerializer):
    """
    Serializador para el modelo de Reportes
    """
    class Meta:
        model = Report
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']