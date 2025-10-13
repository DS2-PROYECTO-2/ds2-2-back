from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils import timezone
from rooms.models import Room


class Schedule(models.Model):
    """
    Modelo para gestionar turnos y calendarios de monitores
    """
    # Estados del turno
    ACTIVE = 'active'
    COMPLETED = 'completed'
    CANCELLED = 'cancelled'
    
    STATUS_CHOICES = [
        (ACTIVE, 'Activo'),
        (COMPLETED, 'Completado'),
        (CANCELLED, 'Cancelado'),
    ]
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='schedules',
        verbose_name="Monitor",
        help_text='Monitor asignado al turno',
        limit_choices_to={'role': 'monitor', 'is_verified': True}
    )
    room = models.ForeignKey(
        Room,
        on_delete=models.CASCADE,
        related_name='schedules',
        verbose_name="Sala",
        help_text='Sala asignada para el turno'
    )
    start_datetime = models.DateTimeField(
        verbose_name="Inicio del turno",
        help_text='Fecha y hora de inicio del turno'
    )
    end_datetime = models.DateTimeField(
        verbose_name="Fin del turno",
        help_text='Fecha y hora de finalización del turno'
    )
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default=ACTIVE,
        verbose_name="Estado",
        help_text='Estado actual del turno'
    )
    recurring = models.BooleanField(
        default=False,
        verbose_name="Recurrente",
        help_text='Indica si el turno se repite semanalmente'
    )
    notes = models.TextField(
        blank=True,
        verbose_name="Notas",
        help_text='Notas adicionales sobre el turno'
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_schedules',
        verbose_name="Creado por",
        help_text='Administrador que creó el turno',
        limit_choices_to={'role': 'admin'}
    )
    
    # Campos de auditoría
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Turno'
        verbose_name_plural = 'Turnos'
        ordering = ['start_datetime']
        # Evitar turnos superpuestos para el mismo monitor
        constraints = [
            models.CheckConstraint(
                check=models.Q(end_datetime__gt=models.F('start_datetime')),
                name='schedule_end_after_start'
            )
        ]

    def __str__(self):
        return f"{self.user} - {self.room} - {self.start_datetime.strftime('%d/%m/%Y %H:%M')}"
    
    def clean(self):
        """Validaciones personalizadas del modelo"""
        super().clean()
        
        # Validar que la fecha de fin sea posterior a la de inicio
        if self.start_datetime and self.end_datetime:
            if self.end_datetime <= self.start_datetime:
                raise ValidationError({
                    'end_datetime': 'La fecha de fin debe ser posterior a la fecha de inicio.'
                })
            
            # Validar que el turno no exceda 12 horas
            duration = self.end_datetime - self.start_datetime
            if duration.total_seconds() > 12 * 3600:  # 12 horas
                raise ValidationError({
                    'end_datetime': 'Un turno no puede exceder 12 horas de duración.'
                })
        
        # Validar que el monitor tenga rol de monitor
        if self.user and hasattr(self.user, 'role') and self.user.role != 'monitor':
            raise ValidationError({
                'user': 'Solo se pueden asignar turnos a usuarios con rol de monitor.'
            })
    
    def save(self, *args, **kwargs):
        """Override save para ejecutar validaciones"""
        self.full_clean()
        super().save(*args, **kwargs)
    
    @property
    def duration_hours(self):
        """Calcula la duración del turno en horas"""
        if self.start_datetime and self.end_datetime:
            duration = self.end_datetime - self.start_datetime
            hours = duration.total_seconds() / 3600
            return round(hours, 2)
        return 0
    
    @property
    def is_active(self):
        """Verifica si el turno está activo"""
        return self.status == self.ACTIVE
    
    @property
    def is_current(self):
        """Verifica si el turno está en horario actual"""
        now = timezone.now()
        return self.start_datetime <= now <= self.end_datetime and self.is_active
    
    @property
    def is_upcoming(self):
        """Verifica si el turno está próximo (dentro de las próximas 24 horas)"""
        now = timezone.now()
        return self.start_datetime > now and (self.start_datetime - now).total_seconds() <= 24 * 3600
    
    def get_room_entries(self):
        """Obtiene las entradas de sala durante este turno"""
        from rooms.models import RoomEntry
        return RoomEntry.objects.filter(
            user=self.user,
            room=self.room,
            entry_time__gte=self.start_datetime,
            entry_time__lte=self.end_datetime
        )
    
    def has_compliance(self):
        """Verifica si el monitor cumplió con el turno (tiene entrada en la sala)"""
        return self.get_room_entries().exists()