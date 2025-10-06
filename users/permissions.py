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
        user = getattr(request, 'user', None)
        return bool(
            user is not None and
            getattr(user, 'is_authenticated', False) and
            getattr(user, 'is_verified', False)
        )


class IsMonitorUser(BasePermission):
    """
    Permiso para verificar si el usuario es monitor verificado
    """
    def has_permission(self, request, view):
        user = getattr(request, 'user', None)
        return bool(
            user is not None and
            getattr(user, 'is_authenticated', False) and 
            getattr(user, 'role', None) == 'monitor' and 
            getattr(user, 'is_verified', False)
        )


class CanManageUsers(BasePermission):
    """
    Permiso para gestionar usuarios (solo administradores)
    """
    def has_permission(self, request, view):
        user = getattr(request, 'user', None)
        if not (user is not None and getattr(user, 'is_authenticated', False)):
            return False
        
        # Solo administradores pueden gestionar usuarios
        if request.method in ['POST', 'PUT', 'PATCH', 'DELETE']:
            return getattr(user, 'is_admin', False) and getattr(user, 'is_verified', False)
        
        # Para GET, cualquier usuario verificado puede ver la lista
        return getattr(user, 'is_verified', False)