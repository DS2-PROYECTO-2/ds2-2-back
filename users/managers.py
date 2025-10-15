from django.contrib.auth.base_user import BaseUserManager


class CustomUserManager(BaseUserManager):
    """
    Custom user model manager where identification is the unique identifier
    for authentication instead of usernames.
    """
    def create_user(self, identification, username, email, password, **extra_fields):
        """
        Create and save a User with the given identification and password.
        OPTIMIZADO: Validaciones más eficientes
        """
        if not identification:
            raise ValueError('The identification must be set')
        if not email:
            raise ValueError('The email must be set')
        
        email = self.normalize_email(email)
        
        # OPTIMIZACIÓN: Configuración por defecto más eficiente
        extra_fields.setdefault('is_verified', False)
        extra_fields.setdefault('is_active', True)
        
        # OPTIMIZACIÓN: Crear usuario con configuración optimizada
        user = self.model(
            identification=identification,
            username=username,
            email=email,
            **extra_fields
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, identification, username, email, password, **extra_fields):
        """
        Create and save a SuperUser with the given identification and password.
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_verified', True)
        extra_fields.setdefault('role', 'admin')

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(identification, username, email, password, **extra_fields)