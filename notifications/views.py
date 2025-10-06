from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Notification
from .serializers import NotificationSerializer, ExcessiveHoursNotificationSerializer


class NotificationViewSet(viewsets.ModelViewSet):
    """
    API endpoint para gestionar notificaciones
    """
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """
        Retorna las notificaciones según el rol del usuario
        """
        if self.request.user.role == 'admin':
            # Los admins ven todas las notificaciones dirigidas a administradores
            return Notification.objects.filter(user=self.request.user).order_by('-created_at')
        else:
            # Los monitores solo ven sus propias notificaciones
            return Notification.objects.filter(user=self.request.user).order_by('-created_at')
    
    @action(detail=False, methods=['get'])
    def excessive_hours(self, request):
        """
        Endpoint específico para obtener TODAS las notificaciones de exceso de horas
        Los admins ven las notificaciones de TODOS los monitores que excedan 8 horas
        """
        if request.user.role != 'admin':
            return Response({'error': 'Solo administradores pueden acceder a este endpoint'}, status=403)
        
        # Obtener TODAS las notificaciones de exceso de horas dirigidas a administradores
        notifications = Notification.objects.filter(
            notification_type='excessive_hours'
        ).select_related('user').order_by('-created_at')
        
        # Usar el serializer específico para notificaciones de exceso de horas
        serializer = ExcessiveHoursNotificationSerializer(notifications, many=True)
        return Response({
            'count': notifications.count(),
            'notifications': serializer.data,
            'message': 'Notificaciones de exceso de horas de todos los monitores'
        })
    
    @action(detail=False, methods=['get'])
    def unread(self, request):
        """
        Obtener solo notificaciones no leídas del usuario
        """
        unread_notifications = self.get_queryset().filter(is_read=False)
        serializer = self.get_serializer(unread_notifications, many=True)
        return Response({
            'count': unread_notifications.count(),
            'notifications': serializer.data
        })
    
    @action(detail=False, methods=['get'])
    def excessive_hours_summary(self, request):
        """
        Obtener resumen estadístico de monitores que han excedido las 8 horas
        Solo para administradores
        """
        if request.user.role != 'admin':
            return Response({'error': 'Solo administradores pueden acceder a este endpoint'}, status=403)
        
        from django.db.models import Count
        from datetime import datetime, timedelta
        
        # Obtener notificaciones de las últimas 30 días
        last_30_days = datetime.now() - timedelta(days=30)
        
        excessive_notifications = Notification.objects.filter(
            notification_type='excessive_hours',
            created_at__gte=last_30_days
        ).order_by('-created_at')
        
        # Crear resumen por monitor
        monitors_summary = {}
        for notification in excessive_notifications:
            if notification.related_object_id:
                try:
                    from rooms.models import RoomEntry
                    from rooms.services import RoomEntryBusinessLogic
                    entry = RoomEntry.objects.get(id=notification.related_object_id)
                    username = entry.user.username
                    monitor_name = entry.user.get_full_name()
                    duration_info = RoomEntryBusinessLogic.calculate_session_duration(entry)
                    duration_hours = duration_info.get('total_duration_hours', 0)
                except RoomEntry.DoesNotExist:
                    continue
                
                if username not in monitors_summary:
                    monitors_summary[username] = {
                        'monitor_username': username,
                        'monitor_name': monitor_name,
                        'total_violations': 0,
                        'max_hours': 0,
                        'last_violation': None,
                        'total_excess_hours': 0
                    }
                
                monitors_summary[username]['total_violations'] += 1
                monitors_summary[username]['max_hours'] = max(
                    monitors_summary[username]['max_hours'], 
                    duration_hours
                )
                excess_hours = max(0, duration_hours - 8) if duration_hours > 8 else 0
                monitors_summary[username]['total_excess_hours'] += excess_hours
                
                if not monitors_summary[username]['last_violation'] or notification.created_at > monitors_summary[username]['last_violation']:
                    monitors_summary[username]['last_violation'] = notification.created_at
        
        return Response({
            'period': 'Últimos 30 días',
            'total_notifications': excessive_notifications.count(),
            'unique_monitors': len(monitors_summary),
            'monitors_summary': list(monitors_summary.values()),
            'recent_notifications': ExcessiveHoursNotificationSerializer(
                excessive_notifications[:5], many=True
            ).data
        })