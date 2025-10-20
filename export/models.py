from django.db import models
from django.conf import settings
from django.utils import timezone


class ExportJob(models.Model):
    """
    Modelo para gestionar trabajos de exportación de datos de monitores
    """
    # Tipos de exportación
    MONITORS_DATA = 'monitors_data'
    ATTENDANCE_DATA = 'attendance_data'
    SCHEDULE_DATA = 'schedule_data'
    ROOM_ENTRIES_DATA = 'room_entries_data'
    
    TYPE_CHOICES = [
        (MONITORS_DATA, 'Datos de Monitores'),
        (ATTENDANCE_DATA, 'Datos de Asistencia'),
        (SCHEDULE_DATA, 'Datos de Turnos'),
        (ROOM_ENTRIES_DATA, 'Datos de Entradas a Salas'),
    ]
    
    # Formatos de exportación
    PDF = 'pdf'
    EXCEL = 'excel'
    
    FORMAT_CHOICES = [
        (PDF, 'PDF'),
        (EXCEL, 'Excel'),
    ]
    
    # Estados del trabajo
    PENDING = 'pending'
    PROCESSING = 'processing'
    COMPLETED = 'completed'
    FAILED = 'failed'
    
    STATUS_CHOICES = [
        (PENDING, 'Pendiente'),
        (PROCESSING, 'Procesando'),
        (COMPLETED, 'Completado'),
        (FAILED, 'Fallido'),
    ]
    
    title = models.CharField(
        max_length=200,
        verbose_name="Título",
        help_text='Título descriptivo de la exportación'
    )
    export_type = models.CharField(
        max_length=30,
        choices=TYPE_CHOICES,
        verbose_name="Tipo de exportación",
        help_text='Tipo de datos a exportar'
    )
    format = models.CharField(
        max_length=10,
        choices=FORMAT_CHOICES,
        verbose_name="Formato",
        help_text='Formato de archivo de exportación'
    )
    status = models.CharField(
        max_length=15,
        choices=STATUS_CHOICES,
        default=PENDING,
        verbose_name="Estado",
        help_text='Estado actual del trabajo de exportación'
    )
    
    # Filtros de datos
    start_date = models.DateField(
        null=True,
        blank=True,
        verbose_name="Fecha inicial",
        help_text='Fecha inicial del período a exportar'
    )
    end_date = models.DateField(
        null=True,
        blank=True,
        verbose_name="Fecha final",
        help_text='Fecha final del período a exportar'
    )
    monitor_ids = models.JSONField(
        null=True,
        blank=True,
        verbose_name="IDs de Monitores",
        help_text='Lista de IDs de monitores específicos a exportar'
    )
    
    # Archivo generado
    file = models.FileField(
        upload_to='exports/',
        null=True,
        blank=True,
        verbose_name="Archivo generado",
        help_text='Archivo de exportación generado'
    )
    
    # Usuario que solicita la exportación
    requested_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='export_jobs',
        verbose_name="Solicitado por",
        help_text='Usuario que solicitó la exportación'
    )
    
    # Campos de auditoría
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Completado en",
        help_text='Fecha y hora de finalización del trabajo'
    )
    
    # Información adicional
    error_message = models.TextField(
        blank=True,
        verbose_name="Mensaje de error",
        help_text='Mensaje de error si el trabajo falló'
    )
    file_size = models.BigIntegerField(
        null=True,
        blank=True,
        verbose_name="Tamaño del archivo",
        help_text='Tamaño del archivo generado en bytes'
    )
    
    class Meta:
        verbose_name = 'Trabajo de Exportación'
        verbose_name_plural = 'Trabajos de Exportación'
        ordering = ['-created_at']
        db_table = "export_exportjob"
    
    def __str__(self):
        return f"{self.title} - {self.get_status_display()}"
    
    def mark_as_processing(self):
        """Marca el trabajo como en procesamiento"""
        self.status = self.PROCESSING
        self.save(update_fields=['status'])
    
    def mark_as_completed(self, file_path=None, file_size=None):
        """Marca el trabajo como completado"""
        self.status = self.COMPLETED
        self.completed_at = timezone.now()
        if file_path:
            self.file = file_path
        if file_size:
            self.file_size = file_size
        self.save(update_fields=['status', 'completed_at', 'file', 'file_size'])
    
    def mark_as_failed(self, error_message):
        """Marca el trabajo como fallido"""
        self.status = self.FAILED
        self.error_message = error_message
        self.completed_at = timezone.now()
        self.save(update_fields=['status', 'error_message', 'completed_at'])
    
    @property
    def is_completed(self):
        """Verifica si el trabajo está completado"""
        return self.status == self.COMPLETED
    
    @property
    def is_failed(self):
        """Verifica si el trabajo falló"""
        return self.status == self.FAILED
    
    @property
    def is_processing(self):
        """Verifica si el trabajo está en procesamiento"""
        return self.status == self.PROCESSING

