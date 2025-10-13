from rest_framework import serializers
from django.utils import timezone
from .utils import generate_raw_token, hash_token, build_password_reset_url
from datetime import timedelta
from django.contrib.auth import get_user_model
from .models import PasswordReset
from .services import send_password_reset_email

User = get_user_model()

class UserRegistrationSerializer(serializers.ModelSerializer):
    """
    Serializador para el registro de nuevos usuarios
    """
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = [
            'username', 'email', 'password', 'password_confirm',
            'first_name', 'last_name', 'identification', 'phone', 'role'
        ]
        extra_kwargs = {
            'email': {'required': True},
            'identification': {'required': True},
            'first_name': {'required': True},
            'last_name': {'required': True},
        }

    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError({
                'password_confirm': ['Las contraseñas no coinciden']
            })
        
        # Validar que la identificación no exista
        if User.objects.filter(identification=attrs['identification']).exists():
            raise serializers.ValidationError({
                'identification': ['Ya existe un usuario con esta identificación']
            })
        
        # Validar que el username no exista
        if User.objects.filter(username=attrs['username']).exists():
            raise serializers.ValidationError({
                'username': ['Ya existe un usuario con este nombre de usuario']
            })
        
        # Validar que el email no exista
        if User.objects.filter(email=attrs['email']).exists():
            raise serializers.ValidationError({
                'email': ['Ya existe un usuario con este email']
            })
        
        return attrs

    def create(self, validated_data):
        validated_data.pop('password_confirm')
        password = validated_data.pop('password')
        
        try:
            user = User.objects.create_user(
                password=password,
                **validated_data
            )
            return user
        except Exception as e:
            # Si hay un IntegrityError, verificar qué campo está duplicado
            if 'IntegrityError' in str(type(e)):
                # Verificar cada campo único
                if User.objects.filter(identification=validated_data.get('identification')).exists():
                    raise serializers.ValidationError({
                        'identification': ['Ya existe un usuario con esta identificación']
                    })
                elif User.objects.filter(username=validated_data.get('username')).exists():
                    raise serializers.ValidationError({
                        'username': ['Ya existe un usuario con este nombre de usuario']
                    })
                elif User.objects.filter(email=validated_data.get('email')).exists():
                    raise serializers.ValidationError({
                        'email': ['Ya existe un usuario con este email']
                    })
                else:
                    raise serializers.ValidationError({
                        'non_field_errors': ['Error de integridad de datos. Verifica que todos los campos sean únicos.']
                    })
            else:
                raise e


class UserLoginSerializer(serializers.Serializer):
    """
    Serializador para el login de usuarios
    """
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        username = attrs.get('username')
        password = attrs.get('password')

        if username and password:
            # Verificar si el usuario existe
            try:
                user = User.objects.get(username=username)
            except User.DoesNotExist:
                raise serializers.ValidationError({
                    'username': ['Usuario no encontrado']
                })
            
            # Verificar si la cuenta está activa
            if not user.is_active:
                raise serializers.ValidationError({
                    'username': ['Cuenta desactivada']
                })
            
            # Verificar contraseña
            if not user.check_password(password):
                raise serializers.ValidationError({
                    'password': ['Contraseña incorrecta']
                })
            
            # Verificar verificación para monitores
            if not user.is_verified and user.role == 'monitor':
                raise serializers.ValidationError({
                    'username': ['Tu cuenta aún no ha sido verificada por un administrador']
                })
            
            attrs['user'] = user
            return attrs
        else:
            raise serializers.ValidationError('Debe incluir username y password')

class UserProfileSerializer(serializers.ModelSerializer):
    """
    Serializador para el perfil del usuario - Solo campos que el usuario puede ver/editar
    """
    class Meta:
        model = User
        fields = [
            'first_name', 'last_name', 'username', 'email', 'phone', 'identification'
        ]
        
    def validate_identification(self, value):
        """
        Validar que la identificación no esté en uso por otro usuario
        """
        if self.instance and self.instance.identification == value:
            return value  # No cambió, es válido
            
        if User.objects.filter(identification=value).exists():
            raise serializers.ValidationError("Ya existe un usuario con esta identificación")
        return value
        
    def validate_username(self, value):
        """
        Validar que el username no esté en uso por otro usuario
        """
        if self.instance and self.instance.username == value:
            return value  # No cambió, es válido
            
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("Ya existe un usuario con este nombre de usuario")
        return value
        
    def validate_email(self, value):
        """
        Validar que el email no esté en uso por otro usuario
        """
        if self.instance and self.instance.email == value:
            return value  # No cambió, es válido
            
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Ya existe un usuario con este email")
        return value


