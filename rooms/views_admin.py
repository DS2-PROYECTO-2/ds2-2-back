from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.authentication import TokenAuthentication
from rest_framework.response import Response
from django.db.models import Q
from django.core.paginator import Paginator
from users.permissions import IsAdminUser
from .models import RoomEntry
import logging

logger = logging.getLogger(__name__)


@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAdminUser])
def admin_entries_list(request):
    """
    Lista todas las entradas con filtros para administradores
    """
    try:
        # Obtener parámetros de filtro
        user_name = request.GET.get('user_name', '').strip()
        room_id = request.GET.get('room', '').strip()
        active = request.GET.get('active', '').strip()
        from_date = request.GET.get('from', '').strip()
        to_date = request.GET.get('to', '').strip()
        document = request.GET.get('document', '').strip()
        page = int(request.GET.get('page', 1))
        page_size = int(request.GET.get('page_size', 20))
        
        # Construir queryset base
        queryset = RoomEntry.objects.select_related('user', 'room').order_by('-entry_time')
        
        # Aplicar filtros
        if user_name:
            queryset = queryset.filter(
                Q(user__first_name__icontains=user_name) |
                Q(user__last_name__icontains=user_name) |
                Q(user__username__icontains=user_name)
            )
        
        if room_id:
            try:
                room_id_int = int(room_id)
                queryset = queryset.filter(room_id=room_id_int)
            except ValueError:
                pass
        
        if active.lower() == 'true':
            queryset = queryset.filter(exit_time__isnull=True)
        elif active.lower() == 'false':
            queryset = queryset.filter(exit_time__isnull=False)
        
        if from_date:
            try:
                from datetime import datetime
                from_date_obj = datetime.fromisoformat(from_date.replace('Z', '+00:00'))
                queryset = queryset.filter(entry_time__gte=from_date_obj)
            except ValueError:
                pass
        
        if to_date:
            try:
                from datetime import datetime
                to_date_obj = datetime.fromisoformat(to_date.replace('Z', '+00:00'))
                queryset = queryset.filter(entry_time__lte=to_date_obj)
            except ValueError:
                pass
        
        if document:
            queryset = queryset.filter(user__identification__icontains=document)
        
        # Paginación
        paginator = Paginator(queryset, page_size)
        page_obj = paginator.get_page(page)
        
        # Serializar datos
        entries_data = []
        for entry in page_obj:
            entry_data = {
                'id': entry.id,
                'room': entry.room.id,
                'room_name': entry.room.name,
                'entry_time': entry.entry_time.isoformat(),
                'exit_time': entry.exit_time.isoformat() if entry.exit_time else None,
                'user': entry.user.id,
                'user_name': entry.user.get_full_name(),
                'user_username': entry.user.username,
                'user_identification': entry.user.identification,
                'notes': entry.notes,
                'is_active': entry.exit_time is None
            }
            entries_data.append(entry_data)
        
        return Response({
            'count': paginator.count,
            'entries': entries_data,
            'page': page,
            'page_size': page_size,
            'total_pages': paginator.num_pages,
            'has_next': page_obj.has_next(),
            'has_previous': page_obj.has_previous()
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Error en admin_entries_list: {e}")
        return Response({
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAdminUser])
def admin_entries_stats(request):
    """
    Estadísticas de entradas para administradores
    """
    try:
        from django.db.models import Count
        from django.utils import timezone
        from datetime import timedelta
        
        # Estadísticas generales
        total_entries = RoomEntry.objects.count()
        active_entries = RoomEntry.objects.filter(exit_time__isnull=True).count()
        completed_entries = RoomEntry.objects.filter(exit_time__isnull=False).count()
        
        # Entradas de hoy
        today = timezone.now().date()
        today_entries = RoomEntry.objects.filter(entry_time__date=today).count()
        
        # Entradas de esta semana
        week_ago = timezone.now() - timedelta(days=7)
        week_entries = RoomEntry.objects.filter(entry_time__gte=week_ago).count()
        
        # Usuarios más activos
        most_active_users = RoomEntry.objects.values(
            'user__username', 'user__first_name', 'user__last_name'
        ).annotate(
            entry_count=Count('id')
        ).order_by('-entry_count')[:5]
        
        # Salas más utilizadas
        most_used_rooms = RoomEntry.objects.values(
            'room__name', 'room__code'
        ).annotate(
            entry_count=Count('id')
        ).order_by('-entry_count')[:5]
        
        return Response({
            'total_entries': total_entries,
            'active_entries': active_entries,
            'completed_entries': completed_entries,
            'today_entries': today_entries,
            'week_entries': week_entries,
            'most_active_users': list(most_active_users),
            'most_used_rooms': list(most_used_rooms)
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Error en admin_entries_stats: {e}")
        return Response({
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
