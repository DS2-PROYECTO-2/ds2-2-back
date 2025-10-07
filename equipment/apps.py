from django.apps import AppConfig


class EquipmentConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'equipment'
    
    def ready(self):
        """
        Importar señales cuando la aplicación esté lista
        """
        import equipment.signals

