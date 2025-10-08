from django.test import TestCase
from django.utils import timezone
from django.core.exceptions import ValidationError
from users.models import User
from datetime import datetime, timedelta
from unittest.mock import patch

from schedule.models import Schedule
from schedule.services import ScheduleValidationService, ScheduleComplianceMonitor
from rooms.models import Room, RoomEntry
from notifications.models import Notification


class ScheduleValidationServiceTest(TestCase):
    """
    Tests para Tarea 2: Backend: Lógica y validaciones para Integración con calendarios
    """
    
    def setUp(self):
        """
        Configurar datos de prueba
        """
        # Crear usuarios de prueba
        self.admin_user = User.objects.create_user(
            username='admin',
            identification='12345678',
            email='admin@test.com',
            password='testpass123',
            role='admin',
            is_verified=True
        )
        
        self.monitor1 = User.objects.create_user(
            username='monitor1',
            identification='87654321',
            email='monitor1@test.com', 
            password='testpass123',
            role='monitor',
            is_verified=True
        )
        
        self.monitor2 = User.objects.create_user(
            username='monitor2',
            identification='11223344',
            email='monitor2@test.com',
            password='testpass123',
            role='monitor',
            is_verified=True
        )
        
        # Crear salas de prueba
        self.room1 = Room.objects.create(
            name='Sala de Computadores 1',
            code='SC1',
            capacity=30,
            description='Sala de computadores principal',
            is_active=True
        )
        
        self.room2 = Room.objects.create(
            name='Sala de Computadores 2', 
            code='SC2',
            capacity=25,
            description='Sala de computadores secundaria',
            is_active=True
        )
        
        # Configurar fechas para las pruebas
        self.now = timezone.now()
        self.start_time = self.now + timedelta(hours=1)
        self.end_time = self.now + timedelta(hours=3)
    
    def test_validate_schedule_conflicts_no_conflicts(self):
        """
        Test: No debe haber errores cuando no existen conflictos
        """
        # No debería lanzar excepción
        result = ScheduleValidationService.validate_schedule_conflicts(
            user=self.monitor1,
            room=self.room1,
            start_datetime=self.start_time,
            end_datetime=self.end_time
        )
        
        self.assertTrue(result)
    
    def test_validate_schedule_conflicts_user_conflict(self):
        """
        Test: Debe detectar conflicto cuando un monitor tiene otro turno al mismo tiempo
        """
        # Crear turno existente
        Schedule.objects.create(
            user=self.monitor1,
            room=self.room2,  # Diferente sala
            start_datetime=self.start_time,
            end_datetime=self.end_time,
            status=Schedule.ACTIVE,
            created_by=self.admin_user
        )
        
        # Intentar crear turno conflictivo (mismo monitor, misma hora, diferente sala)
        with self.assertRaises(ValidationError) as context:
            ScheduleValidationService.validate_schedule_conflicts(
                user=self.monitor1,
                room=self.room1,  # Diferente sala
                start_datetime=self.start_time,
                end_datetime=self.end_time
            )
        
        self.assertIn('user_conflict', str(context.exception))
        self.assertIn('monitor1', str(context.exception))
    
    def test_validate_schedule_conflicts_room_conflict(self):
        """
        Test: Debe detectar conflicto cuando una sala ya tiene monitor asignado (PETICIÓN 2)
        """
        # Crear turno existente
        Schedule.objects.create(
            user=self.monitor1,
            room=self.room1,  # Misma sala
            start_datetime=self.start_time,
            end_datetime=self.end_time,
            status=Schedule.ACTIVE,
            created_by=self.admin_user
        )
        
        # Intentar crear turno conflictivo (diferente monitor, misma sala, misma hora)
        with self.assertRaises(ValidationError) as context:
            ScheduleValidationService.validate_schedule_conflicts(
                user=self.monitor2,  # Diferente monitor
                room=self.room1,     # Misma sala
                start_datetime=self.start_time,
                end_datetime=self.end_time
            )
        
        self.assertIn('room_conflict', str(context.exception))
        self.assertIn('No se permiten 2 monitores por sala', str(context.exception))
    
    def test_validate_schedule_conflicts_exclude_current(self):
        """
        Test: Al editar un turno, debe excluirlo de la validación de conflictos
        """
        # Crear turno existente
        existing_schedule = Schedule.objects.create(
            user=self.monitor1,
            room=self.room1,
            start_datetime=self.start_time,
            end_datetime=self.end_time,
            status=Schedule.ACTIVE,
            created_by=self.admin_user
        )
        
        # Editar el mismo turno - no debería dar conflicto
        result = ScheduleValidationService.validate_schedule_conflicts(
            user=self.monitor1,
            room=self.room1,
            start_datetime=self.start_time + timedelta(minutes=30),  # Cambio menor
            end_datetime=self.end_time + timedelta(minutes=30),
            exclude_schedule_id=existing_schedule.id
        )
        
        self.assertTrue(result)
    
    def test_validate_room_access_permission_valid(self):
        """
        Test: Debe permitir acceso cuando el monitor tiene turno activo
        """
        # Crear turno activo (en curso)
        active_schedule = Schedule.objects.create(
            user=self.monitor1,
            room=self.room1,
            start_datetime=self.now - timedelta(minutes=30),  # Comenzó hace 30 min
            end_datetime=self.now + timedelta(minutes=90),    # Termina en 90 min
            status=Schedule.ACTIVE,
            created_by=self.admin_user
        )
        
        # Validar acceso
        result = ScheduleValidationService.validate_room_access_permission(
            user=self.monitor1,
            room=self.room1,
            access_datetime=self.now
        )
        
        self.assertEqual(result, active_schedule)
    
    def test_validate_room_access_permission_denied(self):
        """
        Test: Debe denegar acceso cuando el monitor no tiene turno activo
        """
        # No crear turnos activos
        
        # Intentar validar acceso
        with self.assertRaises(ValidationError) as context:
            ScheduleValidationService.validate_room_access_permission(
                user=self.monitor1,
                room=self.room1,
                access_datetime=self.now
            )
        
        self.assertIn('access_denied', str(context.exception))
        self.assertIn('no tiene un turno asignado', str(context.exception))
    
    def test_check_schedule_compliance_compliant(self):
        """
        Test: Debe marcar como cumplido cuando hay entrada dentro del período de gracia
        """
        # Crear turno que comenzó hace 10 minutos
        schedule = Schedule.objects.create(
            user=self.monitor1,
            room=self.room1,
            start_datetime=self.now - timedelta(minutes=10),
            end_datetime=self.now + timedelta(minutes=110),
            status=Schedule.ACTIVE,
            created_by=self.admin_user
        )
        
        # Crear entrada dentro del período de gracia
        RoomEntry.objects.create(
            user=self.monitor1,
            room=self.room1,
            entry_time=self.now - timedelta(minutes=5),  # 5 min después del inicio
            exit_time=None
        )
        
        # Verificar cumplimiento
        result = ScheduleValidationService.check_schedule_compliance(schedule.id)
        
        self.assertEqual(result['status'], 'compliant')
        self.assertIn('entry_time', result)
    
    def test_check_schedule_compliance_non_compliant(self):
        """
        Test: Debe marcar como no cumplido cuando no hay entrada en período de gracia
        """
        # Crear turno que comenzó hace 25 minutos (fuera del período de gracia)
        schedule = Schedule.objects.create(
            user=self.monitor1,
            room=self.room1,
            start_datetime=self.now - timedelta(minutes=25),
            end_datetime=self.now + timedelta(minutes=95),
            status=Schedule.ACTIVE,
            created_by=self.admin_user
        )
        
        # No crear entrada de sala
        
        # Verificar cumplimiento
        result = ScheduleValidationService.check_schedule_compliance(schedule.id)
        
        self.assertEqual(result['status'], 'non_compliant')
        self.assertIn('schedule', result)
        self.assertIn('grace_deadline', result)
    
    def test_check_schedule_compliance_grace_period(self):
        """
        Test: Debe marcar como período de gracia cuando estamos dentro de los 20 minutos
        """
        # Crear turno que comenzó hace 15 minutos (dentro del período de gracia)
        schedule = Schedule.objects.create(
            user=self.monitor1,
            room=self.room1,
            start_datetime=self.now - timedelta(minutes=15),
            end_datetime=self.now + timedelta(minutes=105),
            status=Schedule.ACTIVE,
            created_by=self.admin_user
        )
        
        # Verificar cumplimiento
        result = ScheduleValidationService.check_schedule_compliance(schedule.id)
        
        self.assertEqual(result['status'], 'grace_period')
    
    @patch('notifications.models.Notification.objects.create')
    def test_notify_admin_schedule_non_compliance(self, mock_create_notification):
        """
        Test: Debe crear notificaciones para administradores en caso de incumplimiento
        """
        # Crear turno y resultado de incumplimiento
        schedule = Schedule.objects.create(
            user=self.monitor1,
            room=self.room1,
            start_datetime=self.now - timedelta(minutes=25),
            end_datetime=self.now + timedelta(minutes=95),
            status=Schedule.ACTIVE,
            created_by=self.admin_user
        )
        
        compliance_result = {
            'status': 'non_compliant',
            'grace_deadline': self.now - timedelta(minutes=5),
            'current_time': self.now
        }
        
        # Simular creación de notificación
        mock_notification = Notification(
            user=self.admin_user,
            title=f"Incumplimiento de Turno - {schedule.room.code}",
            message="Test message",
            notification_type='schedule_non_compliance'
        )
        mock_create_notification.return_value = mock_notification
        
        # Ejecutar notificación
        result = ScheduleValidationService.notify_admin_schedule_non_compliance(
            schedule, compliance_result
        )
        
        # Verificar que se llamó a create
        mock_create_notification.assert_called()
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0], mock_notification)