class UserProfileCompleteSerializer(serializers.ModelSerializer):
    """
    Serializador completo del usuario para uso interno (dashboard, admin, etc.)
    """
    role_display = serializers.CharField(source='get_role_display', read_only=True)
    verified_by_name = serializers.CharField(source='verified_by.get_full_name', read_only=True)

    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name',
            'identification', 'phone', 'role', 'role_display',
            'is_verified', 'verified_by_name', 'verification_date',
            'date_joined', 'created_at'
        ]
        read_only_fields = [
            'id', 'is_verified', 'verified_by_name', 'verification_date',
            'date_joined', 'created_at'
        ]


class AdminUserListSerializer(serializers.ModelSerializer):
    """
    Serializador para la lista de usuarios (vista de administrador)
    """
    role_display = serializers.CharField(source='get_role_display', read_only=True)
    full_name = serializers.CharField(source='get_full_name', read_only=True)

    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'full_name', 'identification',
            'phone', 'role', 'role_display', 'is_verified', 'is_active',
            'date_joined', 'created_at'
        ]


class AdminUserVerificationSerializer(serializers.ModelSerializer):
    """
    Serializador para que los administradores verifiquen usuarios
    """
    class Meta:
        model = User
        fields = ['is_verified']

    def update(self, instance, validated_data):
        if validated_data.get('is_verified'):
            instance.is_verified = True
            instance.verified_by = self.context['request'].user
            instance.verification_date = timezone.now()
        else:
            instance.is_verified = False
            instance.verified_by = None
            instance.verification_date = None
        
        instance.save()
        return instance


class ChangePasswordSerializer(serializers.Serializer):
    """
    Serializador para cambio de contraseña
    """
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True, min_length=8)
    new_password_confirm = serializers.CharField(required=True)

    def validate(self, attrs):
        if attrs['new_password'] != attrs['new_password_confirm']:
            raise serializers.ValidationError({
                'new_password_confirm': ['Las nuevas contraseñas no coinciden']
            })
        
        user = self.context['request'].user
        if not user.check_password(attrs['old_password']):
            raise serializers.ValidationError({
                'old_password': ['La contraseña actual es incorrecta']
            })
        
        # Validar que la nueva contraseña sea diferente a la actual
        if user.check_password(attrs['new_password']):
            raise serializers.ValidationError({
                'new_password': ['La nueva contraseña debe ser diferente a la actual']
            })
        
        return attrs

    def save(self):
        user = self.context['request'].user
        user.set_password(self.validated_data['new_password'])
        user.save()
        return user

class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def create(self, validated_data):
        email = validated_data['email']
        try:
            user = User.objects.get(email=email, is_active=True)
        except User.DoesNotExist:
            # Ahora explicitamos que no existe
            return {'exists': False}

        raw_token = generate_raw_token()
        token_hash = hash_token(raw_token)

        PasswordReset.objects.create(
            user=user,
            token_hash=token_hash,
            expires_at=timezone.now() + timedelta(hours=2),
        )

        reset_url = build_password_reset_url(raw_token)
        send_password_reset_email(user, reset_url)
        
        # Devolver flag exists y, en modo consola, también el enlace
        from django.conf import settings
        result = {'exists': True}
        if settings.EMAIL_BACKEND == 'django.core.mail.backends.console.EmailBackend':
            result['reset_url'] = reset_url
        return result

class PasswordResetConfirmSerializer(serializers.Serializer):
    token = serializers.CharField()
    new_password = serializers.CharField(min_length=8)
    new_password_confirm = serializers.CharField()

    def validate(self, attrs):
        if attrs['new_password'] != attrs['new_password_confirm']:
            raise serializers.ValidationError({
                'new_password_confirm': ['Las contraseñas no coinciden']
            })
        return attrs

    def create(self, validated_data):
        token_hash = hash_token(validated_data['token'])
        try:
            pr = PasswordReset.objects.get(token_hash=token_hash)
        except PasswordReset.DoesNotExist:
            raise serializers.ValidationError({'token': ['Token inválido']})

        if not pr.is_valid():
            # Limpieza “just-in-time” de expirados
            if pr.is_expired():
                pr.delete()
                raise serializers.ValidationError({'token': ['Token expirado']})
            raise serializers.ValidationError({'token': ['Token ya fue usado']})

        user = pr.user
        if user.check_password(validated_data['new_password']):
            raise serializers.ValidationError({'new_password': ['La nueva contraseña debe ser diferente a la actual']})

        user.set_password(validated_data['new_password'])
        user.save()

        pr.mark_as_used()
        return {}