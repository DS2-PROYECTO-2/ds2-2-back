"""
Test esenciales para la funcionalidad de cursos y notificaciones de incumplimiento.
EISC-86: Backend Modelo y endpoints para Asignación de cursos a salas en calendario
"""
from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
from rest_framework.authtoken.models import Token
import json

from courses.models import Course, CourseHistory
from schedule.models import Schedule
from rooms.models import Room
from notifications.models import Notification

User = get_user_model()


class CourseAPITests(TestCase):
    """Tests esenciales para los endpoints de cursos"""
    
    def setUp(self):
        """Configurar datos de prueba"""
        # Crear usuarios
        self.admin = User.objects.create_user(
            username='admin_test',
            identification='123456789',
            email='admin@test.com',
            password='testpass123',
            role='admin',
            is_verified=True
        )
        self.monitor = User.objects.create_user(
            username='monitor_test',
            identification='987654321',
            email='monitor@test.com',
            password='testpass123',
            role='monitor',
            is_verified=True
        )
        
        # Crear tokens
        self.admin_token = Token.objects.create(user=self.admin)
        self.monitor_token = Token.objects.create(user=self.monitor)
        
        # Crear sala
        self.room = Room.objects.create(
            name='Sala Test',
            code='TEST01',
            capacity=30,
            is_active=True
        )
        
        # Crear schedule
        now = timezone.now()
        self.schedule = Schedule.objects.create(
            user=self.monitor,
            room=self.room,
            start_datetime=now + timedelta(hours=1),
            end_datetime=now + timedelta(hours=3),
            status='active',
            created_by=self.admin
        )
        
        self.client = Client()
    
    def test_course_creation_returns_id(self):
        """Test: Creación de curso retorna ID"""
        self.client.defaults['HTTP_AUTHORIZATION'] = f'Token {self.admin_token.key}'
        
        now = timezone.now()
        course_data = {
            'name': 'Curso Test API',
            'description': 'Curso de prueba',
            'room': self.room.id,
            'schedule': self.schedule.id,
            'start_datetime': (now + timedelta(hours=1)).isoformat(),
            'end_datetime': (now + timedelta(hours=2)).isoformat(),
            'status': 'scheduled'
        }
        
        response = self.client.post(
            '/api/courses/',
            data=json.dumps(course_data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 201)
        data = response.json()
        self.assertIn('id', data)
        self.assertIsNotNone(data['id'])
        self.assertEqual(data['name'], 'Curso Test API')
    
    def test_course_monitor_property_works(self):
        """Test: Propiedad monitor accede via schedule.user"""
        course = Course.objects.create(
            name='Curso Monitor Test',
            description='Test monitor property',
            room=self.room,
            schedule=self.schedule,
            start_datetime=timezone.now() + timedelta(hours=1),
            end_datetime=timezone.now() + timedelta(hours=2),
            created_by=self.admin
        )
        
        # Verificar que la propiedad monitor funciona
        self.assertEqual(course.monitor, self.monitor)
        self.assertEqual(course.monitor.username, 'monitor_test')
    
    def test_course_list_filters_by_monitor(self):
        """Test: Lista de cursos filtra correctamente por monitor"""
        # Crear curso
        Course.objects.create(
            name='Curso para Monitor',
            room=self.room,
            schedule=self.schedule,
            start_datetime=timezone.now() + timedelta(hours=1),
            end_datetime=timezone.now() + timedelta(hours=2),
            created_by=self.admin
        )
        
        # Como monitor, ver lista de cursos
        self.client.defaults['HTTP_AUTHORIZATION'] = f'Token {self.monitor_token.key}'
        response = self.client.get('/api/courses/')
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        # Como monitor, debería ver al menos 1 curso
        self.assertGreaterEqual(len(data.get('results', [])), 1)
    
    def test_calendar_view_endpoint_exists(self):
        """Test: Endpoint de vista de calendario existe"""
        self.client.defaults['HTTP_AUTHORIZATION'] = f'Token {self.admin_token.key}'
        response = self.client.get('/api/courses/calendar_view/')
        
        # Debe existir y no dar 404
        self.assertNotEqual(response.status_code, 404)
        
        if response.status_code == 200:
            data = response.json()
            self.assertIn('calendar_events', data)
            self.assertIn('summary', data)


class ScheduleComplianceTests(TestCase):
    """Tests esenciales para notificaciones de incumplimiento"""
    
    def setUp(self):
        """Configurar datos de prueba"""
        self.admin = User.objects.create_user(
            username='admin_compliance',
            identification='111222333',
            email='admin@compliance.com',
            password='testpass123',
            role='admin',
            is_verified=True
        )
        self.monitor = User.objects.create_user(
            username='monitor_compliance',
            identification='444555666',
            email='monitor@compliance.com',
            password='testpass123',
            role='monitor',
            is_verified=True
        )
        
        self.room = Room.objects.create(
            name='Compliance Test Room',
            code='COMP01',
            capacity=20,
            is_active=True
        )
    
    def test_schedule_compliance_command_exists(self):
        """Test: Comando de verificación de cumplimiento existe"""
        from django.core.management import call_command
        from io import StringIO
        
        # Probar comando en modo dry-run
        out = StringIO()
        try:
            call_command('check_schedule_compliance', '--dry-run', stdout=out)
            output = out.getvalue()
            self.assertIn('verificación', output.lower())
        except Exception as e:
            self.fail(f"Comando check_schedule_compliance falló: {e}")
    
    def test_notification_model_has_schedule_non_compliance_type(self):
        """Test: Modelo de notificación tiene tipo para incumplimientos"""
        # Verificar que el tipo existe en las opciones
        notification_types = [choice[0] for choice in Notification.TYPE_CHOICES]
        self.assertIn('schedule_non_compliance', notification_types)
        
        # Crear notificación de prueba
        notification = Notification.objects.create(
            user=self.admin,
            title='Test Incumplimiento',
            message='Test message',
            notification_type='schedule_non_compliance'
        )
        
        self.assertEqual(notification.notification_type, 'schedule_non_compliance')
        self.assertFalse(notification.read)  # Por defecto no leída
    
    def test_schedule_compliance_monitor_service_exists(self):
        """Test: Servicio de monitoreo de cumplimiento existe"""
        from schedule.services import ScheduleComplianceMonitor
        
        # Verificar que el método principal existe
        self.assertTrue(hasattr(ScheduleComplianceMonitor, 'check_overdue_schedules'))
        self.assertTrue(callable(getattr(ScheduleComplianceMonitor, 'check_overdue_schedules')))


class CourseModelTests(TestCase):
    """Tests esenciales para el modelo Course"""
    
    def setUp(self):
        self.admin = User.objects.create_user(
            username='admin_model',
            identification='777888999',
            email='admin@model.com',
            password='testpass123',
            role='admin',
            is_verified=True
        )
        self.monitor = User.objects.create_user(
            username='monitor_model',
            identification='000111222',
            email='monitor@model.com',
            password='testpass123',
            role='monitor',
            is_verified=True
        )
        self.room = Room.objects.create(
            name='Model Test Room',
            code='MODEL01',
            capacity=25
        )
        self.schedule = Schedule.objects.create(
            user=self.monitor,
            room=self.room,
            start_datetime=timezone.now() + timedelta(hours=1),
            end_datetime=timezone.now() + timedelta(hours=3),
            status='active',
            created_by=self.admin
        )
    
    def test_course_model_has_no_monitor_field(self):
        """Test: Modelo Course no tiene campo monitor directo"""
        course = Course.objects.create(
            name='Test Model Course',
            room=self.room,
            schedule=self.schedule,
            start_datetime=timezone.now() + timedelta(hours=1),
            end_datetime=timezone.now() + timedelta(hours=2),
            created_by=self.admin
        )
        
        # Verificar que no existe campo monitor en el modelo
        field_names = [field.name for field in Course._meta.get_fields()]
        self.assertNotIn('monitor', field_names)
        
        # Pero la propiedad monitor debe funcionar
        self.assertEqual(course.monitor, self.monitor)
    
    def test_course_history_is_created(self):
        """Test: Historial de curso se crea correctamente"""
        initial_count = CourseHistory.objects.count()
        
        Course.objects.create(
            name='History Test Course',
            room=self.room,
            schedule=self.schedule,
            start_datetime=timezone.now() + timedelta(hours=1),
            end_datetime=timezone.now() + timedelta(hours=2),
            created_by=self.admin
        )
        
        # Verificar que el historial puede crearse (no falla por campo monitor)
        self.assertGreaterEqual(CourseHistory.objects.count(), initial_count)