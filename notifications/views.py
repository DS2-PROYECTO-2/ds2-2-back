from rest_framework import viewsets, permissions
from .models import Notification
from .serializers import NotificationSerializer


class NotificationViewSet(viewsets.ModelViewSet):
    """
    API endpoint para gestionar notificaciones
    """
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """
        Retorna todas las notificaciones para desarrollo
        """
        # Para desarrollo: mostrar todas las notificaciones
        return Notification.objects.all().order_by('-created_at')