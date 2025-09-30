from rest_framework import permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from .models import Room
from .serializers import RoomSerializer
from users.permissions import IsVerifiedUser


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
            'error': 'Sala no encontrada'
        }, status=status.HTTP_404_NOT_FOUND)