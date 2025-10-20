from rest_framework import status, generics, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from django.http import HttpResponse, Http404
from django.shortcuts import get_object_or_404
from django.db.models import Q
from django.utils import timezone
from datetime import datetime, date
import threading
from .models import ExportJob
from .serializers import (
    ExportJobSerializer, MonitorExportSerializer, 
    RoomEntryExportSerializer, ScheduleExportSerializer,
    AttendanceExportSerializer, IncapacityExportSerializer
)
from .services import MonitorDataExporter
from users.models import User
from rooms.models import RoomEntry
from attendance.models import Attendance, Incapacity
from schedule.models import Schedule


class ExportJobListCreateView(generics.ListCreateAPIView):
    """
    Vista para listar y crear trabajos de exportación
    """
    serializer_class = ExportJobSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Filtrar trabajos por usuario"""
        return ExportJob.objects.filter(requested_by=self.request.user).order_by('-created_at')
    
    def perform_create(self, serializer):
        """Asignar el usuario actual como solicitante"""
        serializer.save(requested_by=self.request.user)


class ExportJobDetailView(generics.RetrieveAPIView):
    """
    Vista para obtener detalles de un trabajo de exportación
    """
    serializer_class = ExportJobSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Filtrar trabajos por usuario"""
        return ExportJob.objects.filter(requested_by=self.request.user)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def export_monitors_data(request):
    """
    Endpoint para exportar datos de monitores
    """
    try:
        # Validar datos de entrada
        export_type = request.data.get('export_type', 'monitors_data')
        format_type = request.data.get('format', 'pdf')
        title = request.data.get('title', f'Exportación de Monitores - {datetime.now().strftime("%d/%m/%Y %H:%M")}')
        monitor_ids = request.data.get('monitor_ids', None)
        start_date = request.data.get('start_date', None)
        end_date = request.data.get('end_date', None)
        
        # Validar formato
        if format_type not in ['pdf', 'excel']:
            return Response({
                'error': 'Formato no válido. Use "pdf" o "excel"'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Validar fechas
        if start_date:
            try:
                start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
            except ValueError:
                return Response({
                    'error': 'Formato de fecha inicial inválido. Use YYYY-MM-DD'
                }, status=status.HTTP_400_BAD_REQUEST)
        
        if end_date:
            try:
                end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
            except ValueError:
                return Response({
                    'error': 'Formato de fecha final inválido. Use YYYY-MM-DD'
                }, status=status.HTTP_400_BAD_REQUEST)
        
        # Validar que las fechas sean lógicas
        if start_date and end_date and start_date > end_date:
            return Response({
                'error': 'La fecha inicial no puede ser posterior a la fecha final'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Crear trabajo de exportación
        export_job = ExportJob.objects.create(
            title=title,
            export_type=export_type,
            format=format_type,
            start_date=start_date,
            end_date=end_date,
            monitor_ids=monitor_ids,
            requested_by=request.user
        )
        
        # Iniciar exportación en hilo separado
        def run_export():
            exporter = MonitorDataExporter(export_job)
            if format_type == 'pdf':
                exporter.export_to_pdf()
            else:
                exporter.export_to_excel()
        
        thread = threading.Thread(target=run_export)
        thread.daemon = True
        thread.start()
        
        return Response({
            'message': 'Exportación iniciada',
            'export_job_id': export_job.id,
            'status': 'processing'
        }, status=status.HTTP_202_ACCEPTED)
        
    except Exception as e:
        return Response({
            'error': f'Error al iniciar exportación: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def get_monitors_data(request):
    """
    Endpoint para obtener datos de monitores (sin exportar)
    """
    try:
        # Parámetros de filtrado
        monitor_ids = request.GET.getlist('monitor_ids')
        start_date = request.GET.get('start_date')
        end_date = request.GET.get('end_date')
        format_type = request.GET.get('format', 'json')
        
        # Construir queryset
        queryset = User.objects.filter(role=User.MONITOR, is_verified=True)
        
        if monitor_ids:
            queryset = queryset.filter(id__in=monitor_ids)
        
        # Aplicar filtros de fecha si se proporcionan
        if start_date:
            try:
                start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
            except ValueError:
                return Response({
                    'error': 'Formato de fecha inicial inválido. Use YYYY-MM-DD'
                }, status=status.HTTP_400_BAD_REQUEST)
        
        if end_date:
            try:
                end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
            except ValueError:
                return Response({
                    'error': 'Formato de fecha final inválido. Use YYYY-MM-DD'
                }, status=status.HTTP_400_BAD_REQUEST)
        
        # Serializar datos
        serializer = MonitorExportSerializer(queryset, many=True, context={'request': request})
        
        return Response({
            'monitors': serializer.data,
            'total_count': queryset.count(),
            'filters_applied': {
                'monitor_ids': monitor_ids,
                'start_date': start_date.isoformat() if start_date else None,
                'end_date': end_date.isoformat() if end_date else None
            }
        })
        
    except Exception as e:
        return Response({
            'error': f'Error al obtener datos: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def get_room_entries_data(request):
    """
    Endpoint para obtener datos de entradas a salas
    """
    try:
        # Parámetros de filtrado
        monitor_ids = request.GET.getlist('monitor_ids')
        start_date = request.GET.get('start_date')
        end_date = request.GET.get('end_date')
        room_ids = request.GET.getlist('room_ids')
        
        # Construir queryset
        queryset = RoomEntry.objects.select_related('user', 'room').all()
        
        if monitor_ids:
            queryset = queryset.filter(user_id__in=monitor_ids)
        
        if room_ids:
            queryset = queryset.filter(room_id__in=room_ids)
        
        # Aplicar filtros de fecha
        if start_date:
            try:
                start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
                queryset = queryset.filter(entry_time__date__gte=start_date)
            except ValueError:
                return Response({
                    'error': 'Formato de fecha inicial inválido. Use YYYY-MM-DD'
                }, status=status.HTTP_400_BAD_REQUEST)
        
        if end_date:
            try:
                end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
                queryset = queryset.filter(entry_time__date__lte=end_date)
            except ValueError:
                return Response({
                    'error': 'Formato de fecha final inválido. Use YYYY-MM-DD'
                }, status=status.HTTP_400_BAD_REQUEST)
        
        # Serializar datos
        serializer = RoomEntryExportSerializer(queryset.order_by('-entry_time'), many=True, context={'request': request})
        
        return Response({
            'room_entries': serializer.data,
            'total_count': queryset.count(),
            'filters_applied': {
                'monitor_ids': monitor_ids,
                'room_ids': room_ids,
                'start_date': start_date.isoformat() if start_date else None,
                'end_date': end_date.isoformat() if end_date else None
            }
        })
        
    except Exception as e:
        return Response({
            'error': f'Error al obtener datos: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def get_schedules_data(request):
    """
    Endpoint para obtener datos de turnos
    """
    try:
        # Parámetros de filtrado
        monitor_ids = request.GET.getlist('monitor_ids')
        start_date = request.GET.get('start_date')
        end_date = request.GET.get('end_date')
        room_ids = request.GET.getlist('room_ids')
        status_filter = request.GET.get('status')
        
        # Construir queryset
        queryset = Schedule.objects.select_related('user', 'room', 'created_by').all()
        
        if monitor_ids:
            queryset = queryset.filter(user_id__in=monitor_ids)
        
        if room_ids:
            queryset = queryset.filter(room_id__in=room_ids)
        
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        # Aplicar filtros de fecha
        if start_date:
            try:
                start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
                queryset = queryset.filter(start_datetime__date__gte=start_date)
            except ValueError:
                return Response({
                    'error': 'Formato de fecha inicial inválido. Use YYYY-MM-DD'
                }, status=status.HTTP_400_BAD_REQUEST)
        
        if end_date:
            try:
                end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
                queryset = queryset.filter(start_datetime__date__lte=end_date)
            except ValueError:
                return Response({
                    'error': 'Formato de fecha final inválido. Use YYYY-MM-DD'
                }, status=status.HTTP_400_BAD_REQUEST)
        
        # Serializar datos
        serializer = ScheduleExportSerializer(queryset.order_by('-start_datetime'), many=True, context={'request': request})
        
        return Response({
            'schedules': serializer.data,
            'total_count': queryset.count(),
            'filters_applied': {
                'monitor_ids': monitor_ids,
                'room_ids': room_ids,
                'status': status_filter,
                'start_date': start_date.isoformat() if start_date else None,
                'end_date': end_date.isoformat() if end_date else None
            }
        })
        
    except Exception as e:
        return Response({
            'error': f'Error al obtener datos: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def download_export_file(request, export_job_id):
    """
    Endpoint para descargar archivos de exportación
    """
    try:
        export_job = get_object_or_404(ExportJob, id=export_job_id, requested_by=request.user)
        
        if not export_job.is_completed or not export_job.file:
            return Response({
                'error': 'El archivo no está disponible o la exportación no ha terminado'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Determinar content type según el formato
        if export_job.format == ExportJob.PDF:
            content_type = 'application/pdf'
        elif export_job.format == ExportJob.EXCEL:
            content_type = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        else:
            content_type = 'application/octet-stream'
        
        # Crear respuesta HTTP con el archivo
        response = HttpResponse(
            export_job.file.read(),
            content_type=content_type
        )
        
        # Configurar headers para descarga
        filename = f"export_{export_job.export_type}_{export_job.format}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{export_job.format}"
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        if export_job.file_size:
            response['Content-Length'] = export_job.file_size
        
        return response
        
    except Exception as e:
        return Response({
            'error': f'Error al descargar archivo: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def get_export_status(request, export_job_id):
    """
    Endpoint para verificar el estado de una exportación
    """
    try:
        export_job = get_object_or_404(ExportJob, id=export_job_id, requested_by=request.user)
        
        serializer = ExportJobSerializer(export_job, context={'request': request})
        
        return Response(serializer.data)
        
    except Exception as e:
        return Response({
            'error': f'Error al obtener estado: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

