from django.db import models
from django.conf import settings
from rooms.models import Room


class Schedule(models.Model):
    """
    Modelo para gestionar turnos y calendarios de monitores
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='schedules',
        verbose_name="Monitor",
        help_text='Monitor asignado al turno'
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
        help_text='Administrador que creó el turno'
    )
    
    # Campos de auditoría
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Turno'
        verbose_name_plural = 'Turnos'
        ordering = ['start_datetime']

    def __str__(self):
        return f"{self.user} - {self.room} - {self.start_datetime.strftime('%d/%m/%Y %H:%M')}"
    
    @property
    def duration_hours(self):
        """Calcula la duración del turno en horas"""
        duration = self.end_datetime - self.start_datetime
        hours = duration.total_seconds() / 3600
        return round(hours, 2)