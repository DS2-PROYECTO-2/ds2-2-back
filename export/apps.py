from django.apps import AppConfig


class ExportConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'export'
    verbose_name = 'Sistema de Exportación'
    
    def ready(self):
        """Configuración cuando la app está lista"""
        pass

