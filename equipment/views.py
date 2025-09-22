from rest_framework import viewsets, permissions
from .models import Equipment, EquipmentReport
from .serializers import EquipmentSerializer, EquipmentReportSerializer
from users.views import IsAdminUser


class EquipmentViewSet(viewsets.ModelViewSet):
    """
    API endpoint para gestionar equipos
    """
    queryset = Equipment.objects.all()
    serializer_class = EquipmentSerializer
    
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


class EquipmentReportViewSet(viewsets.ModelViewSet):
    """
    API endpoint para gestionar reportes de problemas con equipos
    """
    queryset = EquipmentReport.objects.all().order_by('-reported_date')
    serializer_class = EquipmentReportSerializer
    
    def get_permissions(self):
        """
        Define permisos según la acción
        """
        # Implementar lógica de permisos según necesidades
        return [permissions.IsAuthenticated()]
    
    # Agregar métodos para resolver reportes, asignar usuario que reporta, etc.