class ScheduleComplianceMonitorTest(TestCase):
    """
    Tests para el monitor automático de cumplimiento
    """
    
    def setUp(self):
        """
        Configurar datos de prueba
        """
        self.admin_user = User.objects.create_user(
            username='admin',
            identification='12345678',
            email='admin@test.com',
            password='testpass123',
            role='admin',
            is_verified=True
        )
        
        self.monitor1 = User.objects.create_user(
            username='monitor1',
            identification='87654321',
            email='monitor1@test.com',
            password='testpass123',
            role='monitor',
            is_verified=True
        )
        
        self.room1 = Room.objects.create(
            name='Sala de Computadores 1',
            code='SC1',  
            capacity=30,
            is_active=True
        )
        
        self.now = timezone.now()
    
    @patch('schedule.services.ScheduleValidationService.notify_admin_schedule_non_compliance')
    def test_check_overdue_schedules(self, mock_notify):
        """
        Test: Debe detectar turnos vencidos y generar notificaciones
        """
        # Crear turno vencido (comenzó hace 30 minutos, sin entrada)
        overdue_schedule = Schedule.objects.create(
            user=self.monitor1,
            room=self.room1,
            start_datetime=self.now - timedelta(minutes=30),
            end_datetime=self.now + timedelta(minutes=90),
            status=Schedule.ACTIVE,
            created_by=self.admin_user
        )
        
        # Mock de notificaciones
        mock_notification = Notification(
            user=self.admin_user,
            title="Test notification",
            message="Test message",
            notification_type='schedule_non_compliance'
        )
        mock_notify.return_value = [mock_notification]
        
        # Ejecutar verificación
        result = ScheduleComplianceMonitor.check_overdue_schedules()
        
        # Verificar resultados
        self.assertEqual(result['checked_schedules'], 1)
        self.assertEqual(result['notifications_generated'], 1)
        mock_notify.assert_called_once()