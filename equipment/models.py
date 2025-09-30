from django.db import models
from django.conf import settings
from rooms.models import Room


class Equipment(models.Model):
    """
    Modelo para representar equipos en las salas
    """
    # Estados posibles de los equipos
    OPERATIONAL = 'operational'
    MAINTENANCE = 'maintenance'
    OUT_OF_SERVICE = 'out_of_service'
    
    STATUS_CHOICES = [
        (OPERATIONAL, 'Operativo'),
        (MAINTENANCE, 'En mantenimiento'),
        (OUT_OF_SERVICE, 'Fuera de servicio'),
    ]
    
    serial_number = models.CharField(
        max_length=50, 
        unique=True, 
        verbose_name="Número de Serie",
        help_text='Número de serie único del equipo'
    )
    name = models.CharField(
        max_length=100, 
        verbose_name="Nombre/Modelo",
        help_text='Nombre o modelo del equipo'
    )
    description = models.TextField(
        blank=True, 
        verbose_name="Descripción",
        help_text='Descripción detallada del equipo'
    )
    room = models.ForeignKey(
        Room, 
        on_delete=models.CASCADE, 
        related_name='equipment', 
        verbose_name="Sala",
        help_text='Sala donde se encuentra el equipo'
    )
    status = models.CharField(
        max_length=20, 
        choices=STATUS_CHOICES, 
        default=OPERATIONAL, 
        verbose_name="Estado",
        help_text='Estado actual del equipo'
    )
    acquisition_date = models.DateField(
        verbose_name="Fecha de Adquisición",
        help_text='Fecha en que se adquirió el equipo'
    )
    
    # Campos de auditoría
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Equipo'
        verbose_name_plural = 'Equipos'
        ordering = ['room', 'name']

    def __str__(self):
        return f"{self.name} ({self.serial_number})"


class EquipmentReport(models.Model):
    """
    Modelo para reportar problemas con equipos
    """
    equipment = models.ForeignKey(
        Equipment, 
        on_delete=models.CASCADE, 
        related_name='reports', 
        verbose_name="Equipo",
        help_text='Equipo que presenta el problema'
    )
    reported_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='equipment_reports', 
        verbose_name="Reportado por",
        help_text='Usuario que reporta el problema'
    )
    issue_description = models.TextField(
        verbose_name="Descripción del Problema",
        help_text='Descripción detallada del problema reportado'
    )
    reported_date = models.DateTimeField(
        auto_now_add=True, 
        verbose_name="Fecha del Reporte",
        help_text='Fecha y hora en que se reportó el problema'
    )
    resolved = models.BooleanField(
        default=False, 
        verbose_name="Resuelto",
        help_text='Indica si el problema ha sido resuelto'
    )
    resolved_date = models.DateTimeField(
        null=True, 
        blank=True, 
        verbose_name="Fecha de Resolución",
        help_text='Fecha y hora en que se resolvió el problema'
    )
    resolution_notes = models.TextField(
        blank=True, 
        verbose_name="Notas de Resolución",
        help_text='Detalles sobre cómo se resolvió el problema'
    )
    
    # Campos de auditoría
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Reporte de Equipo'
        verbose_name_plural = 'Reportes de Equipos'
        ordering = ['-reported_date']

    def __str__(self):
        return f"Reporte #{self.id} - {self.equipment.name}"