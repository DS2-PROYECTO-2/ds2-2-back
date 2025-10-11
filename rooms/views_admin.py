from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.authentication import TokenAuthentication
from rest_framework.response import Response
from django.db.models import Q
from django.core.paginator import Paginator
from users.permissions import IsAdminUser
from .models import Room, RoomEntry
from django.shortcuts import get_object_or_404
import logging

logger = logging.getLogger(__name__)


@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAdminUser])
def admin_rooms_list(request):
    """
    Lista de salas para administradores con soporte de búsqueda y conteo de ocupantes.
    Parámetros opcionales:
      - search: filtra por nombre o código
      - include_inactive: 'true' para incluir inactivas
    """
    search = request.GET.get('search', '').strip()
    include_inactive = request.GET.get('include_inactive', 'false').lower() == 'true'

    queryset = Room.objects.all().order_by('code')
    if not include_inactive:
        queryset = queryset.filter(is_active=True)

    if search:
        queryset = queryset.filter(Q(name__icontains=search) | Q(code__icontains=search))

    rooms_data = []
    for room in queryset:
        occupants_count = RoomEntry.objects.filter(room=room, exit_time__isnull=True).count()
        rooms_data.append({
            'id': room.id,
            'name': room.name,
            'code': room.code,
            'capacity': room.capacity,
            'description': room.description,
            'is_active': room.is_active,
            'occupants_count': occupants_count,
        })

    return Response({
        'count': queryset.count(),
        'rooms': rooms_data,
    }, status=status.HTTP_200_OK)


@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAdminUser])
def admin_room_detail(request, room_id):
    """Detalle de sala con estadísticas para administradores."""
    room = get_object_or_404(Room, id=room_id)

    active_entries = RoomEntry.objects.filter(room=room, exit_time__isnull=True)
    total_entries = RoomEntry.objects.filter(room=room)
    completed_entries = total_entries.exclude(exit_time__isnull=True)

    # Calcular horas totales de uso
    total_hours = 0.0
    for e in completed_entries:
        duration = (e.exit_time - e.entry_time).total_seconds() / 3600.0
        total_hours += max(0.0, duration)

    data = {
        'room': {
            'id': room.id,
            'name': room.name,
            'code': room.code,
            'capacity': room.capacity,
            'description': room.description,
            'is_active': room.is_active,
        },
        'statistics': {
            'current_occupants': active_entries.count(),
            'total_entries_historical': total_entries.count(),
            'total_hours_usage': round(total_hours, 2),
            'active_entries': list(active_entries.values_list('id', flat=True)),
        }
    }
    return Response(data, status=status.HTTP_200_OK)


@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAdminUser])
def admin_room_create(request):
    """Crear una sala (solo admin). Valida código duplicado."""
    name = request.data.get('name')
    code = request.data.get('code')
    capacity = request.data.get('capacity')
    description = request.data.get('description', '')

    if Room.objects.filter(code=code).exists():
        return Response({'error': 'Validación fallida', 'details': {'code': ['Código ya existe']}}, status=status.HTTP_400_BAD_REQUEST)

    room = Room.objects.create(
        name=name,
        code=code,
        capacity=capacity,
        description=description,
    )
    return Response({'message': 'Sala creada', 'room': {
        'id': room.id,
        'name': room.name,
        'code': room.code,
        'capacity': room.capacity,
        'description': room.description,
        'is_active': room.is_active,
    }}, status=status.HTTP_201_CREATED)


@api_view(['PATCH'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAdminUser])
def admin_room_update(request, room_id):
    """Actualizar una sala; no permite desactivar si hay ocupantes activos."""
    room = get_object_or_404(Room, id=room_id)

    # Si intenta desactivar, validar ocupantes activos
    is_active = request.data.get('is_active')
    if is_active is not None and str(is_active).lower() in ['false', '0']:
        has_active = RoomEntry.objects.filter(room=room, exit_time__isnull=True).exists()
        if has_active:
            return Response({'error': 'No se puede desactivar: hay ocupantes activos'}, status=status.HTTP_400_BAD_REQUEST)

    # Actualizaciones básicas
    for field in ['name', 'capacity', 'description']:
        if field in request.data:
            setattr(room, field, request.data.get(field))
    if is_active is not None:
        room.is_active = str(is_active).lower() not in ['false', '0']
    room.save()

    return Response({'message': 'Sala actualizada', 'room': {
        'id': room.id,
        'name': room.name,
        'code': room.code,
        'capacity': room.capacity,
        'description': room.description,
        'is_active': room.is_active,
    }}, status=status.HTTP_200_OK)


