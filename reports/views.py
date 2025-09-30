from rest_framework import viewsets, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from .models import Report
from .serializers import ReportSerializer


class ReportViewSet(viewsets.ModelViewSet):
    """
    API endpoint para gestionar reportes
    """
    serializer_class = ReportSerializer
    permission_classes = [permissions.IsAuthenticated]  # Implementar IsAdminUser
    
    def get_queryset(self):
        """
        Retorna reportes creados por el usuario autenticado
        """
        return Report.objects.filter(created_by=self.request.user).order_by('-created_at')


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])  # Implementar IsAdminUser
def generate_report(request):
    """
    Endpoint para generar un nuevo reporte
    """
    # La lógica de generación de reportes se implementará después
    return Response({'message': 'Funcionalidad de generación de reportes a implementar'})