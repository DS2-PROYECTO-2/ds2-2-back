from rest_framework import serializers
from .models import Attendance, Incapacity


class AttendanceSerializer(serializers.ModelSerializer):
    """
    Serializer para el modelo Attendance
    """
    uploaded_by_username = serializers.ReadOnlyField(source='uploaded_by.username')
    reviewed_by_username = serializers.ReadOnlyField(source='reviewed_by.username', read_only=True)
    
    class Meta:
        model = Attendance
        fields = ['id', 'title', 'date', 'uploaded_by', 'uploaded_by_username', 'file', 'description',
                  'reviewed', 'reviewed_by', 'reviewed_by_username', 'created_at', 'updated_at']
        read_only_fields = ['id', 'uploaded_by', 'reviewed', 'reviewed_by', 'created_at', 'updated_at']
    
    def create(self, validated_data):
        """Asignar automáticamente el usuario actual como uploaded_by"""
        validated_data['uploaded_by'] = self.context['request'].user
        return super().create(validated_data)


class IncapacitySerializer(serializers.ModelSerializer):
    """
    Serializer para el modelo Incapacity
    """
    user_username = serializers.ReadOnlyField(source='user.username')
    approved_by_username = serializers.ReadOnlyField(source='approved_by.username', read_only=True)
    
    class Meta:
        model = Incapacity
        fields = ['id', 'user', 'user_username', 'start_date', 'end_date', 'document', 'description',
                  'approved', 'approved_by', 'approved_by_username', 'created_at', 'updated_at']
        read_only_fields = ['id', 'approved', 'approved_by', 'created_at', 'updated_at']
    
    def validate(self, data):
        """Validar que la fecha de inicio sea anterior a la fecha de fin"""
        if 'start_date' in data and 'end_date' in data:
            if data['start_date'] > data['end_date']:
                raise serializers.ValidationError("La fecha de inicio debe ser anterior a la fecha de finalización.")
        return data
    
    def create(self, validated_data):
        """Asignar automáticamente el usuario actual como user"""
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)

