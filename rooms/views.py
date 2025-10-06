from rest_framework import permissions
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.authentication import TokenAuthentication
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from django.core.exceptions import ValidationError
from .models import Room, RoomEntry
from .serializers import (
    RoomSerializer, 
    RoomEntrySerializer, 
    RoomEntryCreateSerializer,
    RoomEntryExitSerializer,
    RoomCreateUpdateSerializer
)
from .services import RoomEntryBusinessLogic
from .permissions import IsAdminUser
from users.permissions import IsVerifiedUser
from django.db import transaction
from django.db import models
from django.utils import timezone


# ========== VISTAS DE SALAS (Sprint 1) ==========

@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def room_list_view(request):
    """
    Vista para listar todas las salas activas
    """
    rooms = Room.objects.filter(is_active=True).order_by('code')
    serializer = RoomSerializer(rooms, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def room_detail_view(request, room_id):
    """
    Vista para obtener detalles de una sala específica
    """
    try:
        room = Room.objects.get(id=room_id, is_active=True)
        serializer = RoomSerializer(room)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Room.DoesNotExist:
        return Response({
            'error': f'Sala con ID {room_id} no encontrada o inactiva'
        }, status=status.HTTP_404_NOT_FOUND)
    except ValueError:
        return Response({
            'error': f'ID de sala inválido: {room_id}'
        }, status=status.HTTP_400_BAD_REQUEST)


# ========== VISTAS DE REGISTRO DE ENTRADA/SALIDA (Sprint 2) ==========

@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsVerifiedUser])
def room_entry_create_view(request):
    """
    Registrar ingreso de un monitor a una sala con validaciones de negocio
    HU: Registro de fecha y hora exacta en cada acción
    HU: No se permite ingresar a otra sala sin antes haber salido
    """
    try:
        # Obtener datos del request
        room_id = request.data.get('room')
        notes = request.data.get('notes', '')
        
        if not room_id:
            return Response({
                'error': 'ID de sala requerido',
                'field': 'room'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Obtener la sala
        try:
            room = Room.objects.get(id=room_id, is_active=True)
        except Room.DoesNotExist:
            return Response({
                'error': 'Sala no encontrada o inactiva',
                'room_id': room_id,
                'field': 'room'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Usar el servicio de lógica de negocio
        result = RoomEntryBusinessLogic.create_room_entry_with_validations(
            user=request.user,
            room=room,
            notes=notes
        )
        
        if result['success']:
            # Serializar la entrada creada
            response_serializer = RoomEntrySerializer(result['entry'])
            return Response({
                'message': result['message'],
                'entry': response_serializer.data
            }, status=status.HTTP_201_CREATED)
        else:
            # Error de validación
            return Response({
                'error': result['error'],
                'details': result['details']
            }, status=status.HTTP_400_BAD_REQUEST)
            
    except Exception as e:
        return Response({
            'error': 'Error interno del servidor',
            'details': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['PATCH'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsVerifiedUser])
def room_entry_exit_view(request, entry_id):
    """
    Registrar salida de un monitor de una sala con validaciones de negocio
    HU: Registro de fecha y hora exacta en cada acción
    HU: El sistema calcule mis horas de permanencia
    HU: Si un monitor excede 8 horas seguidas, se genera notificación al admin
    """
    try:
        # Obtener notas adicionales si las hay
        notes = request.data.get('notes', '')
        
        # Usar el servicio de lógica de negocio
        result = RoomEntryBusinessLogic.exit_room_entry_with_validations(
            user=request.user,
            entry_id=entry_id,
            notes=notes
        )
        
        if result['success']:
            # Serializar la entrada actualizada
            response_serializer = RoomEntrySerializer(result['entry'])
            
            response_data = {
                'message': result['message'],
                'entry': response_serializer.data,
                'duration': result['duration_info']
            }
            
            # Agregar advertencia si se excedieron las 8 horas
            if 'warning' in result:
                response_data['warning'] = result['warning']
            
            return Response(response_data, status=status.HTTP_200_OK)
        else:
            # Determinar el código de estado según el tipo de error
            if result.get('error_type') == 'NOT_FOUND':
                status_code = status.HTTP_404_NOT_FOUND
            else:
                status_code = status.HTTP_400_BAD_REQUEST
                
            return Response({
                'error': result['error'],
                'details': result['details']
            }, status=status_code)
            
    except Exception as e:
        return Response({
            'error': 'Error interno del servidor',
            'details': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['PATCH'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsVerifiedUser])
def user_active_entry_exit_view(request):
    """
    Registrar salida de la entrada activa del usuario (sin necesidad de especificar ID)
    Solución minimalista para facilitar el uso del API
    """
    try:
        # Buscar la entrada activa del usuario
        try:
            active_entry = RoomEntry.objects.get(
                user=request.user,
                exit_time__isnull=True
            )
        except RoomEntry.DoesNotExist:
            return Response({
                'error': 'No tienes una entrada activa',
                'details': 'Debes ingresar a una sala antes de poder salir'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Usar el servicio con el ID de la entrada activa
        notes = request.data.get('notes', '')
        result = RoomEntryBusinessLogic.exit_room_entry_with_validations(
            user=request.user,
            entry_id=active_entry.id,
            notes=notes
        )
        
        if result['success']:
            response_serializer = RoomEntrySerializer(result['entry'])
            response_data = {
                'message': result['message'],
                'entry': response_serializer.data,
                'duration': result['duration_info']
            }
            
            if 'warning' in result:
                response_data['warning'] = result['warning']
            
            return Response(response_data, status=status.HTTP_200_OK)
        else:
            return Response({
                'error': result['error'],
                'details': result['details']
            }, status=status.HTTP_400_BAD_REQUEST)
            
    except Exception as e:
        return Response({
            'error': 'Error interno del servidor',
            'details': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsVerifiedUser])
def user_room_entries_view(request):
    """
    Historial de entradas del usuario autenticado
    HU: El historial refleja cada acción con sala y horario
    """
    entries = RoomEntry.objects.filter(user=request.user).select_related('room')
    serializer = RoomEntrySerializer(entries, many=True)
    return Response({
        'count': entries.count(),
        'entries': serializer.data
    }, status=status.HTTP_200_OK)


@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsVerifiedUser])
def user_active_entry_view(request):
    """
    Obtener entrada activa del usuario con información de duración
    HU: Validación de que no esté en dos salas al mismo tiempo
    HU: El sistema calcule mis horas de permanencia
    """
    try:
        # Usar el servicio de lógica de negocio
        session_info = RoomEntryBusinessLogic.get_user_active_session(request.user)
        
        if session_info['has_active_session']:
            serializer = RoomEntrySerializer(session_info['entry'])
            return Response({
                'has_active_entry': True,
                'active_entry': serializer.data,
                'duration_info': session_info['duration_info'],
                'warning': session_info['warning']
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                'has_active_entry': False,
                'active_entry': None,
                'duration_info': None
            }, status=status.HTTP_200_OK)
            
    except Exception as e:
        return Response({
            'error': 'Error al obtener sesión activa',
            'details': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsVerifiedUser])
def user_daily_summary_view(request):
    """
    Obtener resumen diario de entradas del usuario
    HU: El sistema calcule mis horas de permanencia
    """
    try:
        # Obtener fecha del query param o usar fecha actual
        date_str = request.GET.get('date')
        date = None
        
        if date_str:
            from datetime import datetime
            try:
                date = datetime.strptime(date_str, '%Y-%m-%d').date()
            except ValueError:
                return Response({
                    'error': 'Formato de fecha inválido. Use YYYY-MM-DD'
                }, status=status.HTTP_400_BAD_REQUEST)
        
        # Usar el servicio de lógica de negocio
        summary = RoomEntryBusinessLogic.get_user_daily_summary(request.user, date)
        
        return Response(summary, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({
            'error': 'Error al obtener resumen diario',
            'details': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsVerifiedUser])
def room_current_occupants_view(request, room_id):
    """
    Lista de usuarios actualmente en una sala específica
    """
    room = get_object_or_404(Room, id=room_id, is_active=True)
    active_entries = RoomEntry.objects.filter(
        room=room,
        exit_time__isnull=True
    ).select_related('user')
    
    serializer = RoomEntrySerializer(active_entries, many=True)
    return Response({
        'room': RoomSerializer(room).data,
        'current_occupants': active_entries.count(),
        'entries': serializer.data
    }, status=status.HTTP_200_OK)


# ========== VISTAS DE ADMINISTRACIÓN DE SALAS (SOLO ADMINS) ==========

@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAdminUser])
def admin_room_create_view(request):
    """
    Crear una nueva sala - Solo administradores
    """
    try:
        serializer = RoomCreateUpdateSerializer(data=request.data)
        
        if serializer.is_valid():
            with transaction.atomic():
                room = serializer.save()
                response_serializer = RoomSerializer(room)
                return Response({
                    'message': 'Sala creada exitosamente',
                    'room': response_serializer.data
                }, status=status.HTTP_201_CREATED)
        
        return Response({
            'error': 'Datos inválidos para crear la sala',
            'details': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
        
    except Exception as e:
        return Response({
            'error': 'Error interno del servidor',
            'details': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['PUT', 'PATCH'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAdminUser])
def admin_room_update_view(request, room_id):
    """
    Actualizar una sala existente - Solo administradores
    """
    try:
        room = get_object_or_404(Room, id=room_id)
        
        # Verificar si la sala tiene ocupantes activos antes de permitir ciertos cambios
        active_occupants = RoomEntry.objects.filter(room=room, exit_time__isnull=True).count()
        
        if active_occupants > 0 and 'is_active' in request.data and not request.data['is_active']:
            return Response({
                'error': 'No se puede desactivar una sala con ocupantes activos',
                'details': f'La sala tiene {active_occupants} ocupantes actualmente.',
                'active_occupants': active_occupants
            }, status=status.HTTP_400_BAD_REQUEST)
        
        partial = request.method == 'PATCH'
        serializer = RoomCreateUpdateSerializer(room, data=request.data, partial=partial)
        
        if serializer.is_valid():
            with transaction.atomic():
                updated_room = serializer.save()
                response_serializer = RoomSerializer(updated_room)
                return Response({
                    'message': 'Sala actualizada exitosamente',
                    'room': response_serializer.data
                })
        
        return Response({
            'error': 'Datos inválidos para actualizar la sala',
            'details': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
        
    except Exception as e:
        return Response({
            'error': 'Error interno del servidor',
            'details': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['DELETE'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAdminUser])
def admin_room_delete_view(request, room_id):
    """
    Eliminar una sala - Solo administradores
    Soft delete: marca como inactiva en lugar de eliminar físicamente si tiene historial
    """
    try:
        room = get_object_or_404(Room, id=room_id)
        
        # Verificar si la sala tiene ocupantes activos
        active_occupants = RoomEntry.objects.filter(room=room, exit_time__isnull=True).count()
        
        if active_occupants > 0:
            return Response({
                'error': 'No se puede eliminar una sala con ocupantes activos',
                'details': f'La sala tiene {active_occupants} ocupantes actualmente. Debe esperar a que salgan antes de eliminarla.',
                'active_occupants': active_occupants
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Verificar si la sala tiene historial de entradas
        total_entries = RoomEntry.objects.filter(room=room).count()
        
        if total_entries > 0:
            # Soft delete: marcar como inactiva
            with transaction.atomic():
                room.is_active = False
                room.name = f"{room.name} (ELIMINADA)"
                room.save()
            
            return Response({
                'message': 'Sala marcada como eliminada exitosamente',
                'details': f'La sala tenía {total_entries} registros históricos, por lo que se marcó como inactiva en lugar de eliminarla físicamente.',
                'action': 'soft_delete',
                'room': {
                    'id': room.id,
                    'name': room.name,
                    'is_active': room.is_active
                }
            })
        else:
            # Hard delete: eliminar físicamente si no tiene historial
            room_info = {
                'id': room.id,
                'name': room.name,
                'code': room.code
            }
            room.delete()
            
            return Response({
                'message': 'Sala eliminada completamente',
                'details': 'La sala no tenía registros históricos, por lo que se eliminó completamente.',
                'action': 'hard_delete',
                'deleted_room': room_info
            })
            
    except Exception as e:
        return Response({
            'error': 'Error interno del servidor',
            'details': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAdminUser])
def admin_rooms_list_view(request):
    """
    Lista todas las salas (incluyendo inactivas opcionalmente) - Solo administradores
    """
    try:
        # Parámetros de filtrado
        include_inactive = request.GET.get('include_inactive', 'false').lower() == 'true'
        search = request.GET.get('search', '')
        
        # Query base
        rooms = Room.objects.all()
        
        # Filtros
        if not include_inactive:
            rooms = rooms.filter(is_active=True)
        
        if search:
            rooms = rooms.filter(
                models.Q(name__icontains=search) | 
                models.Q(code__icontains=search) |
                models.Q(description__icontains=search)
            )
        
        # Ordenar por fecha de creación (más recientes primero)
        rooms = rooms.order_by('-created_at')
        
        serializer = RoomSerializer(rooms, many=True)
        
        return Response({
            'count': rooms.count(),
            'include_inactive': include_inactive,
            'search': search if search else None,
            'rooms': serializer.data
        })
        
    except Exception as e:
        return Response({
            'error': 'Error interno del servidor',
            'details': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAdminUser])
def admin_room_detail_view(request, room_id):
    """
    Detalle completo de una sala con estadísticas - Solo administradores
    """
    try:
        room = get_object_or_404(Room, id=room_id)
        
        # Información adicional para administradores
        active_entries = RoomEntry.objects.filter(room=room, exit_time__isnull=True).select_related('user')
        total_entries = RoomEntry.objects.filter(room=room).count()
        
        # Calcular horas totales de uso de la sala
        completed_entries = RoomEntry.objects.filter(room=room, exit_time__isnull=False)
        total_minutes = 0
        for entry in completed_entries:
            duration = entry.exit_time - entry.entry_time
            total_minutes += duration.total_seconds() / 60
        
        total_hours_calculated = round(total_minutes / 60, 2) if total_minutes > 0 else 0
        
        serializer = RoomSerializer(room)
        
        return Response({
            'room': serializer.data,
            'statistics': {
                'current_occupants': active_entries.count(),
                'total_entries_historical': total_entries,
                'total_hours_usage': total_hours_calculated,
                'active_entries': [
                    {
                        'id': entry.id,
                        'user_username': entry.user.username,
                        'user_full_name': entry.user.get_full_name(),
                        'entry_time': entry.entry_time,
                        'duration_minutes': round((timezone.now() - entry.entry_time).total_seconds() / 60, 2)
                    }
                    for entry in active_entries
                ]
            }
        })
        
    except Exception as e:
        return Response({
            'error': 'Error interno del servidor',
            'details': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)