from rest_framework import serializers
from .models import Equipment, EquipmentReport


class EquipmentSerializer(serializers.ModelSerializer):
    """
    Serializer para el modelo Equipment
    """
    class Meta:
        model = Equipment
        fields = ['id', 'serial_number', 'name', 'description', 'room', 
                  'status', 'acquisition_date', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class EquipmentReportSerializer(serializers.ModelSerializer):
    """
    Serializer para el modelo EquipmentReport
    """
    class Meta:
        model = EquipmentReport
        fields = ['id', 'equipment', 'reported_by', 'issue_description', 'reported_date',
                  'resolved', 'resolved_date', 'resolution_notes', 'created_at', 'updated_at']
        read_only_fields = ['id', 'reported_date', 'resolved', 'resolved_date', 'created_at', 'updated_at']
        # Agregar lógica para asignar usuario actual como reported_by, etc.