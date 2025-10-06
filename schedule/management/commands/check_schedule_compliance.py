from django.core.management.base import BaseCommand
from django.utils import timezone
from schedule.services import ScheduleComplianceMonitor
from schedule.tasks import check_and_notify_overdue_schedules, monitor_active_schedules
import logging

# Configurar logging para el comando
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Verificar cumplimiento de turnos y enviar notificaciones automáticas a administradores'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Ejecutar sin enviar notificaciones reales',
        )
        parser.add_argument(
            '--verbose',
            action='store_true',
            help='Mostrar información detallada de la ejecución',
        )
        parser.add_argument(
            '--monitor-active',
            action='store_true',
            help='También monitorear turnos activos en riesgo',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        verbose = options.get('verbose', False)
        monitor_active = options.get('monitor_active', False)
        
        start_time = timezone.now()
        
        self.stdout.write(
            self.style.SUCCESS(f'🔍 Iniciando verificación de cumplimiento de turnos - {start_time}')
        )
        
        if dry_run:
            self.stdout.write(self.style.WARNING('⚠️  Modo DRY RUN - No se enviarán notificaciones'))
        
        try:
            # 1. Verificar turnos vencidos usando la nueva función
            self.stdout.write('\n📋 Verificando turnos vencidos...')
            results = check_and_notify_overdue_schedules()
            
            self.stdout.write(f"Turnos verificados: {results['checked_schedules']}")
            self.stdout.write(f"Turnos conformes: {results['compliant_schedules']}")
            self.stdout.write(f"Turnos no conformes: {results['non_compliant_schedules']}")
            self.stdout.write(f"Notificaciones enviadas: {results['notifications_sent']}")
            
            if results['details']:
                self.stdout.write("\nDetalles:")
                for detail in results['details']:
                    status_emoji = "✅" if detail['compliance_status'] == 'compliant' else "❌"
                    notification_info = " (Notificado)" if detail['notification_sent'] else ""
                    
                    self.stdout.write(
                        f"  {status_emoji} Turno {detail['schedule_id']}: "
                        f"{detail['monitor']} en {detail['room']} - "
                        f"{detail['compliance_status']}{notification_info}"
                    )
            
            if results['non_compliant_schedules'] > 0:
                self.stdout.write(
                    self.style.WARNING(
                        f'Se encontraron {results["non_compliant_schedules"]} turnos no conformes'
                    )
                )
            else:
                self.stdout.write(
                    self.style.SUCCESS('Todos los turnos están conformes')
                )
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error al verificar cumplimiento: {str(e)}')
            )
            raise e
        
        self.stdout.write(
            self.style.SUCCESS(f'Verificación completada - {timezone.now()}')
        )