from django.core.management.base import BaseCommand
from django.utils import timezone
from schedule.services import ScheduleComplianceMonitor


class Command(BaseCommand):
    """
    Management command para verificar cumplimiento de turnos
    Uso: python manage.py check_schedule_compliance
    
    Para configurar en cron (cada hora):
    0 * * * * cd /path/to/project && python manage.py check_schedule_compliance
    """
    
    help = 'Verificar cumplimiento de turnos y generar notificaciones automáticas'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Ejecutar sin generar notificaciones (solo mostrar resultados)',
        )
        
        parser.add_argument(
            '--verbose',
            action='store_true',
            help='Mostrar información detallada',
        )
    
    def handle(self, *args, **options):
        """
        Ejecutar verificación de cumplimiento de turnos
        """
        dry_run = options['dry_run']
        verbose = options['verbose']
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Iniciando verificación de cumplimiento de turnos - {timezone.now()}'
            )
        )
        
        if dry_run:
            self.stdout.write(
                self.style.WARNING('MODO DRY-RUN: No se generarán notificaciones')
            )
        
        try:
            # Ejecutar verificación
            if dry_run:
                # En modo dry-run, simular la verificación sin generar notificaciones
                result = self._dry_run_check(verbose)
            else:
                result = ScheduleComplianceMonitor.check_overdue_schedules()
            
            # Mostrar resultados
            self.stdout.write(
                self.style.SUCCESS(
                    f'Verificación completada:'
                )
            )
            self.stdout.write(f'- Turnos verificados: {result["checked_schedules"]}')
            self.stdout.write(f'- Notificaciones generadas: {result["notifications_generated"]}')
            
            if verbose and result["notifications"]:
                self.stdout.write(
                    self.style.HTTP_INFO('\nDetalles de notificaciones generadas:')
                )
                for notification in result["notifications"]:
                    self.stdout.write(
                        f'  - Admin: {notification.user.username} | '
                        f'Título: {notification.title}'
                    )
            
            if result["checked_schedules"] == 0:
                self.stdout.write(
                    self.style.WARNING('No se encontraron turnos para verificar')
                )
            elif result["notifications_generated"] == 0:
                self.stdout.write(
                    self.style.SUCCESS('Todos los turnos están en cumplimiento ✓')
                )
            else:
                self.stdout.write(
                    self.style.ERROR(
                        f'Se detectaron {result["notifications_generated"]} incumplimientos'
                    )
                )
        
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error durante la verificación: {str(e)}')
            )
            raise
    
    def _dry_run_check(self, verbose):
        """
        Simular verificación sin generar notificaciones
        """
        from datetime import timedelta
        from schedule.models import Schedule
        from schedule.services import ScheduleValidationService
        
        current_time = timezone.now()
        grace_period = timedelta(minutes=5)
        
        # Buscar turnos que deberían haber comenzado hace más de 5 minutos
        overdue_schedules = Schedule.objects.filter(
            status=Schedule.ACTIVE,
            start_datetime__lt=current_time - grace_period,
            start_datetime__gte=current_time - timedelta(hours=24)
        ).select_related('user', 'room')
        
        non_compliant_count = 0
        
        for schedule in overdue_schedules:
            compliance_result = ScheduleValidationService.check_schedule_compliance(schedule.id)
            
            if compliance_result['status'] == 'non_compliant':
                non_compliant_count += 1
                
                if verbose:
                    self.stdout.write(
                        f'  INCUMPLIMIENTO: {schedule.user.username} en '
                        f'{schedule.room.code} ({schedule.start_datetime})'
                    )
        
        return {
            'checked_schedules': len(overdue_schedules),
            'notifications_generated': non_compliant_count,
            'notifications': []
        }