from rest_framework import permissions
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.authentication import TokenAuthentication
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from .models import Room, RoomEntry
from .serializers import (
    RoomSerializer, 
    RoomEntrySerializer, 
    RoomEntryCreateSerializer,
    RoomEntryExitSerializer
)
from users.permissions import IsVerifiedUser


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
    Registrar ingreso de un monitor a una sala
    HU: Registro de fecha y hora exacta en cada acción
    """
    serializer = RoomEntryCreateSerializer(data=request.data, context={'request': request})
    
    if serializer.is_valid():
        room_entry = serializer.save()
        # Retornar la entrada creada con datos completos
        response_serializer = RoomEntrySerializer(room_entry)
        return Response({
            'message': 'Ingreso registrado exitosamente',
            'entry': response_serializer.data
        }, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PATCH'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsVerifiedUser])
def room_entry_exit_view(request, entry_id):
    """
    Registrar salida de un monitor de una sala
    HU: Registro de fecha y hora exacta en cada acción
    """
    room_entry = get_object_or_404(
        RoomEntry, 
        id=entry_id, 
        user=request.user,
        exit_time__isnull=True  # Solo entradas activas
    )
    
    serializer = RoomEntryExitSerializer(room_entry, data=request.data, partial=True)
    
    if serializer.is_valid():
        updated_entry = serializer.save()
        response_serializer = RoomEntrySerializer(updated_entry)
        return Response({
            'message': 'Salida registrada exitosamente',
            'entry': response_serializer.data
        }, status=status.HTTP_200_OK)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


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
    Obtener entrada activa del usuario (si existe)
    HU: Validación de que no esté en dos salas al mismo tiempo
    """
    try:
        active_entry = RoomEntry.objects.get(
            user=request.user,
            exit_time__isnull=True
        )
        serializer = RoomEntrySerializer(active_entry)
        return Response({
            'has_active_entry': True,
            'active_entry': serializer.data
        }, status=status.HTTP_200_OK)
    except RoomEntry.DoesNotExist:
        return Response({
            'has_active_entry': False,
            'active_entry': None
        }, status=status.HTTP_200_OK)


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