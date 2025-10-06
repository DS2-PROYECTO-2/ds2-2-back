from django.db import models
from django.conf import settings


class Report(models.Model):
    """
    Modelo para gestionar la generación y almacenamiento de reportes
    """
    # Tipos de reportes
    HOURS_SUMMARY = 'hours_summary'
    ATTENDANCE = 'attendance'
    EQUIPMENT_STATUS = 'equipment_status'
    INCAPACITY = 'incapacity'
    
    TYPE_CHOICES = [
        (HOURS_SUMMARY, 'Resumen de horas'),
        (ATTENDANCE, 'Asistencia'),
        (EQUIPMENT_STATUS, 'Estado de equipos'),
        (INCAPACITY, 'Incapacidades'),
    ]
    
    # Formatos de exportación
    PDF = 'pdf'
    EXCEL = 'excel'
    
    FORMAT_CHOICES = [
        (PDF, 'PDF'),
        (EXCEL, 'Excel'),
    ]
    
    title = models.CharField(
        max_length=200,
        verbose_name="Título",
        help_text='Título descriptivo del reporte'
    )
    report_type = models.CharField(
        max_length=30,
        choices=TYPE_CHOICES,
        verbose_name="Tipo de reporte",
        help_text='Tipo de información incluida en el reporte'
    )
    start_date = models.DateField(
        verbose_name="Fecha inicial",
        help_text='Fecha inicial del período del reporte'
    )
    end_date = models.DateField(
        verbose_name="Fecha final",
        help_text='Fecha final del período del reporte'
    )
    format = models.CharField(
        max_length=10,
        choices=FORMAT_CHOICES,
        default=PDF,
        verbose_name="Formato",
        help_text='Formato de exportación del reporte'
    )
    file = models.FileField(
        upload_to='reports/',
        null=True,
        blank=True,
        verbose_name="Archivo generado",
        help_text='Archivo del reporte generado'
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='reports',
        verbose_name="Generado por",
        help_text='Usuario que generó el reporte'
    )
    user_filter = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='filtered_reports',
        verbose_name="Filtrado por usuario",
        help_text='Filtrar reporte para un usuario específico (opcional)'
    )
    
    # Campos de auditoría
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Reporte'
        verbose_name_plural = 'Reportes'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} - {self.get_report_type_display()} ({self.start_date} - {self.end_date})"