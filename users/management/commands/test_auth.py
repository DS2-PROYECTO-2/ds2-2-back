from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.conf import settings
from users.services import send_password_reset_email
from users.utils import generate_raw_token, build_password_reset_url
import logging

logger = logging.getLogger(__name__)

User = get_user_model()


class Command(BaseCommand):
    help = 'Probar funcionalidad de autenticación y email'

    def add_arguments(self, parser):
        parser.add_argument(
            '--test-email',
            action='store_true',
            help='Probar envío de email',
        )
        parser.add_argument(
            '--create-test-user',
            action='store_true',
            help='Crear usuario de prueba',
        )

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS('🔍 Iniciando pruebas de autenticación...')
        )
        
        # Probar configuración de email
        self.stdout.write('\n📧 Configuración de Email:')
        self.stdout.write(f'EMAIL_BACKEND: {settings.EMAIL_BACKEND}')
        self.stdout.write(f'EMAIL_HOST: {settings.EMAIL_HOST}')
        self.stdout.write(f'EMAIL_PORT: {settings.EMAIL_PORT}')
        self.stdout.write(f'EMAIL_HOST_USER: {settings.EMAIL_HOST_USER}')
        self.stdout.write(f'DEFAULT_FROM_EMAIL: {settings.DEFAULT_FROM_EMAIL}')
        
        if options['test_email']:
            self.test_email_sending()
        
        if options['create_test_user']:
            self.create_test_user()
        
        self.stdout.write(
            self.style.SUCCESS('✅ Pruebas completadas')
        )

    def test_email_sending(self):
        """Probar envío de email"""
        try:
            self.stdout.write('\n📧 Probando envío de email...')
            
            # Crear un usuario de prueba si no existe
            test_email = 'test@ejemplo.com'
            user, created = User.objects.get_or_create(
                username='test_user',
                defaults={
                    'email': test_email,
                    'first_name': 'Usuario',
                    'last_name': 'Prueba',
                    'identification': '12345678',
                    'role': 'monitor',
                    'is_verified': True
                }
            )
            
            if created:
                user.set_password('test123456')
                user.save()
                self.stdout.write(f'✅ Usuario de prueba creado: {user.username}')
            else:
                self.stdout.write(f'ℹ️ Usuario de prueba ya existe: {user.username}')
            
            # Probar envío de email
            raw_token = generate_raw_token()
            reset_url = build_password_reset_url(raw_token)
            
            self.stdout.write(f'🔗 URL de reset generada: {reset_url}')
            
            # Enviar email de prueba
            send_password_reset_email(user, reset_url)
            
            self.stdout.write('✅ Email enviado exitosamente')
            self.stdout.write('📧 Revisa la consola para ver el email (modo desarrollo)')
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Error enviando email: {str(e)}')
            )
            logger.error(f"Error en prueba de email: {e}")

    def create_test_user(self):
        """Crear usuario de prueba"""
        try:
            self.stdout.write('\n👤 Creando usuario de prueba...')
            
            # Crear usuario admin
            admin_user, created = User.objects.get_or_create(
                username='admin',
                defaults={
                    'email': 'admin@ejemplo.com',
                    'first_name': 'Admin',
                    'last_name': 'Sistema',
                    'identification': '00000000',
                    'role': 'admin',
                    'is_verified': True,
                    'is_staff': True,
                    'is_superuser': True
                }
            )
            
            if created:
                admin_user.set_password('admin123456')
                admin_user.save()
                self.stdout.write('✅ Usuario admin creado: admin / admin123456')
            else:
                self.stdout.write('ℹ️ Usuario admin ya existe')
            
            # Crear usuario monitor
            monitor_user, created = User.objects.get_or_create(
                username='monitor',
                defaults={
                    'email': 'monitor@ejemplo.com',
                    'first_name': 'Monitor',
                    'last_name': 'Prueba',
                    'identification': '11111111',
                    'role': 'monitor',
                    'is_verified': True
                }
            )
            
            if created:
                monitor_user.set_password('monitor123456')
                monitor_user.save()
                self.stdout.write('✅ Usuario monitor creado: monitor / monitor123456')
            else:
                self.stdout.write('ℹ️ Usuario monitor ya existe')
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Error creando usuarios: {str(e)}')
            )
            logger.error(f"Error creando usuarios: {e}")