@api_view(['DELETE'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAdminUser])
def admin_room_delete(request, room_id):
    """Eliminar sala: hard delete si no hay historial; si lo hay, soft delete; si hay ocupantes activos, 400."""
    room = get_object_or_404(Room, id=room_id)

    if RoomEntry.objects.filter(room=room, exit_time__isnull=True).exists():
        return Response({'error': 'No se puede eliminar: hay ocupantes activos'}, status=status.HTTP_400_BAD_REQUEST)

    if RoomEntry.objects.filter(room=room).exists():
        # Soft delete
        if room.is_active:
            room.is_active = False
        if not room.name.startswith('ELIMINADA'):
            room.name = f"ELIMINADA - {room.name}"
        room.save()
        return Response({'message': 'Sala marcada como eliminada', 'action': 'soft_delete'}, status=status.HTTP_200_OK)

    # Hard delete
    room.delete()
    return Response({'message': 'Sala eliminada definitivamente', 'action': 'hard_delete'}, status=status.HTTP_200_OK)


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
        # Manejo robusto de paginación cuando vienen vacíos o inválidos
        page_raw = request.GET.get('page', '').strip()
        page_size_raw = request.GET.get('page_size', '').strip()
        try:
            page = int(page_raw) if page_raw else 1
        except ValueError:
            page = 1
        try:
            page_size = int(page_size_raw) if page_size_raw else 20
        except ValueError:
            page_size = 20
        
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

        # FILTROS DE FECHA COMPLETOS (CORREGIDOS)
        if from_date and to_date:
            # Caso 1: Ambas fechas presentes - filtrar por rango completo
            try:
                from datetime import datetime, timezone
                from django.utils import timezone as django_timezone
                
                # Manejar diferentes formatos de fecha
                if 'T' in from_date:
                    from_date_obj = datetime.fromisoformat(from_date.replace('Z', '+00:00'))
                else:
                    from_date_obj = datetime.fromisoformat(f"{from_date}T00:00:00+00:00")
                
                if 'T' in to_date:
                    to_date_obj = datetime.fromisoformat(to_date.replace('Z', '+00:00'))
                else:
                    to_date_obj = datetime.fromisoformat(f"{to_date}T23:59:59+00:00")
                
                # Asegurar que las fechas estén en UTC usando Django timezone
                if from_date_obj.tzinfo is None:
                    from_date_obj = django_timezone.make_aware(from_date_obj, timezone.utc)
                if to_date_obj.tzinfo is None:
                    to_date_obj = django_timezone.make_aware(to_date_obj, timezone.utc)
                
                # Configurar el rango completo del día
                start_datetime = from_date_obj.replace(hour=0, minute=0, second=0, microsecond=0)
                end_datetime = to_date_obj.replace(hour=23, minute=59, second=59, microsecond=999999)
                
                queryset = queryset.filter(
                    entry_time__gte=start_datetime,
                    entry_time__lte=end_datetime
                )
            except ValueError as e:
                logger.warning(f"Error parsing date range: {e}")
                pass
        elif from_date:
            # Caso 2: Solo fecha inicio - mostrar desde esa fecha en adelante
            try:
                from datetime import datetime, timezone
                from django.utils import timezone as django_timezone
                
                if 'T' in from_date:
                    from_date_obj = datetime.fromisoformat(from_date.replace('Z', '+00:00'))
                else:
                    from_date_obj = datetime.fromisoformat(f"{from_date}T00:00:00+00:00")
                
                if from_date_obj.tzinfo is None:
                    from_date_obj = django_timezone.make_aware(from_date_obj, timezone.utc)
                
                # Configurar inicio del día
                start_datetime = from_date_obj.replace(hour=0, minute=0, second=0, microsecond=0)
                queryset = queryset.filter(entry_time__gte=start_datetime)
            except ValueError as e:
                logger.warning(f"Error parsing from_date: {e}")
                pass
        elif to_date:
            # Caso 3: Solo fecha fin - mostrar hasta esa fecha
            try:
                from datetime import datetime, timezone
                from django.utils import timezone as django_timezone
                
                if 'T' in to_date:
                    to_date_obj = datetime.fromisoformat(to_date.replace('Z', '+00:00'))
                else:
                    to_date_obj = datetime.fromisoformat(f"{to_date}T23:59:59+00:00")
                
                if to_date_obj.tzinfo is None:
                    to_date_obj = django_timezone.make_aware(to_date_obj, timezone.utc)
                
                # Configurar final del día
                end_datetime = to_date_obj.replace(hour=23, minute=59, second=59, microsecond=999999)
                queryset = queryset.filter(entry_time__lte=end_datetime)
            except ValueError as e:
                logger.warning(f"Error parsing to_date: {e}")
                pass
        # Caso 4: Sin fechas - no aplicar filtros de fecha (mostrar todo)
        
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
