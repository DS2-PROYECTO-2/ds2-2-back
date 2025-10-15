from rest_framework import status, permissions
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.authentication import TokenAuthentication
from rest_framework.response import Response
from django.shortcuts import redirect
from rest_framework.authtoken.models import Token
from django.contrib.auth import login, logout, update_session_auth_hash
from django.views.decorators.csrf import csrf_exempt
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
from .permissions import IsAdminUser, IsVerifiedUser
from django.conf import settings
from .models import ApprovalLink
import hashlib
import logging
from .serializers import PasswordResetRequestSerializer, PasswordResetConfirmSerializer
from rest_framework.permissions import AllowAny
from django.db import transaction

logger = logging.getLogger(__name__)



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
    OPTIMIZADA: Respuesta más rápida + manejo de errores mejorado
    """
    try:
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            
            # OPTIMIZACIÓN: Respuesta inmediata sin esperar signals
            # Los signals se ejecutan en background
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
        
    except Exception as e:
        logger.error(f"Error en register_view: {e}")
        return Response({
            'error': 'Error interno del servidor. Inténtalo de nuevo.'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


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


@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAdminUser])
def admin_promote_user_view(request, user_id):
    """
    Vista minimalista para que los administradores asciendan monitores a administradores.
    Reglas:
    - Solo admins pueden usar este endpoint
    - Solo se puede ascender monitores a admins
    - No se puede cambiar el rol de otros admins
    """
    try:
        target_user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return Response({
            'error': f'Usuario con ID {user_id} no encontrado'
        }, status=status.HTTP_404_NOT_FOUND)
    
    # Validar que el usuario objetivo sea monitor
    if target_user.role != 'monitor':
        return Response({
            'error': f'Solo se pueden ascender monitores a administradores. Usuario actual: {target_user.role}'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Ascender a admin
    target_user.role = 'admin'
    target_user.save()
    
    return Response({
        'message': f'Usuario {target_user.username} ascendido a administrador exitosamente',
        'user': {
            'id': target_user.id,
            'username': target_user.username,
            'role': target_user.role,
            'is_verified': target_user.is_verified
        }
    }, status=status.HTTP_200_OK)


@api_view(['PATCH'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAdminUser])
def admin_edit_user_view(request, user_id):
    """
    Vista consolidada para que los administradores editen información completa de usuarios
    Incluye: información personal, rol y verificación
    """
    try:
        target_user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return Response({
            'error': f'Usuario con ID {user_id} no encontrado'
        }, status=status.HTTP_404_NOT_FOUND)
    
    # Prevenir que un admin edite otro admin (excepto a sí mismo)
    if target_user.role == 'admin' and target_user != request.user:
        return Response({
            'error': 'No se puede editar información de otros administradores'
        }, status=status.HTTP_403_FORBIDDEN)
    
    # Campos editables básicos
    basic_fields = ['first_name', 'last_name', 'email', 'phone', 'identification']
    update_data = {k: v for k, v in request.data.items() if k in basic_fields}
    
    # Campos administrativos especiales
    admin_fields = {}
    changes_made = []
    
    # Manejo de cambio de rol
    if 'role' in request.data:
        new_role = request.data['role']
        if new_role in ['admin', 'monitor']:
            if target_user.role != new_role:
                # Solo permitir ascender monitores a admins
                if target_user.role == 'monitor' and new_role == 'admin':
                    admin_fields['role'] = new_role
                    changes_made.append(f'ascendido a {new_role}')
                # Permitir degradar admins a monitores (solo para casos especiales)
                elif target_user.role == 'admin' and new_role == 'monitor':
                    admin_fields['role'] = new_role
                    changes_made.append(f'cambiado a {new_role}')
                else:
                    return Response({
                        'error': f'Cambio de rol inválido: de {target_user.role} a {new_role}'
                    }, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({
                'error': 'Rol inválido. Solo se permite "admin" o "monitor"'
            }, status=status.HTTP_400_BAD_REQUEST)
    
    # Manejo de verificación
    if 'is_verified' in request.data:
        new_verification = request.data['is_verified']
        # Convertir string a boolean si es necesario
        if isinstance(new_verification, str):
            if new_verification.lower() == 'true':
                new_verification = True
            elif new_verification.lower() == 'false':
                new_verification = False
            else:
                return Response({
                    'error': 'is_verified debe ser true o false'
                }, status=status.HTTP_400_BAD_REQUEST)
        elif not isinstance(new_verification, bool):
            return Response({
                'error': 'is_verified debe ser true o false'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        if target_user.is_verified != new_verification:
            admin_fields['is_verified'] = new_verification
            admin_fields['verified_by'] = request.user if new_verification else None
            # Marcar que la verificación cambió para activar el signal
            target_user._verification_changed = True
            changes_made.append('verificado' if new_verification else 'desverificado')
    
    # Verificar que al menos hay algo que actualizar
    if not update_data and not admin_fields:
        return Response({
            'error': 'No se proporcionaron campos válidos para actualizar'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Actualizar campos básicos
    for field, value in update_data.items():
        if getattr(target_user, field) != value:
            setattr(target_user, field, value)
            changes_made.append(f'{field} actualizado')
    
    # Actualizar campos administrativos
    for field, value in admin_fields.items():
        setattr(target_user, field, value)
    
    try:
        target_user.save()
    except Exception as e:
        return Response({
            'error': f'Error al actualizar usuario: {str(e)}'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Mensaje de respuesta descriptivo
    if changes_made:
        changes_text = ', '.join(changes_made)
        message = f'Usuario {target_user.username} actualizado exitosamente: {changes_text}'
    else:
        message = f'Usuario {target_user.username} - sin cambios realizados'
    
    return Response({
        'message': message,
        'user': {
            'id': target_user.id,
            'username': target_user.username,
            'first_name': target_user.first_name,
            'last_name': target_user.last_name,
            'email': target_user.email,
            'phone': target_user.phone,
            'identification': target_user.identification,
            'role': target_user.role,
            'is_verified': target_user.is_verified
        }
    }, status=status.HTTP_200_OK)


@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAdminUser])
def admin_user_detail_view(request, user_id):
    """
    Vista para obtener detalles de un usuario específico
    """
    try:
        target_user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return Response({
            'error': f'Usuario con ID {user_id} no encontrado'
        }, status=status.HTTP_404_NOT_FOUND)
    
    return Response({
        'user': {
            'id': target_user.id,
            'username': target_user.username,
            'first_name': target_user.first_name,
            'last_name': target_user.last_name,
            'email': target_user.email,
            'phone': target_user.phone,
            'identification': target_user.identification,
            'role': target_user.role,
            'is_verified': target_user.is_verified,
            'date_joined': target_user.date_joined,
            'last_login': target_user.last_login,
            'is_active': target_user.is_active
        }
    }, status=status.HTTP_200_OK)


@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAdminUser])
def admin_users_search_view(request):
    """
    Vista para buscar usuarios con filtros múltiples
    """
    queryset = User.objects.all()
    
    # Filtro por rol
    role = request.query_params.get('role')
    if role in ['admin', 'monitor']:
        queryset = queryset.filter(role=role)
    
    # Filtro por estado de verificación
    is_verified = request.query_params.get('is_verified')
    if is_verified in ['true', 'false']:
        queryset = queryset.filter(is_verified=is_verified.lower() == 'true')
    
    # Filtro por estado activo
    is_active = request.query_params.get('is_active')
    if is_active in ['true', 'false']:
        queryset = queryset.filter(is_active=is_active.lower() == 'true')
    
    # Búsqueda por texto (username, email, nombre)
    search = request.query_params.get('search')
    if search:
        from django.db.models import Q
        queryset = queryset.filter(
            Q(username__icontains=search) |
            Q(email__icontains=search) |
            Q(first_name__icontains=search) |
            Q(last_name__icontains=search) |
            Q(identification__icontains=search)
        )
    
    # Ordenamiento
    order_by = request.query_params.get('order_by', 'date_joined')
    if order_by.startswith('-'):
        order_field = order_by[1:]
    else:
        order_field = order_by
    
    valid_order_fields = ['username', 'email', 'role', 'is_verified', 'date_joined']
    if order_field in valid_order_fields:
        queryset = queryset.order_by(order_by)
    
    # Paginación básica
    page_size = min(int(request.query_params.get('page_size', 20)), 100)  # Max 100
    page = int(request.query_params.get('page', 1))
    start = (page - 1) * page_size
    end = start + page_size
    
    total_count = queryset.count()
    users = queryset[start:end]
    
    return Response({
        'users': [{
            'id': user.id,
            'username': user.username,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'email': user.email,
            'role': user.role,
            'is_verified': user.is_verified,
            'is_active': user.is_active,
            'date_joined': user.date_joined
        } for user in users],
        'pagination': {
            'total_count': total_count,
            'page': page,
            'page_size': page_size,
            'total_pages': (total_count + page_size - 1) // page_size
        },
        'filters_applied': {
            'role': role,
            'is_verified': is_verified,
            'is_active': is_active,
            'search': search,
            'order_by': order_by
        }
    }, status=status.HTTP_200_OK)


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
        return redirect(f"{settings.FRONTEND_BASE_URL}/admin/approval?error=missing_token")
    
    # Hash del token para buscar en DB
    token_hash = hashlib.sha256(token.encode()).hexdigest()
    
    try:
        approval_link = ApprovalLink.objects.get(
            token_hash=token_hash,
            action=ApprovalLink.APPROVE
        )
    except ApprovalLink.DoesNotExist:
        return redirect(f"{settings.FRONTEND_BASE_URL}/admin/approval?error=invalid_token")

    if not approval_link.is_valid():
        # Si expiró o ya fue usado, bórralo y redirige con error
        approval_link.delete()
        error_type = "expired" if approval_link.is_expired() else "used"
        return redirect(f"{settings.FRONTEND_BASE_URL}/admin/approval?error={error_type}")

    user = approval_link.user

    with transaction.atomic():
        # aplicar acción
        user._verification_changed = True
        user.is_verified = True
        user.verified_by = None
        user.save()

        # borrar ambos (approve/reject) para este usuario
        ApprovalLink.objects.filter(user=user).delete()

    # Redirigir al frontend con éxito
    return redirect(f"{settings.FRONTEND_BASE_URL}/admin/approval?action=approved&user={user.username}")

@api_view(['GET'])
@permission_classes([])
def admin_user_delete_via_token(request):
    token = request.query_params.get("token")
    if not token:
        return redirect(f"{settings.FRONTEND_BASE_URL}/admin/approval?error=missing_token")
    
    # Hash del token para buscar en DB
    token_hash = hashlib.sha256(token.encode()).hexdigest()
    
    try:
        approval_link = ApprovalLink.objects.get(
            token_hash=token_hash,
            action=ApprovalLink.REJECT
        )
    except ApprovalLink.DoesNotExist:
        return redirect(f"{settings.FRONTEND_BASE_URL}/admin/approval?error=invalid_token")
    
    if not approval_link.is_valid():
        approval_link.delete()
        error_type = "expired" if approval_link.is_expired() else "used"
        return redirect(f"{settings.FRONTEND_BASE_URL}/admin/approval?error={error_type}")

    user = approval_link.user
    username = user.username

    with transaction.atomic():
        # borrar ambos enlaces primero para no dejar basura si falla delete
        ApprovalLink.objects.filter(user=user).delete()
        user.delete()  # dispara post_delete y envía correo

    # Redirigir al frontend con éxito
    return redirect(f"{settings.FRONTEND_BASE_URL}/admin/approval?action=rejected&user={username}")

@api_view(['POST'])
@permission_classes([AllowAny])
def password_reset_request_view(request):
    serializer = PasswordResetRequestSerializer(data=request.data)
    if serializer.is_valid():
        result = serializer.save()
        # Respuesta explícita según existencia
        # Mantener mensaje genérico esperado por los tests
        if not result.get('exists'):
            return Response({
                'message': 'El email no existe en la base de datos',
                'exists': False
            }, status=status.HTTP_200_OK)

        response_payload = {
            'message': 'Si el email existe, recibirás un enlace de restablecimiento',
            'exists': True
        }
        if 'reset_url' in result:
            response_payload['reset_url'] = result['reset_url']
            response_payload['note'] = 'Enlace de desarrollo - copia y pega en el navegador'
        return Response(response_payload, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
def password_reset_confirm_view(request):
    if request.method == 'GET':
        # Validar token y devolver datos del usuario
        token = request.query_params.get('token')
        if not token:
            return Response({'error': 'Token no proporcionado'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Verificar que el token existe y es válido
        from users.models import PasswordReset
        import hashlib
        
        token_hash = hashlib.sha256(token.encode()).hexdigest()
        try:
            password_reset = PasswordReset.objects.get(token_hash=token_hash)
            if not password_reset.is_valid():
                return Response({'error': 'Token expirado o ya usado'}, status=status.HTTP_400_BAD_REQUEST)
            
            # Devolver datos del usuario para el frontend
            return Response({
                'valid': True,
                'user': {
                    'id': password_reset.user.id,
                    'username': password_reset.user.username,
                    'email': password_reset.user.email,
                    'full_name': password_reset.user.get_full_name()
                }
            }, status=status.HTTP_200_OK)
            
        except PasswordReset.DoesNotExist:
            return Response({'error': 'Token inválido'}, status=status.HTTP_400_BAD_REQUEST)
    
    else:  # POST
        serializer = PasswordResetConfirmSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'Contraseña actualizada correctamente'}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)