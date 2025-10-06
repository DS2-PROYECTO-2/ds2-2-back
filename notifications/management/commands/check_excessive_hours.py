from django.core.management.base import BaseCommand
from django.utils import timezone
from notifications.services import NotificationService, ExcessiveHoursChecker
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Verificar y notificar monitores que exceden las 8 horas continuas'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Ejecutar sin enviar notificaciones (solo mostrar qué se haría)',
        )
        parser.add_argument(
            '--verbose',
            action='store_true',
            help='Mostrar información detallada',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        verbose = options['verbose']
        
        self.stdout.write(
            self.style.SUCCESS('🔍 Iniciando verificación de exceso de horas...')
        )
        
        try:
            # Obtener monitores con exceso de horas
            excessive_monitors = ExcessiveHoursChecker.get_monitors_with_excessive_hours()
            
            if verbose:
                self.stdout.write(f'📊 Monitores con exceso de horas encontrados: {len(excessive_monitors)}')
            
            if not excessive_monitors:
                self.stdout.write(
                    self.style.SUCCESS('✅ No se encontraron monitores con exceso de horas')
                )
                return
            
            # Mostrar información de monitores con exceso
            for monitor in excessive_monitors:
                status_icon = "🚨" if monitor['is_critical'] else "⚠️"
                self.stdout.write(
                    f"{status_icon} {monitor['user'].get_full_name()} ({monitor['user'].username}) - "
                    f"Sala: {monitor['room'].name} - "
                    f"Duración: {monitor['total_hours']:.1f}h - "
                    f"Exceso: {monitor['excess_hours']:.1f}h"
                )
            
            if dry_run:
                self.stdout.write(
                    self.style.WARNING('🔍 MODO DRY-RUN: No se enviaron notificaciones')
                )
                return
            
            # Verificar y enviar notificaciones
            notifications_sent = NotificationService.check_and_notify_excessive_hours()
            
            if notifications_sent > 0:
                self.stdout.write(
                    self.style.SUCCESS(
                        f'✅ Verificación completada. {notifications_sent} notificaciones enviadas.'
                    )
                )
            else:
                self.stdout.write(
                    self.style.WARNING('⚠️ No se enviaron nuevas notificaciones')
                )
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Error durante la verificación: {str(e)}')
            )
            logger.error(f"Error en verificación de exceso de horas: {e}")
            raise
