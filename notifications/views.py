from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Notification
from .serializers import NotificationSerializer, ExcessiveHoursNotificationSerializer
from .services import NotificationService, ExcessiveHoursChecker


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
        unread_notifications = self.get_queryset().filter(read=False)
        serializer = self.get_serializer(unread_notifications, many=True)
        return Response({
            'count': unread_notifications.count(),
            'notifications': serializer.data
        })
    
    def list(self, request):
        """
        Lista todas las notificaciones del usuario con filtros opcionales
        """
        queryset = self.get_queryset()
        
        # Filtros opcionales
        notification_type = request.query_params.get('type', None)
        read_status = request.query_params.get('read', None)
        
        if notification_type:
            queryset = queryset.filter(notification_type=notification_type)
        
        if read_status is not None:
            read_bool = read_status.lower() == 'true'
            queryset = queryset.filter(read=read_bool)
        
        # Paginación
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['patch'])
    def mark_read(self, request, pk=None):
        """
        Marcar una notificación específica como leída
        """
        try:
            notification = self.get_object()
            if NotificationService.mark_notification_as_read(notification.id, request.user):
                return Response({'message': 'Notificación marcada como leída'})
            else:
                return Response({'error': 'No se pudo marcar la notificación'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['patch'])
    def mark_all_read(self, request):
        """
        Marcar todas las notificaciones del usuario como leídas
        """
        try:
            updated_count = NotificationService.mark_all_as_read(request.user)
            return Response({
                'message': f'{updated_count} notificaciones marcadas como leídas',
                'updated_count': updated_count
            })
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'])
    def unread_count(self, request):
        """
        Obtener solo el contador de notificaciones no leídas
        """
        unread_count = self.get_queryset().filter(read=False).count()
        return Response({
            'unread_count': unread_count
        })
    
    @action(detail=False, methods=['get'])
    def summary(self, request):
        """
        Obtener resumen de notificaciones del usuario
        """
        try:
            summary = NotificationService.get_user_notifications_summary(request.user)
            serializer = self.get_serializer(summary['recent'], many=True)
            
            return Response({
                'total': summary['total'],
                'unread': summary['unread'],
                'recent': serializer.data,
                'by_type': list(summary['by_type'])
            })
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'])
    def excessive_hours_summary(self, request):
        """
        Obtener resumen estadístico de monitores que han excedido las 8 horas
        Solo para administradores
        """
        if request.user.role != 'admin':
            return Response({'error': 'Solo administradores pueden acceder a este endpoint'}, status=403)
        
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
    
    @action(detail=False, methods=['post'])
    def hours_exceeded(self, request):
        """
        Endpoint para verificar y notificar exceso de horas manualmente
        Solo para administradores
        """
        if request.user.role != 'admin':
            return Response({'error': 'Solo administradores pueden acceder a este endpoint'}, status=403)
        
        try:
            # Verificar todas las entradas activas
            notifications_sent = NotificationService.check_and_notify_excessive_hours()
            
            # Obtener monitores con exceso de horas actual
            excessive_monitors = ExcessiveHoursChecker.get_monitors_with_excessive_hours()
            
            return Response({
                'message': f'Verificación completada. {notifications_sent} notificaciones enviadas.',
                'notifications_sent': notifications_sent,
                'current_excessive_monitors': len(excessive_monitors),
                'monitors': [
                    {
                        'username': monitor['user'].username,
                        'full_name': monitor['user'].get_full_name(),
                        'room': monitor['room'].name,
                        'total_hours': monitor['total_hours'],
                        'excess_hours': monitor['excess_hours'],
                        'is_critical': monitor['is_critical']
                    }
                    for monitor in excessive_monitors
                ]
            })
            
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)