from rest_framework import status, generics, permissions
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.authentication import TokenAuthentication
from rest_framework.response import Response
from django.http import HttpResponse
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
from django.conf import settings
from users.utils import verify_action_token
from .models import ApprovalLink
import hashlib
from django.utils import timezone
def _html_message(text: str, ok: bool) -> str:
    color = "#16a34a" if ok else "#dc2626"
    title = "Operación exitosa" if ok else "No se pudo completar la operación"
    return f"""<!doctype html><html><head><meta charset=\"utf-8\"><title>{title}</title></head>
<body style=\"font-family:system-ui,Segoe UI,Arial;margin:40px;background:#f6f7f9;\">
  <div style=\"max-width:640px;margin:0 auto;background:#ffffff;border-radius:12px;box-shadow:0 6px 24px rgba(0,0,0,.08);overflow:hidden;\">
    <div style=\"padding:20px 24px;border-bottom:1px solid #eef2f7;\">
      <h2 style=\"margin:0;color:{color};\">{title}</h2>
    </div>
    <div style=\"padding:20px 24px;\">
      <p style=\"white-space:pre-wrap;color:#111827;\">{text}</p>
    </div>
  </div>
  <p style=\"text-align:center;color:#9ca3af;font-size:12px;margin-top:16px;\">DS2 • Confirmación</p>
</body></html>"""



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
@authentication_classes([TokenAuthentication])
@permission_classes([IsAdminUser])
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
@authentication_classes([TokenAuthentication])
@permission_classes([IsAdminUser])
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

@api_view(['DELETE'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAdminUser])  # usa tu permiso de admin
def admin_delete_user_view(request, user_id):
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return Response({'error': f'Usuario con ID {user_id} no encontrado'}, status=status.HTTP_404_NOT_FOUND)

    user.delete()  # esto dispara post_delete y enviará el correo
    return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['GET'])
@permission_classes([])  # validación por token, no requiere login
def admin_user_activate_via_token(request):
    token = request.query_params.get("token")
    if not token:
        return HttpResponse(_html_message("Falta token.", False), status=status.HTTP_400_BAD_REQUEST)
    
    # Hash del token para buscar en DB
    token_hash = hashlib.sha256(token.encode()).hexdigest()
    
    try:
        approval_link = ApprovalLink.objects.get(
            token_hash=token_hash,
            action=ApprovalLink.APPROVE
        )
    except ApprovalLink.DoesNotExist:
        return HttpResponse(_html_message("Enlace inválido.", False), status=status.HTTP_400_BAD_REQUEST)
    
    # Validar que no esté usado ni expirado
    if not approval_link.is_valid():
        if approval_link.is_used():
            return HttpResponse(_html_message("Este enlace ya fue usado.", False), status=status.HTTP_400_BAD_REQUEST)
        elif approval_link.is_expired():
            return HttpResponse(_html_message("El enlace expiró.", False), status=status.HTTP_400_BAD_REQUEST)
    
    user = approval_link.user
    
    # Marcar ambos enlaces (approve y reject) como usados para invalidar ambos
    ApprovalLink.objects.filter(
        user=user,
        action__in=[ApprovalLink.APPROVE, ApprovalLink.REJECT]
    ).update(used_at=timezone.now())
    
    # Ejecutar la acción
    user._verification_changed = True
    user.is_verified = True
    user.verified_by = None  # sin sesión; opcional
    user.save()
    
    return HttpResponse(_html_message(f"El usuario @{user.username} ha sido verificado.", True), status=200)

@api_view(['GET'])
@permission_classes([])
def admin_user_delete_via_token(request):
    token = request.query_params.get("token")
    if not token:
        return HttpResponse(_html_message("Falta token.", False), status=status.HTTP_400_BAD_REQUEST)
    
    # Hash del token para buscar en DB
    token_hash = hashlib.sha256(token.encode()).hexdigest()
    
    try:
        approval_link = ApprovalLink.objects.get(
            token_hash=token_hash,
            action=ApprovalLink.REJECT
        )
    except ApprovalLink.DoesNotExist:
        return HttpResponse(_html_message("Enlace inválido.", False), status=status.HTTP_400_BAD_REQUEST)
    
    # Validar que no esté usado ni expirado
    if not approval_link.is_valid():
        if approval_link.is_used():
            return HttpResponse(_html_message("Este enlace ya fue usado.", False), status=status.HTTP_400_BAD_REQUEST)
        elif approval_link.is_expired():
            return HttpResponse(_html_message("El enlace expiró.", False), status=status.HTTP_400_BAD_REQUEST)
    
    user = approval_link.user
    
    # Marcar ambos enlaces (approve y reject) como usados para invalidar ambos
    ApprovalLink.objects.filter(
        user=user,
        action__in=[ApprovalLink.APPROVE, ApprovalLink.REJECT]
    ).update(used_at=timezone.now())
    
    # Ejecutar la acción
    username = user.username
    user.delete()  # esto dispara post_delete y enviará el correo
    
    return HttpResponse(_html_message(f"El usuario @{username} ha sido eliminado.", True), status=200)