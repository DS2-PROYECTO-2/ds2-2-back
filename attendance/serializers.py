from rest_framework import serializers
from .models import Attendance, Incapacity


class AttendanceSerializer(serializers.ModelSerializer):
    """
    Serializer para el modelo Attendance
    """
    class Meta:
        model = Attendance
        fields = ['id', 'title', 'date', 'uploaded_by', 'file', 'description',
                  'upload_timestamp', 'reviewed', 'reviewed_by', 'created_at', 'updated_at']
        read_only_fields = ['id', 'upload_timestamp', 'reviewed', 'reviewed_by', 'created_at', 'updated_at']
        # Agregar lógica para asignar usuario actual como uploaded_by, etc.


class IncapacitySerializer(serializers.ModelSerializer):
    """
    Serializer para el modelo Incapacity
    """
    class Meta:
        model = Incapacity
        fields = ['id', 'user', 'start_date', 'end_date', 'document', 'description',
                  'approved', 'approved_by', 'created_at', 'updated_at']
        read_only_fields = ['id', 'approved', 'approved_by', 'created_at', 'updated_at']
        # Agregar lógica para validar fechas, calcular duración, etc.