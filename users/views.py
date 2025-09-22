from rest_framework import viewsets, permissions
from .models import User
from .serializers import UserSerializer, UserCreateSerializer


class IsAdminUser(permissions.BasePermission):
    """
    Permiso personalizado que solo permite acceso a administradores
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_admin


class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint para gestionar usuarios
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    
    def get_permissions(self):
        """
        Define permisos según la acción
        """
        # Implementar lógica de permisos según necesidades
        return [permissions.IsAuthenticated()]
    
    def get_serializer_class(self):
        """
        Selecciona el serializer adecuado según la acción
        """
        if self.action == 'create':
            return UserCreateSerializer
        return UserSerializer
    
    # Agregar métodos personalizados para activar/desactivar usuarios, etc.