from rest_framework.permissions import BasePermission


class IsAdminUser(BasePermission):
    """
    Permiso personalizado para permitir solo a usuarios administradores verificados.
    """
    
    def has_permission(self, request, view):
        return (
            request.user and 
            request.user.is_authenticated and 
            hasattr(request.user, 'role') and 
            request.user.role == 'admin' and
            request.user.is_verified
        )
    
    message = "Solo los administradores verificados pueden realizar esta acción."