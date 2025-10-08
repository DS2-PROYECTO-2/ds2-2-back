from django.core.management.base import BaseCommand
from django.utils import timezone
from rooms.services import auto_close_expired_sessions


class Command(BaseCommand):
    help = 'Cerrar automáticamente sesiones de monitores cuyos turnos han terminado'
    
    def add_arguments(self, parser):
        parser.add_argument('--verbose', action='store_true', help='Mostrar información detallada')
    
    def handle(self, *args, **options):
        verbose = options['verbose']
        
        self.stdout.write(f'Cerrando sesiones vencidas - {timezone.now()}')
        
        try:
            closed_sessions = auto_close_expired_sessions()
            
            if closed_sessions:
                self.stdout.write(self.style.SUCCESS(f'Se cerraron {len(closed_sessions)} sesiones'))
                if verbose:
                    for session in closed_sessions:
                        self.stdout.write(f'  - {session["user"]} en {session["room"]}')
            else:
                self.stdout.write(self.style.SUCCESS('No hay sesiones vencidas'))
        
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error: {str(e)}'))
            raise