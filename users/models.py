from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    """
    Modelo personalizado de usuario para administradores y monitores
    """
    # Roles de usuario
    ADMIN = 'admin'
    MONITOR = 'monitor'
    
    ROLE_CHOICES = [
        (ADMIN, 'Administrador'),
        (MONITOR, 'Monitor'),
    ]
    
    role = models.CharField(
        max_length=10,
        choices=ROLE_CHOICES,
        default=MONITOR,
        help_text='Rol del usuario en el sistema'
    )
    identification = models.CharField(
        max_length=20, 
        unique=True, 
        verbose_name="Número de Identificación",
        help_text='Número de identificación del usuario'
    )
    phone = models.CharField(
        max_length=15, 
        blank=True, 
        verbose_name="Teléfono",
        help_text='Número de teléfono de contacto'
    )
    is_verified = models.BooleanField(
        default=False,
        help_text='Indica si el usuario ha sido verificado por un administrador'
    )
    
    # Campos de auditoría
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'
        ordering = ['username']
    
    def __str__(self):
        return f"{self.get_full_name()} ({self.get_role_display()})"
    
    @property
    def is_admin(self):
        """Verifica si el usuario es administrador"""
        return self.role == self.ADMIN
    
    @property
    def is_monitor(self):
        """Verifica si el usuario es monitor"""
        return self.role == self.MONITOR
    
    def save(self, *args, **kwargs):
        """Sobrescribe el método save para verificar automáticamente a los administradores"""
        if not self.pk and self.role == self.ADMIN:
            self.is_verified = True
        super().save(*args, **kwargs)