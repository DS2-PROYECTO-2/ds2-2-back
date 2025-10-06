from django.test import TestCase
from django.utils import timezone
from django.core.exceptions import ValidationError
from datetime import timedelta
from unittest.mock import patch

from users.models import User
from rooms.models import Room, RoomEntry
from schedule.models import Schedule
from schedule.services import ScheduleValidationService, ScheduleComplianceMonitor
from notifications.models import Notification


class ScheduleValidationServiceTest(TestCase):
    """
    Tests para el servicio de validaciones de turnos - Tarea 2
    """
    
    def setUp(self):
        """Configurar datos de prueba"""
        # Crear usuarios
        self.admin = User.objects.create_user(
            username='admin_test',
            email='admin@test.com',
            password='test123',
            identification='12345678',
            role='admin',
            is_verified=True
        )
        
        self.monitor1 = User.objects.create_user(
            username='monitor1',
            email='monitor1@test.com',
            password='test123',
            identification='87654321',
            first_name='Monitor',
            last_name='Uno',
            role='monitor',
            is_verified=True
        )
        
        self.monitor2 = User.objects.create_user(
            username='monitor2',
            email='monitor2@test.com',
            password='test123',
            identification='11223344',
            first_name='Monitor',
            last_name='Dos',
            role='monitor',
            is_verified=True
        )
        
        # Crear salas
        self.room1 = Room.objects.create(
            name='Sala de Estudio 1',
            code='SE001',
            capacity=20,
            is_active=True
        )
        
        self.room2 = Room.objects.create(
            name='Sala de Estudio 2',
            code='SE002',
            capacity=15,
            is_active=True
        )
        
        # Fechas para pruebas
        self.now = timezone.now()
        self.start_time = self.now.replace(minute=0, second=0, microsecond=0)
        self.end_time = self.start_time + timedelta(hours=2)
        
    def test_validate_schedule_conflicts_no_conflict(self):
        """Test: No debe haber conflicto cuando no hay turnos superpuestos"""
        # No debería lanzar excepción
        result = ScheduleValidationService.validate_schedule_conflicts(
            user=self.monitor1,
            room=self.room1,
            start_datetime=self.start_time,
            end_datetime=self.end_time
        )
        self.assertTrue(result)
        
    def test_validate_schedule_conflicts_with_conflict(self):
        """Test: Debe detectar conflicto cuando hay turnos superpuestos del mismo usuario"""
        # Crear turno existente
        Schedule.objects.create(
            user=self.monitor1,
            room=self.room1,
            start_datetime=self.start_time,
            end_datetime=self.end_time,
            created_by=self.admin,
            status=Schedule.ACTIVE
        )
        
        # Intentar crear turno superpuesto en OTRA SALA (para que sea conflicto de usuario)
        conflicting_start = self.start_time + timedelta(minutes=30)
        conflicting_end = self.end_time + timedelta(minutes=30)
        
        with self.assertRaises(ValidationError) as context:
            ScheduleValidationService.validate_schedule_conflicts(
                user=self.monitor1,
                room=self.room2,  # Diferente sala para probar conflicto de usuario
                start_datetime=conflicting_start,
                end_datetime=conflicting_end
            )
        
        error_message = str(context.exception)
        self.assertIn('se superponen', error_message)
    
    def test_validate_schedule_conflicts_with_room_conflict(self):
        """Test: Debe detectar conflicto cuando la sala está ocupada por otro monitor"""
        # Crear turno existente con monitor1
        Schedule.objects.create(
            user=self.monitor1,
            room=self.room1,
            start_datetime=self.start_time,
            end_datetime=self.end_time,
            created_by=self.admin,
            status=Schedule.ACTIVE
        )
        
        # Intentar crear turno superpuesto con monitor2 en la MISMA SALA
        conflicting_start = self.start_time + timedelta(minutes=30)
        conflicting_end = self.end_time + timedelta(minutes=30)
        
        with self.assertRaises(ValidationError) as context:
            ScheduleValidationService.validate_schedule_conflicts(
                user=self.monitor2,  # Diferente monitor
                room=self.room1,     # Misma sala
                start_datetime=conflicting_start,
                end_datetime=conflicting_end
            )
        
        error_message = str(context.exception)
        self.assertIn('ya está ocupada por', error_message)
        self.assertIn('No se permiten dos monitores', error_message)
        
    def test_validate_schedule_conflicts_exclude_schedule(self):
        """Test: Debe excluir el turno actual al editar"""
        # Crear turno existente
        existing_schedule = Schedule.objects.create(
            user=self.monitor1,
            room=self.room1,
            start_datetime=self.start_time,
            end_datetime=self.end_time,
            created_by=self.admin,
            status=Schedule.ACTIVE
        )
        
        # No debería detectar conflicto al editar el mismo turno
        result = ScheduleValidationService.validate_schedule_conflicts(
            user=self.monitor1,
            room=self.room1,
            start_datetime=self.start_time + timedelta(minutes=15),
            end_datetime=self.end_time + timedelta(minutes=15),
            exclude_schedule_id=existing_schedule.id
        )
        self.assertTrue(result)
        
    def test_validate_room_access_permission_with_valid_schedule(self):
        """Test: Debe permitir acceso cuando hay turno activo"""
        # Crear turno activo
        Schedule.objects.create(
            user=self.monitor1,
            room=self.room1,
            start_datetime=self.start_time - timedelta(minutes=30),
            end_datetime=self.end_time + timedelta(minutes=30),
            created_by=self.admin,
            status=Schedule.ACTIVE
        )
        
        # Debería permitir acceso
        result = ScheduleValidationService.validate_room_access_permission(
            user=self.monitor1,
            room=self.room1,
            entry_time=self.now
        )
        
        self.assertTrue(result['access_granted'])
        self.assertEqual(result['message'], 'Acceso autorizado por turno activo')
        
    def test_validate_room_access_permission_without_schedule(self):
        """Test: Debe denegar acceso cuando no hay turno activo"""
        with self.assertRaises(ValidationError) as context:
            ScheduleValidationService.validate_room_access_permission(
                user=self.monitor1,
                room=self.room1,
                entry_time=self.now
            )
        
        error_message = str(context.exception)
        self.assertIn('sin turno activo', error_message)
        
    def test_validate_room_access_permission_with_upcoming_schedule(self):
        """Test: Debe dar información sobre turnos próximos"""
        # Crear turno que empieza en 10 minutos
        upcoming_start = self.now + timedelta(minutes=10)
        Schedule.objects.create(
            user=self.monitor1,
            room=self.room1,
            start_datetime=upcoming_start,
            end_datetime=upcoming_start + timedelta(hours=2),
            created_by=self.admin,
            status=Schedule.ACTIVE
        )
        
        with self.assertRaises(ValidationError) as context:
            ScheduleValidationService.validate_room_access_permission(
                user=self.monitor1,
                room=self.room1,
                entry_time=self.now
            )
        
        error_message = str(context.exception)
        self.assertIn('sin turno activo', error_message)
        
    def test_check_schedule_compliance_pending(self):
        """Test: Turno pendiente (aún no ha comenzado)"""
        future_schedule = Schedule.objects.create(
            user=self.monitor1,
            room=self.room1,
            start_datetime=self.now + timedelta(hours=1),
            end_datetime=self.now + timedelta(hours=3),
            created_by=self.admin,
            status=Schedule.ACTIVE
        )
        
        result = ScheduleValidationService.check_schedule_compliance(future_schedule)
        self.assertEqual(result['compliance_status'], 'pending')
        
    def test_check_schedule_compliance_compliant(self):
        """Test: Turno cumplido (monitor se presentó a tiempo)"""
        past_schedule = Schedule.objects.create(
            user=self.monitor1,
            room=self.room1,
            start_datetime=self.now - timedelta(hours=2),
            end_datetime=self.now - timedelta(hours=1),
            created_by=self.admin,
            status=Schedule.ACTIVE
        )
        
        # Crear entrada dentro del período de gracia
        RoomEntry.objects.create(
            user=self.monitor1,
            room=self.room1,
            entry_time=past_schedule.start_datetime + timedelta(minutes=5)
        )
        
        result = ScheduleValidationService.check_schedule_compliance(past_schedule)
        self.assertEqual(result['compliance_status'], 'compliant')
        self.assertTrue(result['within_grace_period'])
        
    def test_check_schedule_compliance_non_compliant(self):
        """Test: Turno no cumplido (monitor no se presentó)"""
        past_schedule = Schedule.objects.create(
            user=self.monitor1,
            room=self.room1,
            start_datetime=self.now - timedelta(hours=2),
            end_datetime=self.now - timedelta(hours=1),
            created_by=self.admin,
            status=Schedule.ACTIVE
        )
        
        # No crear entrada - monitor no se presentó
        result = ScheduleValidationService.check_schedule_compliance(past_schedule)
        self.assertEqual(result['compliance_status'], 'non_compliant')
        self.assertTrue(result['should_notify_admin'])
        
    def test_check_schedule_compliance_late_compliance(self):
        """Test: Turno con retraso (monitor llegó tarde)"""
        past_schedule = Schedule.objects.create(
            user=self.monitor1,
            room=self.room1,
            start_datetime=self.now - timedelta(hours=2),
            end_datetime=self.now - timedelta(hours=1),
            created_by=self.admin,
            status=Schedule.ACTIVE
        )
        
        # Crear entrada con 30 minutos de retraso
        RoomEntry.objects.create(
            user=self.monitor1,
            room=self.room1,
            entry_time=past_schedule.start_datetime + timedelta(minutes=30)
        )
        
        result = ScheduleValidationService.check_schedule_compliance(past_schedule)
        self.assertEqual(result['compliance_status'], 'late_compliance')
        self.assertFalse(result['within_grace_period'])
        self.assertTrue(result['should_notify_admin'])
        
    def test_notify_admin_schedule_non_compliance(self):
        """Test: Notificación a administradores por incumplimiento"""
        past_schedule = Schedule.objects.create(
            user=self.monitor1,
            room=self.room1,
            start_datetime=self.now - timedelta(hours=2),
            end_datetime=self.now - timedelta(hours=1),
            created_by=self.admin,
            status=Schedule.ACTIVE
        )
        
        compliance_info = {
            'compliance_status': 'non_compliant',
            'should_notify_admin': True,
            'minutes_late': 30
        }
        
        result = ScheduleValidationService.notify_admin_schedule_non_compliance(
            past_schedule, compliance_info
        )
        
        self.assertTrue(result['notification_sent'])
        self.assertEqual(result['notifications_created'], 1)
        
        # Verificar que se creó la notificación
        notification = Notification.objects.filter(
            user=self.admin,
            notification_type='schedule_non_compliance'
        ).first()
        
        self.assertIsNotNone(notification)
        self.assertIn('INCUMPLIMIENTO DE TURNO', notification.message)
        
    def test_create_schedule_with_validations_success(self):
        """Test: Crear turno exitosamente con validaciones"""
        result = ScheduleValidationService.create_schedule_with_validations(
            user=self.monitor1,
            room=self.room1,
            start_datetime=self.start_time,
            end_datetime=self.end_time,
            created_by=self.admin,
            notes='Turno de prueba'
        )
        
        self.assertTrue(result['success'])
        self.assertIsNotNone(result['schedule'])
        self.assertEqual(result['schedule'].user, self.monitor1)
        
    def test_create_schedule_with_validations_conflict(self):
        """Test: Fallar al crear turno con conflicto"""
        # Crear turno existente
        Schedule.objects.create(
            user=self.monitor1,
            room=self.room1,
            start_datetime=self.start_time,
            end_datetime=self.end_time,
            created_by=self.admin,
            status=Schedule.ACTIVE
        )
        
        # Intentar crear turno conflictivo
        result = ScheduleValidationService.create_schedule_with_validations(
            user=self.monitor1,
            room=self.room2,  # Diferente sala pero mismo monitor y horario
            start_datetime=self.start_time + timedelta(minutes=30),
            end_datetime=self.end_time + timedelta(minutes=30),
            created_by=self.admin
        )
        
        self.assertFalse(result['success'])
        self.assertEqual(result['error'], 'Validación fallida')
        
    def test_get_monitor_schedule_status(self):
        """Test: Obtener estado de cumplimiento de turnos del monitor"""
        today = self.now.date()
        
        # Crear turnos para hoy
        schedule1 = Schedule.objects.create(
            user=self.monitor1,
            room=self.room1,
            start_datetime=self.now - timedelta(hours=3),
            end_datetime=self.now - timedelta(hours=1),
            created_by=self.admin,
            status=Schedule.ACTIVE
        )
        
        schedule2 = Schedule.objects.create(
            user=self.monitor1,
            room=self.room2,
            start_datetime=self.now + timedelta(hours=1),
            end_datetime=self.now + timedelta(hours=3),
            created_by=self.admin,
            status=Schedule.ACTIVE
        )
        
        # Crear entrada para el primer turno
        RoomEntry.objects.create(
            user=self.monitor1,
            room=self.room1,
            entry_time=schedule1.start_datetime + timedelta(minutes=5)
        )
        
        result = ScheduleValidationService.get_monitor_schedule_status(
            user=self.monitor1,
            date=today
        )
        
        self.assertEqual(result['total_schedules'], 2)
        self.assertEqual(result['compliant'], 1)
        self.assertEqual(result['pending'], 1)
        self.assertEqual(len(result['schedules']), 2)


