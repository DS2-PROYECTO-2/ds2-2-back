from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from schedule.tasks import daily_compliance_summary


class Command(BaseCommand):
    help = 'Enviar resumen diario de cumplimiento de turnos a administradores'

    def add_arguments(self, parser):
        parser.add_argument(
            '--date',
            type=str,
            help='Fecha específica para el resumen (YYYY-MM-DD). Por defecto: hoy',
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Ejecutar sin enviar notificaciones reales',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        date_str = options.get('date')
        
        if date_str:
            try:
                from datetime import datetime
                target_date = datetime.strptime(date_str, '%Y-%m-%d').date()
            except ValueError:
                self.stdout.write(
                    self.style.ERROR('Formato de fecha inválido. Use YYYY-MM-DD')
                )
                return
        else:
            target_date = timezone.now().date()
        
        self.stdout.write(
            self.style.SUCCESS(f'Generando resumen de cumplimiento para {target_date}')
        )
        
        if dry_run:
            self.stdout.write(self.style.WARNING('Modo DRY RUN - No se enviarán notificaciones'))
        
        try:
            # Ejecutar resumen diario
            daily_compliance_summary()
            
            self.stdout.write(
                self.style.SUCCESS(f'Resumen diario enviado exitosamente para {target_date}')
            )
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error al generar resumen diario: {str(e)}')
            )