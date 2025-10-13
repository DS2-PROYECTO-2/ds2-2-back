from django.db import models
from django.conf import settings
from django.utils import timezone


class Room(models.Model):
    """
    Modelo para representar las salas donde trabajan los monitores
    """
    name = models.CharField(
        max_length=100,
        help_text='Nombre descriptivo de la sala'
    )
    code = models.CharField(
        max_length=10, 
        unique=True,
        help_text='Código único de identificación de la sala'
    )
    capacity = models.IntegerField(
        help_text='Capacidad máxima de personas en la sala'
    )
    description = models.TextField(
        blank=True,
        help_text='Descripción adicional de la sala'
    )
    is_active = models.BooleanField(
        default=True,
        help_text='Indica si la sala está activa para uso'
    )
    
    # Campos de auditoría
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Sala'
        verbose_name_plural = 'Salas'
        ordering = ['code']

    def __str__(self):
        return f"{self.code} - {self.name}"


class RoomEntry(models.Model):
    """
    Modelo para registrar entradas y salidas de monitores a las salas
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='room_entries',
        help_text='Monitor que ingresa a la sala'
    )
    room = models.ForeignKey(
        Room,
        on_delete=models.CASCADE,
        related_name='entries',
        help_text='Sala a la que ingresa el monitor'
    )
    entry_time = models.DateTimeField(
        default=timezone.now,
        help_text='Fecha y hora de entrada a la sala'
    )
    exit_time = models.DateTimeField(
        null=True,
        blank=True,
        help_text='Fecha y hora de salida de la sala'
    )
    notes = models.TextField(
        blank=True,
        help_text='Notas o comentarios sobre la entrada/salida'
    )
    active = models.BooleanField(
        default=True,
        help_text='Indica si la entrada está activa'
    )
    
    # Campos de auditoría
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Registro de Entrada'
        verbose_name_plural = 'Registros de Entrada'
        ordering = ['-entry_time']

    def __str__(self):
        return f"{self.user} - {self.room} - {self.entry_time.strftime('%d/%m/%Y %H:%M')}"
    
    @property
    def is_active(self):
        """Indica si el monitor aún está en la sala"""
        return self.exit_time is None
    
    @property
    def duration_hours(self):
        """Calcula la duración de la permanencia en la sala en horas"""
        if not self.exit_time:
            return None
        
        duration = self.exit_time - self.entry_time
        # Duración en horas (con dos decimales)
        hours = duration.total_seconds() / 3600
        return round(hours, 2)
    
    @property
    def duration_minutes(self):
        """Calcula la duración de la permanencia en la sala en minutos"""
        if not self.exit_time:
            return None
        
        duration = self.exit_time - self.entry_time
        return int(duration.total_seconds() / 60)
    
    def get_duration_formatted(self):
        """Retorna la duración en formato legible (ej: '2h 30m')"""
        if not self.duration_minutes:
            return "En curso"
        
        hours = self.duration_minutes // 60
        minutes = self.duration_minutes % 60
        
        if hours > 0:
            return f"{hours}h {minutes}m"
        return f"{minutes}m"

    @classmethod
    def create_with_reused_id(cls, **kwargs):
        """
        Crea una nueva entrada reutilizando IDs disponibles
        Utiliza el sistema de reutilización de IDs para optimizar la base de datos
        """
        from .id_reuse import RoomEntryIDManager
        return RoomEntryIDManager.create_with_reused_id(**kwargs)
    
    @classmethod
    def get_id_statistics(cls):
        """
        Obtiene estadísticas sobre el uso de IDs en este modelo
        """
        from .id_reuse import RoomEntryIDManager
        return RoomEntryIDManager.get_room_entry_stats()
