from rest_framework.permissions import BasePermission


class IsAdminUser(BasePermission):
    """
    Permiso para verificar si el usuario es administrador
    """
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and 
            request.user.role == 'admin' and 
            request.user.is_verified
        )


class IsVerifiedUser(BasePermission):
    """
    Permiso para verificar si el usuario está verificado
    """
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and 
            request.user.is_verified
        )


class IsMonitorUser(BasePermission):
    """
    Permiso para verificar si el usuario es monitor verificado
    """
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and 
            request.user.role == 'monitor' and 
            request.user.is_verified
        )


class CanManageUsers(BasePermission):
    """
    Permiso para gestionar usuarios (solo administradores)
    """
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        # Solo administradores pueden gestionar usuarios
        if request.method in ['POST', 'PUT', 'PATCH', 'DELETE']:
            return request.user.is_admin and request.user.is_verified
        
        # Para GET, cualquier usuario verificado puede ver la lista
        return request.user.is_verified