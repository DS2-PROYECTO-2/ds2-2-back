from rest_framework import serializers
from .models import ExportJob
from users.models import User
from rooms.models import RoomEntry
from attendance.models import Attendance, Incapacity
from schedule.models import Schedule


class ExportJobSerializer(serializers.ModelSerializer):
    """
    Serializer para trabajos de exportación
    """
    requested_by_name = serializers.CharField(source='requested_by.get_full_name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    export_type_display = serializers.CharField(source='get_export_type_display', read_only=True)
    format_display = serializers.CharField(source='get_format_display', read_only=True)
    file_url = serializers.SerializerMethodField()
    file_size_mb = serializers.SerializerMethodField()
    
    class Meta:
        model = ExportJob
        fields = [
            'id', 'title', 'export_type', 'export_type_display', 'format', 'format_display',
            'status', 'status_display', 'start_date', 'end_date', 'monitor_ids',
            'file', 'file_url', 'file_size', 'file_size_mb', 'requested_by', 'requested_by_name',
            'created_at', 'updated_at', 'completed_at', 'error_message'
        ]
        read_only_fields = [
            'id', 'status', 'file', 'file_size', 'requested_by', 'created_at', 
            'updated_at', 'completed_at', 'error_message'
        ]
    
    def get_file_url(self, obj):
        """Obtiene la URL del archivo si existe"""
        if obj.file:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.file.url)
        return None
    
    def get_file_size_mb(self, obj):
        """Convierte el tamaño del archivo a MB"""
        if obj.file_size:
            return round(obj.file_size / (1024 * 1024), 2)
        return None


class MonitorExportSerializer(serializers.ModelSerializer):
    """
    Serializer para exportar datos de monitores
    """
    full_name = serializers.CharField(source='get_full_name', read_only=True)
    role_display = serializers.CharField(source='get_role_display', read_only=True)
    is_verified_display = serializers.SerializerMethodField()
    total_room_entries = serializers.SerializerMethodField()
    total_hours_worked = serializers.SerializerMethodField()
    total_schedules = serializers.SerializerMethodField()
    total_incapacities = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name', 'full_name',
            'identification', 'phone', 'role', 'role_display', 'is_verified',
            'is_verified_display', 'created_at', 'updated_at',
            'total_room_entries', 'total_hours_worked', 'total_schedules', 'total_incapacities'
        ]
    
    def get_is_verified_display(self, obj):
        """Convierte el booleano a texto"""
        return "Sí" if obj.is_verified else "No"
    
    def get_total_room_entries(self, obj):
        """Cuenta el total de entradas a salas"""
        return obj.room_entries.count()
    
    def get_total_hours_worked(self, obj):
        """Calcula el total de horas trabajadas"""
        entries = obj.room_entries.filter(exit_time__isnull=False)
        total_hours = 0
        for entry in entries:
            if entry.duration_hours:
                total_hours += entry.duration_hours
        return round(total_hours, 2)
    
    def get_total_schedules(self, obj):
        """Cuenta el total de turnos asignados"""
        return obj.schedules.count()
    
    def get_total_incapacities(self, obj):
        """Cuenta el total de incapacidades"""
        return obj.incapacities.count()


class RoomEntryExportSerializer(serializers.ModelSerializer):
    """
    Serializer para exportar datos de entradas a salas
    """
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    user_identification = serializers.CharField(source='user.identification', read_only=True)
    room_name = serializers.CharField(source='room.name', read_only=True)
    room_code = serializers.CharField(source='room.code', read_only=True)
    duration_hours = serializers.ReadOnlyField()
    is_active_display = serializers.SerializerMethodField()
    
    class Meta:
        model = RoomEntry
        fields = [
            'id', 'user', 'user_name', 'user_identification', 'room', 'room_name', 'room_code',
            'entry_time', 'exit_time', 'duration_hours', 'active', 'is_active_display',
            'notes', 'created_at', 'updated_at'
        ]
    
    def get_is_active_display(self, obj):
        """Convierte el booleano a texto"""
        return "Sí" if obj.is_active else "No"


class ScheduleExportSerializer(serializers.ModelSerializer):
    """
    Serializer para exportar datos de turnos
    """
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    user_identification = serializers.CharField(source='user.identification', read_only=True)
    room_name = serializers.CharField(source='room.name', read_only=True)
    room_code = serializers.CharField(source='room.code', read_only=True)
    duration_hours = serializers.ReadOnlyField()
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    is_active_display = serializers.SerializerMethodField()
    is_current_display = serializers.SerializerMethodField()
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)
    
    class Meta:
        model = Schedule
        fields = [
            'id', 'user', 'user_name', 'user_identification', 'room', 'room_name', 'room_code',
            'start_datetime', 'end_datetime', 'duration_hours', 'status', 'status_display',
            'recurring', 'notes', 'created_by', 'created_by_name', 'is_active_display',
            'is_current_display', 'created_at', 'updated_at'
        ]
    
    def get_is_active_display(self, obj):
        """Convierte el booleano a texto"""
        return "Sí" if obj.is_active else "No"
    
    def get_is_current_display(self, obj):
        """Convierte el booleano a texto"""
        return "Sí" if obj.is_current else "No"


class AttendanceExportSerializer(serializers.ModelSerializer):
    """
    Serializer para exportar datos de asistencia
    """
    uploaded_by_name = serializers.CharField(source='uploaded_by.get_full_name', read_only=True)
    reviewed_by_name = serializers.CharField(source='reviewed_by.get_full_name', read_only=True)
    reviewed_display = serializers.SerializerMethodField()
    
    class Meta:
        model = Attendance
        fields = [
            'id', 'title', 'date', 'uploaded_by', 'uploaded_by_name', 'file',
            'description', 'reviewed', 'reviewed_display', 'reviewed_by', 'reviewed_by_name',
            'created_at', 'updated_at'
        ]
    
    def get_reviewed_display(self, obj):
        """Convierte el booleano a texto"""
        return "Sí" if obj.reviewed else "No"


class IncapacityExportSerializer(serializers.ModelSerializer):
    """
    Serializer para exportar datos de incapacidades
    """
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    user_identification = serializers.CharField(source='user.identification', read_only=True)
    approved_by_name = serializers.CharField(source='approved_by.get_full_name', read_only=True)
    duration_days = serializers.ReadOnlyField()
    approved_display = serializers.SerializerMethodField()
    
    class Meta:
        model = Incapacity
        fields = [
            'id', 'user', 'user_name', 'user_identification', 'start_date', 'end_date',
            'duration_days', 'document', 'description', 'approved', 'approved_display',
            'approved_by', 'approved_by_name', 'created_at', 'updated_at'
        ]
    
    def get_approved_display(self, obj):
        """Convierte el booleano a texto"""
        return "Sí" if obj.approved else "No"

