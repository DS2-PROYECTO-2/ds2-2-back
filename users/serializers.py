from rest_framework import serializers
from .models import User


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer básico para el modelo User
    """
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 
                  'role', 'document_id', 'phone_number', 'is_active']
        read_only_fields = ['id', 'is_active']


class UserCreateSerializer(serializers.ModelSerializer):
    """
    Serializer para la creación de usuarios
    """
    password = serializers.CharField(write_only=True, required=True)
    password_confirm = serializers.CharField(write_only=True, required=True)
    
    class Meta:
        model = User
        fields = ['username', 'password', 'password_confirm', 'email', 'first_name', 
                  'last_name', 'role', 'document_id', 'phone_number']
