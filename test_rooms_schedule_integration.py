"""
Test de integración para validar que el sistema de rooms ahora requiere turnos
y previene múltiples monitores por sala (PETICIÓN 2)
"""
from django.test import TestCase
from django.utils import timezone
from users.models import User
from datetime import datetime, timedelta

from rooms.models import Room, RoomEntry
from rooms.services import RoomEntryBusinessLogic, ScheduleValidationService
from schedule.models import Schedule


class RoomScheduleIntegrationTest(TestCase):
    """
    Tests de integración entre sistema de rooms y schedule
    Verificar que las validaciones de TAREA 2 están funcionando
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
        
        self.monitor2 = User.objects.create_user(
            username='monitor2',
            identification='11223344',
            email='monitor2@test.com',
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
    
    def test_room_entry_requires_schedule(self):
        """
        Test: Debe requerir turno asignado para entrar a sala
        """
        # Intentar entrar sin turno
        result = RoomEntryBusinessLogic.create_room_entry_with_validations(
            user=self.monitor1,
            room=self.room1,
            notes="Test entry"
        )
        
        # Debe fallar
        self.assertFalse(result['success'])
        self.assertIn('schedule_required', result.get('details', {}).get('reason', ''))
        self.assertIn('Sin turno asignado', result['error'])
    
    def test_room_entry_with_valid_schedule(self):
        """
        Test: Debe permitir entrada con turno válido
        """
        # Crear turno activo
        schedule = Schedule.objects.create(
            user=self.monitor1,
            room=self.room1,
            start_datetime=self.now - timedelta(minutes=10),  # Comenzó hace 10 min
            end_datetime=self.now + timedelta(minutes=110),   # Termina en 110 min
            status=Schedule.ACTIVE,
            created_by=self.admin_user
        )
        
        # Intentar entrar con turno válido
        result = RoomEntryBusinessLogic.create_room_entry_with_validations(
            user=self.monitor1,
            room=self.room1,
            notes="Test entry with schedule"
        )
        
        # Debe funcionar
        self.assertTrue(result['success'])
        self.assertIn('schedule', result)
        self.assertEqual(result['schedule']['id'], schedule.id)
        self.assertIn('Acceso concedido', result['message'])
    
    def test_prevent_multiple_monitors_per_room(self):
        """
        Test: Debe prevenir múltiples monitores en la misma sala (PETICIÓN 2)
        """
        # Crear turnos para ambos monitores en la misma sala
        schedule1 = Schedule.objects.create(
            user=self.monitor1,
            room=self.room1,
            start_datetime=self.now - timedelta(minutes=10),
            end_datetime=self.now + timedelta(minutes=110),
            status=Schedule.ACTIVE,
            created_by=self.admin_user
        )
        
        schedule2 = Schedule.objects.create(
            user=self.monitor2,
            room=self.room1,
            start_datetime=self.now - timedelta(minutes=5),
            end_datetime=self.now + timedelta(minutes=115),
            status=Schedule.ACTIVE,
            created_by=self.admin_user
        )
        
        # Monitor1 entra primero
        result1 = RoomEntryBusinessLogic.create_room_entry_with_validations(
            user=self.monitor1,
            room=self.room1,
            notes="First entry"
        )
        self.assertTrue(result1['success'])
        
        # Monitor2 intenta entrar (debe fallar)
        result2 = RoomEntryBusinessLogic.create_room_entry_with_validations(
            user=self.monitor2,
            room=self.room1,
            notes="Second entry - should fail"
        )
        
        # Debe fallar por múltiples monitores
        self.assertFalse(result2['success'])
        self.assertIn('room_occupied', result2.get('details', {}).get('reason', ''))
        self.assertIn('Sala ocupada por otro monitor', result2['error'])
    
    def test_schedule_validation_service_integration(self):
        """
        Test: Verificar que ScheduleValidationService funciona correctamente
        """
        # Crear turno activo
        schedule = Schedule.objects.create(
            user=self.monitor1,
            room=self.room1,
            start_datetime=self.now - timedelta(minutes=10),
            end_datetime=self.now + timedelta(minutes=110),
            status=Schedule.ACTIVE,
            created_by=self.admin_user
        )
        
        # Validar acceso con turno válido
        active_schedule = ScheduleValidationService.validate_room_access_permission(
            user=self.monitor1,
            room=self.room1,
            access_datetime=self.now
        )
        
        self.assertEqual(active_schedule, schedule)
        
        # Validar sin turno válido
        with self.assertRaises(Exception):
            ScheduleValidationService.validate_room_access_permission(
                user=self.monitor2,  # Sin turno
                room=self.room1,
                access_datetime=self.now
            )
    
    def test_multiple_monitors_validation_service(self):
        """
        Test: Verificar validación de múltiples monitores
        """
        # Crear entrada activa
        entry = RoomEntry.objects.create(
            user=self.monitor1,
            room=self.room1,
            active=True
        )
        
        # Validar que detecta múltiples monitores
        with self.assertRaises(Exception):
            ScheduleValidationService.validate_no_multiple_monitors_in_room(
                room=self.room1,
                exclude_user=None
            )
        
        # Validar que excluye usuario correcto
        result = ScheduleValidationService.validate_no_multiple_monitors_in_room(
            room=self.room1,
            exclude_user=self.monitor1
        )
        self.assertTrue(result)