class ScheduleComplianceMonitorTest(TestCase):
    """
    Tests para el monitor de cumplimiento automático
    """
    
    def setUp(self):
        """Configurar datos de prueba"""
        self.admin = User.objects.create_user(
            username='admin_test',
            email='admin@test.com',
            password='test123',
            identification='12345678',
            role='admin',
            is_verified=True
        )
        
        self.monitor = User.objects.create_user(
            username='monitor_test',
            email='monitor@test.com',
            password='test123',
            identification='87654321',
            role='monitor',
            is_verified=True
        )
        
        self.room = Room.objects.create(
            name='Sala Test',
            code='ST001',
            capacity=10,
            is_active=True
        )
        
        self.now = timezone.now()
        
    def test_check_overdue_schedules_empty(self):
        """Test: No hay turnos vencidos"""
        result = ScheduleComplianceMonitor.check_overdue_schedules()
        
        self.assertEqual(result['checked_schedules'], 0)
        self.assertEqual(result['notifications_sent'], 0)
        self.assertEqual(result['compliant_schedules'], 0)
        self.assertEqual(result['non_compliant_schedules'], 0)
        
    @patch('schedule.services.ScheduleValidationService.notify_admin_schedule_non_compliance')
    def test_check_overdue_schedules_with_non_compliant(self, mock_notify):
        """Test: Verificar turnos vencidos no conformes"""
        mock_notify.return_value = {
            'notification_sent': True,
            'notifications_created': 1
        }
        
        # Crear turno vencido (comenzó hace más de 20 minutos)
        overdue_schedule = Schedule.objects.create(
            user=self.monitor,
            room=self.room,
            start_datetime=self.now - timedelta(minutes=30),
            end_datetime=self.now + timedelta(minutes=90),
            created_by=self.admin,
            status=Schedule.ACTIVE
        )
        
        result = ScheduleComplianceMonitor.check_overdue_schedules()
        
        self.assertEqual(result['checked_schedules'], 1)
        self.assertEqual(result['non_compliant_schedules'], 1)
        self.assertEqual(result['notifications_sent'], 1)
        
        # Verificar que se llamó al método de notificación
        mock_notify.assert_called_once()