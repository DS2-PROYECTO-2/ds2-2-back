from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from notifications.models import Notification


class Command(BaseCommand):
    help = 'Limpiar notificaciones antiguas del sistema'

    def add_arguments(self, parser):
        parser.add_argument(
            '--days',
            type=int,
            default=30,
            help='Días de antigüedad para considerar notificaciones como antiguas (por defecto: 30)',
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Mostrar qué se eliminaría sin hacer cambios reales',
        )
        parser.add_argument(
            '--type',
            type=str,
            help='Tipo específico de notificación a limpiar',
        )

    def handle(self, *args, **options):
        days = options['days']
        dry_run = options['dry_run']
        notification_type = options.get('type')
        
        cutoff_date = timezone.now() - timedelta(days=days)
        
        self.stdout.write(
            self.style.SUCCESS(f'Limpiando notificaciones anteriores a {cutoff_date.date()}')
        )
        
        if dry_run:
            self.stdout.write(self.style.WARNING('Modo DRY RUN - No se eliminarán registros'))
        
        try:
            # Construir query
            query = Notification.objects.filter(created_at__lt=cutoff_date)
            
            if notification_type:
                query = query.filter(notification_type=notification_type)
                self.stdout.write(f'Filtrando por tipo: {notification_type}')
            
            # Contar notificaciones a eliminar
            count = query.count()
            
            if count == 0:
                self.stdout.write(
                    self.style.SUCCESS('No hay notificaciones antiguas para eliminar')
                )
                return
            
            # Mostrar estadísticas por tipo
            types_stats = {}
            for notification in query.values('notification_type').distinct():
                notification_type_name = notification['notification_type']
                type_count = query.filter(notification_type=notification_type_name).count()
                types_stats[notification_type_name] = type_count
            
            self.stdout.write(f'Notificaciones a eliminar por tipo:')
            for type_name, type_count in types_stats.items():
                self.stdout.write(f'  • {type_name}: {type_count}')
            
            if not dry_run:
                # Eliminar notificaciones
                deleted_count, details = query.delete()
                
                self.stdout.write(
                    self.style.SUCCESS(f'Eliminadas {deleted_count} notificaciones antiguas')
                )
                
                # Mostrar detalles de eliminación
                if details:
                    for model, count in details.items():
                        if count > 0:
                            self.stdout.write(f'  • {model}: {count} registros')
            else:
                self.stdout.write(
                    self.style.WARNING(f'Se eliminarían {count} notificaciones (DRY RUN)')
                )
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error al limpiar notificaciones: {str(e)}')
            )