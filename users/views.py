from rest_framework import status, generics, permissions
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.authentication import TokenAuthentication
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from django.contrib.auth import login, logout, update_session_auth_hash
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from .models import User
from .serializers import (
    UserRegistrationSerializer,
    UserLoginSerializer,
    UserProfileSerializer,
    UserProfileCompleteSerializer,
    AdminUserListSerializer,
    AdminUserVerificationSerializer,
    ChangePasswordSerializer
)
from .permissions import IsAdminUser, IsVerifiedUser, CanManageUsers


@csrf_exempt
@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def register_view(request):
    """
    Vista para el registro de nuevos usuarios
    """
    serializer = UserRegistrationSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        
        # Mensaje diferenciado según el rol
        if user.role == 'monitor':
            message = 'Usuario registrado exitosamente. Esperando verificación del administrador.'
        else:
            message = 'Administrador registrado y verificado exitosamente.'
        
        return Response({
            'message': message,
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'role': user.role,
                'is_verified': user.is_verified
            }
        }, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@csrf_exempt
@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def login_view(request):
    """
    Vista para el login de usuarios
    """
    serializer = UserLoginSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.validated_data['user']
        
        # Crear o obtener token
        token, created = Token.objects.get_or_create(user=user)
        
        # Login del usuario
        login(request, user)
        
        return Response({
            'message': 'Login exitoso',
            'token': token.key,
            'user': UserProfileCompleteSerializer(user).data
        }, status=status.HTTP_200_OK)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@csrf_exempt
@csrf_exempt
@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def logout_view(request):
    """
    Vista para el logout de usuarios
    """
    try:
        # Eliminar el token del usuario
        Token.objects.filter(user=request.user).delete()
        logout(request)
        return Response({
            'message': 'Logout exitoso'
        }, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({
            'error': f'Error durante el logout: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsVerifiedUser])
def profile_view(request):
    """
    Vista para obtener el perfil del usuario autenticado
    """
    serializer = UserProfileSerializer(request.user)
    return Response(serializer.data, status=status.HTTP_200_OK)


@csrf_exempt
@api_view(['PUT', 'PATCH'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsVerifiedUser])
def update_profile_view(request):
    """
    Vista para actualizar el perfil del usuario
    """
    serializer = UserProfileSerializer(
        request.user, 
        data=request.data, 
        partial=True
    )
    if serializer.is_valid():
        serializer.save()
        return Response({
            'message': 'Perfil actualizado exitosamente',
            'user': serializer.data
        }, status=status.HTTP_200_OK)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@csrf_exempt
@api_view(['POST'])
@permission_classes([IsVerifiedUser])
def change_password_view(request):
    """
    Vista para cambiar contraseña
    """
    serializer = ChangePasswordSerializer(data=request.data, context={'request': request})
    if serializer.is_valid():
        serializer.save()
        update_session_auth_hash(request, request.user)  # Mantener la sesión activa
        return Response({
            'message': 'Contraseña cambiada exitosamente'
        }, status=status.HTTP_200_OK)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def admin_users_list_view(request):
    """
    Vista para que los administradores vean la lista de usuarios
    """
    users = User.objects.all().order_by('-created_at')
    
    # Filtros opcionales
    role = request.query_params.get('role')
    is_verified = request.query_params.get('is_verified')
    
    if role:
        users = users.filter(role=role)
    if is_verified is not None:
        users = users.filter(is_verified=is_verified.lower() == 'true')
    
    serializer = AdminUserListSerializer(users, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@csrf_exempt
@api_view(['PATCH'])
@permission_classes([permissions.AllowAny])
def admin_verify_user_view(request, user_id):
    """
    Vista para que los administradores verifiquen usuarios
    """
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return Response({
            'error': f'Usuario con ID {user_id} no encontrado'
        }, status=status.HTTP_404_NOT_FOUND)
    except ValueError:
        return Response({
            'error': f'ID de usuario inválido: {user_id}'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    serializer = AdminUserVerificationSerializer(
        user, 
        data=request.data, 
        context={'request': request},
        partial=True
    )
    
    if serializer.is_valid():
        # Marcar que la verificación cambió para activar el signal
        user._verification_changed = True
        serializer.save()
        
        return Response({
            'message': f'Usuario {user.username} actualizado exitosamente',
            'user': AdminUserListSerializer(user).data
        }, status=status.HTTP_200_OK)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsVerifiedUser])
def dashboard_view(request):
    """
    Vista básica del dashboard según el rol del usuario
    """
    user = request.user
    
    if user.is_admin:
        # Dashboard para administradores
        total_users = User.objects.count()
        pending_verifications = User.objects.filter(is_verified=False, role='monitor').count()
        total_monitors = User.objects.filter(role='monitor').count()
        verified_monitors = User.objects.filter(role='monitor', is_verified=True).count()
        
        return Response({
            'user': UserProfileCompleteSerializer(user).data,
            'dashboard_type': 'admin',
            'stats': {
                'total_users': total_users,
                'pending_verifications': pending_verifications,
                'total_monitors': total_monitors,
                'verified_monitors': verified_monitors,
            },
            'message': f'Bienvenido al panel de administrador, {user.get_full_name()}'
        })
    
    else:
        # Dashboard para monitores
        return Response({
            'user': UserProfileCompleteSerializer(user).data,
            'dashboard_type': 'monitor',
            'stats': {
                'account_status': 'verified' if user.is_verified else 'pending',
                'verification_date': user.verification_date,
            },
            'message': f'Bienvenido, {user.get_full_name()}'
        })