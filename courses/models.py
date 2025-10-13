from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import timedelta

from rooms.models import Room
from schedule.models import Schedule


class Course(models.Model):
    """
    Modelo para gestionar cursos asignados a salas en calendario
    """
    # Estados del curso
    SCHEDULED = 'scheduled'
    IN_PROGRESS = 'in_progress'
    COMPLETED = 'completed'
    CANCELLED = 'cancelled'
    
    STATUS_CHOICES = [
        (SCHEDULED, 'Programado'),
        (IN_PROGRESS, 'En Progreso'),
        (COMPLETED, 'Completado'),
        (CANCELLED, 'Cancelado'),
    ]
    
    name = models.CharField(
        max_length=200,
        verbose_name="Nombre del Curso",
        help_text='Nombre descriptivo del curso'
    )
    description = models.TextField(
        blank=True,
        verbose_name="Descripción",
        help_text='Descripción detallada del curso'
    )
    room = models.ForeignKey(
        Room,
        on_delete=models.CASCADE,
        related_name='courses',
        verbose_name="Sala",
        help_text='Sala donde se impartirá el curso'
    )
    schedule = models.ForeignKey(
        Schedule,
        on_delete=models.CASCADE,
        related_name='course_assignments',
        verbose_name="Turno Asociado",
        help_text='Turno del monitor que debe cubrir este curso'
    )
    start_datetime = models.DateTimeField(
        verbose_name="Fecha y Hora de Inicio",
        help_text='Inicio del curso'
    )
    end_datetime = models.DateTimeField(
        verbose_name="Fecha y Hora de Fin",
        help_text='Fin del curso'
    )
    status = models.CharField(
        max_length=15,
        choices=STATUS_CHOICES,
        default=SCHEDULED,
        verbose_name="Estado",
        help_text='Estado actual del curso'
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_courses',
        verbose_name="Creado por",
        help_text='Administrador que creó el curso',
        limit_choices_to={'role': 'admin'}
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Curso"
        verbose_name_plural = "Cursos"
        ordering = ['start_datetime']
        indexes = [
            models.Index(fields=['start_datetime', 'end_datetime']),
            models.Index(fields=['room', 'start_datetime']),
            models.Index(fields=['schedule', 'start_datetime']),
        ]
    
    def __str__(self):
        return f"{self.name} - {self.room.name} - {self.start_datetime.strftime('%d/%m/%Y %H:%M')}"
    
    def clean(self):
        """Validaciones del modelo"""
        if self.start_datetime and self.end_datetime:
            if self.end_datetime <= self.start_datetime:
                raise ValidationError('La fecha de fin debe ser posterior a la fecha de inicio.')
            
            # Validar duración máxima de 8 horas
            duration = self.end_datetime - self.start_datetime
            if duration > timedelta(hours=8):
                raise ValidationError('Un curso no puede durar más de 8 horas.')
        
        # Validar que el monitor del schedule sea verificado
        if self.schedule and self.schedule.user:
            monitor = self.schedule.user
            if monitor.role != 'monitor' or not monitor.is_verified:
                raise ValidationError('Solo se pueden asignar cursos a monitores verificados.')
    
    @property
    def monitor(self):
        """Obtener el monitor a través del schedule"""
        return self.schedule.user if self.schedule else None
    
    @property
    def duration_hours(self):
        """Duración del curso en horas"""
        if self.start_datetime and self.end_datetime:
            delta = self.end_datetime - self.start_datetime
            return round(delta.total_seconds() / 3600, 2)
        return 0
    
    @property
    def is_current(self):
        """Verificar si el curso está en curso actualmente"""
        now = timezone.now()
        return self.start_datetime <= now <= self.end_datetime and self.status in [self.SCHEDULED, self.IN_PROGRESS]
    
    @property
    def is_upcoming(self):
        """Verificar si el curso es próximo (en las próximas 24 horas)"""
        now = timezone.now()
        return self.start_datetime > now and self.start_datetime <= now + timedelta(hours=24)
    
    @property
    def is_active(self):
        """Verificar si el curso está activo (programado o en progreso)"""
        return self.status in [self.SCHEDULED, self.IN_PROGRESS]
    
    def save(self, *args, **kwargs):
        """Override save para ejecutar validaciones"""
        self.full_clean()
        super().save(*args, **kwargs)


class CourseHistory(models.Model):
    """
    Modelo para registrar historial de cambios en cursos
    """
    ACTION_CREATE = 'create'
    ACTION_UPDATE = 'update'
    ACTION_DELETE = 'delete'
    
    ACTION_CHOICES = [
        (ACTION_CREATE, 'Creado'),
        (ACTION_UPDATE, 'Actualizado'),
        (ACTION_DELETE, 'Eliminado'),
    ]
    
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='history',
        verbose_name="Curso"
    )
    action = models.CharField(
        max_length=10,
        choices=ACTION_CHOICES,
        verbose_name="Acción"
    )
    changes = models.JSONField(
        default=dict,
        verbose_name="Cambios",
        help_text='Detalles de los cambios realizados'
    )
    changed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name="Modificado por"
    )
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Historial de Curso"
        verbose_name_plural = "Historiales de Cursos"
        ordering = ['-timestamp']
    
    def __str__(self):
        return f"{self.course.name} - {self.get_action_display()} - {self.timestamp.strftime('%d/%m/%Y %H:%M')}"
