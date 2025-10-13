from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Notification

class NotificationSerializer(serializers.ModelSerializer):
    recipient_name = serializers.CharField(source='user.get_full_name', read_only=True)
    recipient_username = serializers.CharField(source='user.username', read_only=True)
    is_read = serializers.BooleanField(source='read', read_only=True)
    monitor_id = serializers.IntegerField(source='user.id', read_only=True)
    monitor_name = serializers.CharField(source='user.get_full_name', read_only=True)
    # Permitir creación desde API para admins: user oculto y tipo requerido
    user = serializers.PrimaryKeyRelatedField(queryset=get_user_model().objects.all(), required=False, write_only=True)
    notification_type = serializers.ChoiceField(choices=Notification.TYPE_CHOICES, write_only=True, required=True)
    
    class Meta:
        model = Notification
        fields = [
            'id', 'notification_type', 'title', 'message', 'read', 'is_read', 'created_at',
            'recipient_name', 'recipient_username', 'monitor_id', 'monitor_name', 'user', 'related_object_id'
        ]
        read_only_fields = ['created_at', 'updated_at']

    def create(self, validated_data):
        # Si no se pasa user explícito, usar el request.user
        request = self.context.get('request') if self.context else None
        user = validated_data.pop('user', None)
        if user is None and request is not None:
            user = request.user
        # Crear notificación con usuario y tipo
        return Notification.objects.create(user=user, **validated_data)

class ExcessiveHoursNotificationSerializer(serializers.ModelSerializer):
    """
    Serializer específico para notificaciones de exceso de horas con información detallada
    """
    recipient_name = serializers.CharField(source='user.get_full_name', read_only=True)
    recipient_username = serializers.CharField(source='user.username', read_only=True)
    monitor_name = serializers.SerializerMethodField()
    monitor_username = serializers.SerializerMethodField()
    room_name = serializers.SerializerMethodField()
    duration_hours = serializers.SerializerMethodField()
    excess_hours = serializers.SerializerMethodField()
    
    class Meta:
        model = Notification
        fields = [
            'id', 'title', 'message', 'notification_type',
            'read', 'created_at', 'recipient_name', 'recipient_username',
            'monitor_name', 'monitor_username', 'room_name', 
            'duration_hours', 'excess_hours', 'related_object_id'
        ]
        read_only_fields = ['created_at']
    
    def get_monitor_name(self, obj):
        """Obtener nombre del monitor desde el objeto relacionado"""
        if obj.related_object_id and obj.notification_type == 'excessive_hours':
            try:
                from rooms.models import RoomEntry
                entry = RoomEntry.objects.get(id=obj.related_object_id)
                return entry.user.get_full_name()
            except RoomEntry.DoesNotExist:
                pass
        return 'N/A'
    
    def get_monitor_username(self, obj):
        """Obtener username del monitor desde el objeto relacionado"""
        if obj.related_object_id and obj.notification_type == 'excessive_hours':
            try:
                from rooms.models import RoomEntry
                entry = RoomEntry.objects.get(id=obj.related_object_id)
                return entry.user.username
            except RoomEntry.DoesNotExist:
                pass
        return 'N/A'
    
    def get_room_name(self, obj):
        """Obtener nombre de la sala desde el objeto relacionado"""
        if obj.related_object_id and obj.notification_type == 'excessive_hours':
            try:
                from rooms.models import RoomEntry
                entry = RoomEntry.objects.get(id=obj.related_object_id)
                return entry.room.name
            except RoomEntry.DoesNotExist:
                pass
        return 'N/A'
    
    def get_duration_hours(self, obj):
        """Obtener duración total desde el objeto relacionado"""
        if obj.related_object_id and obj.notification_type == 'excessive_hours':
            try:
                from rooms.models import RoomEntry
                from rooms.services import RoomEntryBusinessLogic
                entry = RoomEntry.objects.get(id=obj.related_object_id)
                duration_info = RoomEntryBusinessLogic.calculate_session_duration(entry)
                return duration_info.get('total_duration_hours', 0)
            except RoomEntry.DoesNotExist:
                pass
        return 0
    
    def get_excess_hours(self, obj):
        """Obtener horas de exceso desde el objeto relacionado"""
        duration_hours = self.get_duration_hours(obj)
        if duration_hours > 8:
            return round(duration_hours - 8, 2)
        return 0

