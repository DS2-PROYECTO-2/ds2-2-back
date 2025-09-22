from rest_framework import viewsets, permissions
from .models import Room, RoomEntry
from .serializers import RoomSerializer, RoomEntrySerializer
from users.views import IsAdminUser


class RoomViewSet(viewsets.ModelViewSet):
    """
    API endpoint para gestionar salas
    """
    queryset = Room.objects.all()
    serializer_class = RoomSerializer
    
    def get_permissions(self):
        """
        Define permisos según la acción
        """
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [IsAdminUser]
        else:
            permission_classes = [permissions.IsAuthenticated]
        
        return [permission() for permission in permission_classes]
    
    # Agregar métodos personalizados según necesidades


class RoomEntryViewSet(viewsets.ModelViewSet):
    """
    API endpoint para gestionar entradas y salidas de salas
    """
    queryset = RoomEntry.objects.all().order_by('-entry_time')
    serializer_class = RoomEntrySerializer
    
    def get_permissions(self):
        """
        Define permisos según la acción
        """
        # Implementar lógica de permisos según necesidades
        return [permissions.IsAuthenticated()]
    
    # Agregar métodos para registrar salidas, verificar entradas activas, etc.