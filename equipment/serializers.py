from rest_framework import serializers
from django.utils import timezone
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
    reported_by_name = serializers.SerializerMethodField(read_only=True)
    """
    Serializer para el modelo EquipmentReport
    """
    class Meta:
        model = EquipmentReport
        fields = ['id', 'equipment', 'reported_by', 'reported_by_name', 'issue_description', 'issue_type', 'reported_date',
                  'resolved', 'resolved_date', 'resolution_notes', 'created_at', 'updated_at']
        read_only_fields = ['id', 'reported_date', 'resolved_date', 'created_at', 'updated_at']
        # Agregar lógica para asignar usuario actual como reported_by, etc.

    def update(self, instance, validated_data):
        resolved_before = instance.resolved
        resolved_after = validated_data.get('resolved', resolved_before)

        instance = super().update(instance, validated_data)

        # Autocalcular resolved_date cuando cambia resolved
        if resolved_after and not resolved_before:
            instance.resolved_date = timezone.now()
            instance.save(update_fields=['resolved_date'])
        elif not resolved_after and resolved_before:
            instance.resolved_date = None
            instance.save(update_fields=['resolved_date'])

        return instance

    def get_reported_by_name(self, obj):
        try:
            full_name = obj.reported_by.get_full_name()
            return full_name or obj.reported_by.username
        except Exception:
            return None