from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Notification

class NotificationSerializer(serializers.ModelSerializer):
    recipient_name = serializers.CharField(source='user.get_full_name', read_only=True)
    recipient_username = serializers.CharField(source='user.username', read_only=True)
    is_read = serializers.BooleanField(source='read', read_only=True)
    monitor_id = serializers.IntegerField(source='user.id', read_only=True)
    monitor_name = serializers.CharField(source='user.get_full_name', read_only=True)
    # Permitir creación desde API para admins: user oculto y tipo requerido
    user = serializers.PrimaryKeyRelatedField(queryset=get_user_model().objects.all(), required=False, write_only=True)
    notification_type = serializers.ChoiceField(choices=Notification.TYPE_CHOICES, write_only=True, required=True)
    
    class Meta:
        model = Notification
        fields = [
            'id', 'notification_type', 'title', 'message', 'read', 'is_read', 'created_at',
            'recipient_name', 'recipient_username', 'monitor_id', 'monitor_name', 'user', 'related_object_id'
        ]
        read_only_fields = ['created_at', 'updated_at']

    def create(self, validated_data):
        # Si no se pasa user explícito, usar el request.user
        request = self.context.get('request') if self.context else None
        user = validated_data.pop('user', None)
        if user is None and request is not None:
            user = request.user
        # Crear notificación con usuario y tipo
        return Notification.objects.create(user=user, **validated_data)

class ExcessiveHoursNotificationSerializer(serializers.ModelSerializer):
    """
    Serializer específico para notificaciones de exceso de horas con información detallada
    """
    recipient_name = serializers.CharField(source='user.get_full_name', read_only=True)
    recipient_username = serializers.CharField(source='user.username', read_only=True)
    monitor_name = serializers.SerializerMethodField()
    monitor_username = serializers.SerializerMethodField()
    room_name = serializers.SerializerMethodField()
    duration_hours = serializers.SerializerMethodField()
    excess_hours = serializers.SerializerMethodField()
    
    class Meta:
        model = Notification
        fields = [
            'id', 'title', 'message', 'notification_type',
            'read', 'created_at', 'recipient_name', 'recipient_username',
            'monitor_name', 'monitor_username', 'room_name', 
            'duration_hours', 'excess_hours', 'related_object_id'
        ]
        read_only_fields = ['created_at']
    
    def get_monitor_name(self, obj):
        """Obtener nombre del monitor desde el objeto relacionado"""
        if obj.related_object_id and obj.notification_type == 'excessive_hours':
            try:
                from rooms.models import RoomEntry
                entry = RoomEntry.objects.get(id=obj.related_object_id)
                return entry.user.get_full_name()
            except RoomEntry.DoesNotExist:
                pass
        return 'N/A'
    
    def get_monitor_username(self, obj):
        """Obtener username del monitor desde el objeto relacionado"""
        if obj.related_object_id and obj.notification_type == 'excessive_hours':
            try:
                from rooms.models import RoomEntry
                entry = RoomEntry.objects.get(id=obj.related_object_id)
                return entry.user.username
            except RoomEntry.DoesNotExist:
                pass
        return 'N/A'
    
    def get_room_name(self, obj):
        """Obtener nombre de la sala desde el objeto relacionado"""
        if obj.related_object_id and obj.notification_type == 'excessive_hours':
            try:
                from rooms.models import RoomEntry
                entry = RoomEntry.objects.get(id=obj.related_object_id)
                return entry.room.name
            except RoomEntry.DoesNotExist:
                pass
        return 'N/A'
    
    def get_duration_hours(self, obj):
        """Obtener duración total desde el objeto relacionado"""
        if obj.related_object_id and obj.notification_type == 'excessive_hours':
            try:
                from rooms.models import RoomEntry
                from rooms.services import RoomEntryBusinessLogic
                entry = RoomEntry.objects.get(id=obj.related_object_id)
                duration_info = RoomEntryBusinessLogic.calculate_session_duration(entry)
                return duration_info.get('total_duration_hours', 0)
            except RoomEntry.DoesNotExist:
                pass
        return 0
    
    def get_excess_hours(self, obj):
        """Obtener horas de exceso desde el objeto relacionado"""
        duration_hours = self.get_duration_hours(obj)
        if duration_hours > 8:
            return round(duration_hours - 8, 2)
        return 0