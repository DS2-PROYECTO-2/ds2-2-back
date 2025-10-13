from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.authentication import TokenAuthentication
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Notification
from .serializers import NotificationSerializer
from .services import NotificationService

@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def notifications_list(request):
    """
    Lista todas las notificaciones del usuario
    """
    try:
        notifications = Notification.objects.filter(user=request.user).order_by('-created_at')
        serializer = NotificationSerializer(notifications, many=True)
        return Response({
            'notifications': serializer.data,
            'count': notifications.count()
        }, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def notifications_unread(request):
    """
    Lista solo las notificaciones no leídas del usuario
    """
    try:
        unread_notifications = Notification.objects.filter(
            user=request.user, 
            read=False
        ).order_by('-created_at')
        serializer = NotificationSerializer(unread_notifications, many=True)
        return Response({
            'success': True,
            'notifications': serializer.data,
            'count': unread_notifications.count()
        }, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def notifications_unread_count(request):
    """
    Obtener solo el contador de notificaciones no leídas
    """
    try:
        unread_count = Notification.objects.filter(user=request.user, read=False).count()
        return Response({
            'success': True,
            'unread_count': unread_count
        }, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def notifications_summary(request):
    """
    Obtener resumen de notificaciones del usuario
    """
    try:
        summary = NotificationService.get_user_notifications_summary(request.user)
        serializer = NotificationSerializer(summary['recent'], many=True)
        
        return Response({
            'success': True,
            'total': summary['total'],
            'unread': summary['unread'],
            'recent': serializer.data,
            'by_type': list(summary['by_type'])
        }, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['PATCH'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def notifications_mark_all_read(request):
    """
    Marcar todas las notificaciones del usuario como leídas
    """
    try:
        updated_count = NotificationService.mark_all_as_read(request.user)
        return Response({
            'success': True,
            'message': f'{updated_count} notificaciones marcadas como leídas',
            'updated_count': updated_count
        }, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['PATCH'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def notifications_mark_read(request, notification_id):
    """
    Marcar una notificación específica como leída
    """
    try:
        if NotificationService.mark_notification_as_read(notification_id, request.user):
            return Response({
                'success': True,
                'message': 'Notificación marcada como leída'
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                'success': False,
                'error': 'No se pudo marcar la notificación'
            }, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
