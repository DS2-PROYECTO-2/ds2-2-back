from rest_framework import viewsets, permissions
from .models import Schedule
from .serializers import ScheduleSerializer


class ScheduleViewSet(viewsets.ModelViewSet):
    """
    API endpoint para gestionar turnos
    """
    serializer_class = ScheduleSerializer
    
    def get_queryset(self):
        """
        Retorna turnos según el rol del usuario
        """
        user = self.request.user
        if user.is_admin:
            # Administradores pueden ver todos los turnos
            return Schedule.objects.all()
        else:
            # Monitores solo ven sus propios turnos
            return Schedule.objects.filter(user=user)
    
    def get_permissions(self):
        """
        Define permisos según la acción
        """
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [permissions.IsAuthenticated]  # Implementar IsAdminUser
        else:
            permission_classes = [permissions.IsAuthenticated]
        
        return [permission() for permission in permission_classes]