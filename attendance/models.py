from django.db import models
from django.conf import settings


class Attendance(models.Model):
    """
    Modelo para subir y almacenar listados de asistencia
    """
    title = models.CharField(
        max_length=200, 
        verbose_name="Título",
        help_text='Título descriptivo del listado de asistencia'
    )
    date = models.DateField(
        verbose_name="Fecha",
        help_text='Fecha a la que corresponde el listado de asistencia'
    )
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='uploaded_attendances', 
        verbose_name="Subido por",
        help_text='Usuario que subió el listado de asistencia'
    )
    file = models.FileField(
        upload_to='attendances/', 
        verbose_name="Archivo",
        help_text='Archivo con el listado de asistencia (PDF recomendado)'
    )
    description = models.TextField(
        blank=True, 
        verbose_name="Descripción",
        help_text='Descripción adicional sobre el listado de asistencia'
    )
    reviewed = models.BooleanField(
        default=False, 
        verbose_name="Revisado",
        help_text='Indica si el listado ha sido revisado por un administrador'
    )
    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='reviewed_attendances', 
        verbose_name="Revisado por",
        help_text='Administrador que revisó el listado de asistencia'
    )
    
    # Campos de auditoría
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Listado de Asistencia'
        verbose_name_plural = 'Listados de Asistencia'
        ordering = ['-date']

    def __str__(self):
        return f"{self.title} - {self.date.strftime('%d/%m/%Y')}"


class Incapacity(models.Model):
    """
    Modelo para gestionar incapacidades de monitores
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='incapacities', 
        verbose_name="Monitor",
        help_text='Monitor que presenta la incapacidad'
    )
    start_date = models.DateField(
        verbose_name="Fecha de Inicio",
        help_text='Fecha de inicio de la incapacidad'
    )
    end_date = models.DateField(
        verbose_name="Fecha de Finalización",
        help_text='Fecha de finalización de la incapacidad'
    )
    document = models.FileField(
        upload_to='incapacities/', 
        verbose_name="Documento de Incapacidad",
        help_text='Documento que certifica la incapacidad (PDF recomendado)'
    )
    description = models.TextField(
        blank=True, 
        verbose_name="Descripción",
        help_text='Descripción o motivo de la incapacidad'
    )
    approved = models.BooleanField(
        default=False, 
        verbose_name="Aprobada",
        help_text='Indica si la incapacidad ha sido aprobada por un administrador'
    )
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='approved_incapacities', 
        verbose_name="Aprobada por",
        help_text='Administrador que aprobó la incapacidad'
    )
    
    # Campos de auditoría
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Incapacidad'
        verbose_name_plural = 'Incapacidades'
        ordering = ['-start_date']

    def __str__(self):
        return f"Incapacidad de {self.user.get_full_name()} - {self.start_date.strftime('%d/%m/%Y')}"
    
    @property
    def duration_days(self):
        """Calcula la duración de la incapacidad en días"""
        return (self.end_date - self.start_date).days + 1  # +1 porque el día final cuenta