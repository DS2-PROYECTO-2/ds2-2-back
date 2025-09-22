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
        Retorna solo las notificaciones del usuario autenticado
        """
        return Notification.objects.filter(user=self.request.user).order_by('-created_at')