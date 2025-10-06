from rest_framework import viewsets, permissions
from .models import Attendance, Incapacity
from .serializers import AttendanceSerializer, IncapacitySerializer
from users.views import IsAdminUser


class AttendanceViewSet(viewsets.ModelViewSet):
    """
    API endpoint para gestionar listados de asistencia
    """
    queryset = Attendance.objects.all().order_by('-date')
    serializer_class = AttendanceSerializer
    
    def get_permissions(self):
        """
        Define permisos según la acción
        """
        # Implementar lógica de permisos según necesidades
        return [permissions.IsAuthenticated()]
    
    # Agregar métodos para marcar como revisado, asignar usuario que sube, etc.


class IncapacityViewSet(viewsets.ModelViewSet):
    """
    API endpoint para gestionar incapacidades
    """
    queryset = Incapacity.objects.all().order_by('-start_date')
    serializer_class = IncapacitySerializer
    
    def get_permissions(self):
        """
        Define permisos según la acción
        """
        # Implementar lógica de permisos según necesidades
        return [permissions.IsAuthenticated()]
    
    # Agregar métodos para aprobar incapacidades, asignar usuario, etc.