from django.db import models
from django.conf import settings


class Notification(models.Model):
    """
    Modelo para gestionar notificaciones en tiempo real
    """
    # Tipos de notificaciones
    ROOM_ENTRY = 'room_entry'
    ROOM_EXIT = 'room_exit'
    INCAPACITY = 'incapacity'
    EQUIPMENT_REPORT = 'equipment_report'
    ATTENDANCE = 'attendance'
    ADMIN_VERIFICATION = 'admin_verification'
    EXCESSIVE_HOURS = 'excessive_hours'
    CONVERSATION_MESSAGE = 'conversation_message'
    
    TYPE_CHOICES = [
        (ROOM_ENTRY, 'Entrada a sala'),
        (ROOM_EXIT, 'Salida de sala'),
        (INCAPACITY, 'Incapacidad registrada'),
        (EQUIPMENT_REPORT, 'Reporte de equipo'),
        (ATTENDANCE, 'Listado de asistencia'),
        (ADMIN_VERIFICATION, 'Verificación de usuario'),
        (EXCESSIVE_HOURS, 'Exceso de horas continuas'),
        (CONVERSATION_MESSAGE, 'Nuevo mensaje en conversación'),
    ]
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notifications_received',
        help_text='Usuario que recibe la notificación'
    )
    notification_type = models.CharField(
        max_length=30,
        choices=TYPE_CHOICES,
        verbose_name="Tipo",
        help_text='Tipo de notificación'
    )
    title = models.CharField(
        max_length=200,
        verbose_name="Título",
        help_text='Título breve de la notificación'
    )
    message = models.TextField(
        verbose_name="Mensaje",
        help_text='Mensaje detallado de la notificación'
    )
    related_object_id = models.IntegerField(
        null=True,
        blank=True,
        verbose_name="ID de objeto relacionado",
        help_text='ID del objeto relacionado con la notificación (ej. ID de una entrada, incapacidad, etc.)'
    )
    read = models.BooleanField(
        default=False,
        verbose_name="Leída",
        help_text='Indica si la notificación ha sido leída'
    )
    read_timestamp = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Fecha de lectura",
        help_text='Fecha y hora en que se leyó la notificación'
    )
    
    # Campos de auditoría
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Notificación'
        verbose_name_plural = 'Notificaciones'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.get_notification_type_display()} - {self.title} ({self.user})"