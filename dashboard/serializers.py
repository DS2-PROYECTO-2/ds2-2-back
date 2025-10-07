from rest_framework import serializers


class DashboardStatsSerializer(serializers.Serializer):
    """
    Serializer para las estadísticas del dashboard
    """
    # Estadísticas generales
    total_users = serializers.IntegerField()
    total_rooms = serializers.IntegerField()
    active_entries = serializers.IntegerField()
    unread_notifications = serializers.IntegerField()
    
    # Estadísticas de monitores
    total_monitors = serializers.IntegerField()
    verified_monitors = serializers.IntegerField()
    pending_verifications = serializers.IntegerField()
    
    # Estadísticas de salas
    occupied_rooms = serializers.IntegerField()
    available_rooms = serializers.IntegerField()
    
    # Estadísticas de tiempo
    total_hours_today = serializers.FloatField()
    average_session_duration = serializers.FloatField()
    
    # Alertas
    excessive_hours_alerts = serializers.IntegerField()
    critical_alerts = serializers.IntegerField()


class MiniCardSerializer(serializers.Serializer):
    """
    Serializer para las mini cards del dashboard
    """
    title = serializers.CharField()
    value = serializers.CharField()
    icon = serializers.CharField()
    color = serializers.CharField()
    trend = serializers.CharField(required=False)
    trend_value = serializers.CharField(required=False)


class DashboardDataSerializer(serializers.Serializer):
    """
    Serializer completo del dashboard
    """
    user_info = serializers.DictField()
    stats = DashboardStatsSerializer()
    mini_cards = MiniCardSerializer(many=True)
    recent_activities = serializers.ListField()
    alerts = serializers.ListField()
    charts_data = serializers.DictField()


