from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
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
    
    # Acciones dedicadas para resolver y reabrir reportes
    @action(detail=True, methods=['post'], url_path='resolve')
    def resolve(self, request, pk=None):
        report = self.get_object()
        if not report.resolved:
            report.resolved = True
            report.resolved_date = timezone.now()
            report.save(update_fields=['resolved', 'resolved_date'])
        serializer = self.get_serializer(report)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'], url_path='reopen')
    def reopen(self, request, pk=None):
        report = self.get_object()
        if report.resolved:
            report.resolved = False
            report.resolved_date = None
            report.save(update_fields=['resolved', 'resolved_date'])
        serializer = self.get_serializer(report)
        return Response(serializer.data, status=status.HTTP_200_OK)