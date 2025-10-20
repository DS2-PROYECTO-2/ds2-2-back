from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from django.http import HttpResponse, Http404
from django.shortcuts import get_object_or_404
from .models import Attendance, Incapacity
from .serializers import AttendanceSerializer, IncapacitySerializer

User = get_user_model()


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
        if self.action in ['mark_as_reviewed']:
            # Solo admins pueden marcar como revisado
            return [permissions.IsAuthenticated() and permissions.IsAdminUser()]
        return [permissions.IsAuthenticated()]
    
    def perform_create(self, serializer):
        """Asignar automáticamente el usuario actual como uploaded_by"""
        serializer.save(uploaded_by=self.request.user)
    
    @action(detail=True, methods=['post'])
    def mark_as_reviewed(self, request, pk=None):
        """Marcar un listado como revisado por un administrador"""
        attendance = self.get_object()
        attendance.reviewed = True
        attendance.reviewed_by = request.user
        attendance.save()
        
        serializer = self.get_serializer(attendance)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def my_uploads(self, request):
        """Obtener listados subidos por el usuario actual"""
        attendances = Attendance.objects.filter(uploaded_by=request.user)
        serializer = self.get_serializer(attendances, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def download(self, request, pk=None):
        """Descargar archivo de un listado de asistencia"""
        attendance = self.get_object()
        
        # Verificar que el archivo existe
        if not attendance.file:
            raise Http404("El archivo no está disponible")
        
        try:
            # Leer el archivo
            with attendance.file.open('rb') as f:
                file_content = f.read()
            
            # Determinar content type según la extensión
            file_extension = attendance.file.name.split('.')[-1].lower()
            if file_extension == 'pdf':
                content_type = 'application/pdf'
            elif file_extension in ['xlsx', 'xls']:
                content_type = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            elif file_extension == 'txt':
                content_type = 'text/plain'
            else:
                content_type = 'application/octet-stream'
            
            # Crear respuesta HTTP
            response = HttpResponse(file_content, content_type=content_type)
            response['Content-Disposition'] = f'attachment; filename="{attendance.title}.{file_extension}"'
            response['Content-Length'] = len(file_content)
            
            return response
            
        except Exception as e:
            return Response(
                {'error': f'Error al descargar archivo: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


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
        if self.action in ['approve', 'reject']:
            # Solo admins pueden aprobar/rechazar
            return [permissions.IsAuthenticated() and permissions.IsAdminUser()]
        return [permissions.IsAuthenticated()]
    
    def perform_create(self, serializer):
        """Asignar automáticamente el usuario actual como user"""
        serializer.save(user=self.request.user)
    
    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        """Aprobar una incapacidad"""
        incapacity = self.get_object()
        incapacity.approved = True
        incapacity.approved_by = request.user
        incapacity.save()
        
        serializer = self.get_serializer(incapacity)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        """Rechazar una incapacidad"""
        incapacity = self.get_object()
        incapacity.approved = False
        incapacity.approved_by = request.user
        incapacity.save()
        
        serializer = self.get_serializer(incapacity)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def my_incapacities(self, request):
        """Obtener incapacidades del usuario actual"""
        incapacities = Incapacity.objects.filter(user=request.user)
        serializer = self.get_serializer(incapacities, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def download(self, request, pk=None):
        """Descargar documento de una incapacidad"""
        incapacity = self.get_object()
        
        # Verificar que el documento existe
        if not incapacity.document:
            raise Http404("El documento no está disponible")
        
        try:
            # Leer el archivo
            with incapacity.document.open('rb') as f:
                file_content = f.read()
            
            # Determinar content type según la extensión
            file_extension = incapacity.document.name.split('.')[-1].lower()
            if file_extension == 'pdf':
                content_type = 'application/pdf'
            elif file_extension in ['xlsx', 'xls']:
                content_type = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            elif file_extension == 'txt':
                content_type = 'text/plain'
            else:
                content_type = 'application/octet-stream'
            
            # Crear respuesta HTTP
            response = HttpResponse(file_content, content_type=content_type)
            response['Content-Disposition'] = f'attachment; filename="incapacidad_{incapacity.user.username}_{incapacity.start_date}.{file_extension}"'
            response['Content-Length'] = len(file_content)
            
            return response
            
        except Exception as e:
            return Response(
                {'error': f'Error al descargar documento: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

