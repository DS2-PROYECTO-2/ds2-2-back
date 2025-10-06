from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from django.utils import timezone
from datetime import timedelta

from users.models import User
from rooms.models import Room, RoomEntry
from schedule.models import Schedule
from notifications.models import Notification


class ScheduleValidationEndpointsTest(TestCase):
    """
    Tests para endpoints de validación de turnos - Tarea 2
    """
    
    def setUp(self):
        """Configurar datos de prueba"""
        self.client = APIClient()
        
        # Crear usuarios
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
        
        # Crear sala
        self.room = Room.objects.create(
            name='Sala Test',
            code='ST001',
            capacity=20,
            is_active=True
        )
        
        self.now = timezone.now()
        
        # URLs
        self.validate_room_access_url = reverse('validate_room_access')
        self.notify_non_compliance_url = reverse('notify_non_compliance')
        self.monitor_compliance_url = reverse('monitor_compliance')
        
    def test_validate_room_access_with_valid_schedule(self):
        """Test: Validar acceso a sala con turno activo"""
        # Crear turno activo
        Schedule.objects.create(
            user=self.monitor,
            room=self.room,
            start_datetime=self.now - timedelta(minutes=30),
            end_datetime=self.now + timedelta(hours=1),
            created_by=self.admin,
            status=Schedule.ACTIVE
        )
        
        # Autenticar como monitor
        self.client.force_authenticate(user=self.monitor)
        
        data = {
            'room_id': self.room.id
        }
        
        response = self.client.post(self.validate_room_access_url, data)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['access_granted'])
        self.assertIn('active_schedule', response.data)
        self.assertIn('message', response.data)
        
    def test_validate_room_access_without_schedule(self):
        """Test: Denegar acceso a sala sin turno activo"""
        # Autenticar como monitor
        self.client.force_authenticate(user=self.monitor)
        
        data = {
            'room_id': self.room.id
        }
        
        response = self.client.post(self.validate_room_access_url, data)
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertFalse(response.data['access_granted'])
        self.assertIn('validation_error', response.data)
        
    def test_validate_room_access_missing_room_id(self):
        """Test: Error cuando falta room_id"""
        self.client.force_authenticate(user=self.monitor)
        
        response = self.client.post(self.validate_room_access_url, {})
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('room_id es requerido', response.data['error'])
        
    def test_validate_room_access_room_not_found(self):
        """Test: Error cuando la sala no existe"""
        self.client.force_authenticate(user=self.monitor)
        
        data = {
            'room_id': 9999  # ID inexistente
        }
        
        response = self.client.post(self.validate_room_access_url, data)
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn('Sala no encontrada', response.data['error'])
        

        

        

        

        

        
    def test_notify_schedule_non_compliance_success(self):
        """Test: Notificar incumplimiento exitosamente"""
        # Crear turno vencido sin cumplimiento
        past_schedule = Schedule.objects.create(
            user=self.monitor,
            room=self.room,
            start_datetime=self.now - timedelta(hours=2),
            end_datetime=self.now - timedelta(hours=1),
            created_by=self.admin,
            status=Schedule.ACTIVE
        )
        
        self.client.force_authenticate(user=self.admin)
        
        data = {
            'schedule_id': past_schedule.id
        }
        
        response = self.client.post(self.notify_non_compliance_url, data)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['notification_sent'])
        self.assertEqual(response.data['notifications_created'], 1)
        
        # Verificar que se creó la notificación
        notification = Notification.objects.filter(
            user=self.admin,
            notification_type='schedule_non_compliance'
        ).first()
        self.assertIsNotNone(notification)
        
    def test_notify_schedule_non_compliance_not_required(self):
        """Test: No notificar cuando no es necesario"""
        # Crear turno futuro
        future_schedule = Schedule.objects.create(
            user=self.monitor,
            room=self.room,
            start_datetime=self.now + timedelta(hours=1),
            end_datetime=self.now + timedelta(hours=3),
            created_by=self.admin,
            status=Schedule.ACTIVE
        )
        
        self.client.force_authenticate(user=self.admin)
        
        data = {
            'schedule_id': future_schedule.id
        }
        
        response = self.client.post(self.notify_non_compliance_url, data)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(response.data['notification_sent'])
        self.assertIn('No se requiere notificación', response.data['reason'])
        
    def test_notify_schedule_non_compliance_schedule_not_found(self):
        """Test: Error cuando el turno no existe"""
        self.client.force_authenticate(user=self.admin)
        
        data = {
            'schedule_id': 9999  # ID inexistente
        }
        
        response = self.client.post(self.notify_non_compliance_url, data)
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn('Turno no encontrado', response.data['error'])
        
    def test_monitor_schedule_compliance_current_date(self):
        """Test: Obtener estado de cumplimiento para fecha actual"""
        today = self.now.date()
        
        # Crear turno de hoy con cumplimiento
        schedule = Schedule.objects.create(
            user=self.monitor,
            room=self.room,
            start_datetime=self.now - timedelta(hours=2),
            end_datetime=self.now - timedelta(hours=1),
            created_by=self.admin,
            status=Schedule.ACTIVE
        )
        
        # Crear entrada para cumplimiento
        RoomEntry.objects.create(
            user=self.monitor,
            room=self.room,
            entry_time=schedule.start_datetime + timedelta(minutes=5)
        )
        
        self.client.force_authenticate(user=self.monitor)
        
        response = self.client.get(self.monitor_compliance_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['date'], today.isoformat())
        self.assertEqual(response.data['total_schedules'], 1)
        self.assertEqual(response.data['compliant'], 1)
        self.assertEqual(response.data['non_compliant'], 0)
        
    def test_monitor_schedule_compliance_specific_date(self):
        """Test: Obtener estado de cumplimiento para fecha específica"""
        target_date = self.now.date() - timedelta(days=1)
        
        # Crear turno para ayer
        yesterday_start = timezone.make_aware(
            timezone.datetime.combine(target_date, timezone.datetime.min.time())
        ) + timedelta(hours=9)
        
        Schedule.objects.create(
            user=self.monitor,
            room=self.room,
            start_datetime=yesterday_start,
            end_datetime=yesterday_start + timedelta(hours=2),
            created_by=self.admin,
            status=Schedule.ACTIVE
        )
        
        self.client.force_authenticate(user=self.monitor)
        
        response = self.client.get(self.monitor_compliance_url, {'date': target_date.strftime('%Y-%m-%d')})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['date'], target_date.isoformat())
        self.assertEqual(response.data['total_schedules'], 1)
        
    def test_monitor_schedule_compliance_invalid_date_format(self):
        """Test: Error con formato de fecha inválido"""
        self.client.force_authenticate(user=self.monitor)
        
        response = self.client.get(self.monitor_compliance_url, {'date': 'invalid-date'})
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('Formato de fecha inválido', response.data['error'])
        
    def test_schedule_viewset_create_with_validations(self):
        """Test: Crear turno con validaciones integradas"""
        self.client.force_authenticate(user=self.admin)
        
        start_time = self.now + timedelta(hours=1)
        data = {
            'user': self.monitor.id,
            'room': self.room.id,
            'start_datetime': start_time.isoformat(),
            'end_datetime': (start_time + timedelta(hours=2)).isoformat(),
            'notes': 'Turno de prueba con validaciones'
        }
        
        url = reverse('schedule-list')
        response = self.client.post(url, data)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['user_details']['id'], self.monitor.id)
        self.assertEqual(response.data['room_details']['id'], self.room.id)
        
    def test_schedule_viewset_create_with_conflict(self):
        """Test: Error al crear turno con conflicto"""
        # Crear turno existente
        existing_start = self.now + timedelta(hours=1)
        Schedule.objects.create(
            user=self.monitor,
            room=self.room,
            start_datetime=existing_start,
            end_datetime=existing_start + timedelta(hours=2),
            created_by=self.admin,
            status=Schedule.ACTIVE
        )
        
        self.client.force_authenticate(user=self.admin)
        
        # Intentar crear turno conflictivo
        conflicting_start = existing_start + timedelta(minutes=30)
        data = {
            'user': self.monitor.id,
            'room': self.room.id,
            'start_datetime': conflicting_start.isoformat(),
            'end_datetime': (conflicting_start + timedelta(hours=2)).isoformat()
        }
        
        url = reverse('schedule-list')
        response = self.client.post(url, data)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
        self.assertIn('details', response.data)
        
    def test_schedule_viewset_compliance_action(self):
        """Test: Acción de verificar cumplimiento en ViewSet"""
        # Crear turno con cumplimiento
        schedule = Schedule.objects.create(
            user=self.monitor,
            room=self.room,
            start_datetime=self.now - timedelta(hours=2),
            end_datetime=self.now - timedelta(hours=1),
            created_by=self.admin,
            status=Schedule.ACTIVE
        )
        
        RoomEntry.objects.create(
            user=self.monitor,
            room=self.room,
            entry_time=schedule.start_datetime + timedelta(minutes=5)
        )
        
        self.client.force_authenticate(user=self.admin)
        
        url = reverse('schedule-compliance', kwargs={'pk': schedule.id})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['schedule_id'], schedule.id)
        self.assertIn('compliance_info', response.data)
        
    def test_schedule_viewset_check_compliance_batch(self):
        """Test: Verificación batch de cumplimiento"""
        self.client.force_authenticate(user=self.admin)
        
        url = reverse('schedule-check-compliance-batch')
        response = self.client.post(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('checked_schedules', response.data)
        self.assertIn('notifications_sent', response.data)
        self.assertIn('compliant_schedules', response.data)
        self.assertIn('non_compliant_schedules', response.data)
        
    def test_permissions_admin_only_endpoints(self):
        """Test: Endpoints solo para administradores"""
        # Autenticar como monitor (no admin)
        self.client.force_authenticate(user=self.monitor)
        
        # Intentar acceder a endpoints de admin
        admin_endpoints = [
            (self.notify_non_compliance_url, {'schedule_id': 1}),
        ]
        
        for url, data in admin_endpoints:
            response = self.client.post(url, data)
            self.assertIn(response.status_code, [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN])
            
    def test_permissions_authenticated_required(self):
        """Test: Endpoints requieren autenticación"""
        # No autenticar
        endpoints = [
            (self.validate_room_access_url, {'room_id': 1}),
            (self.monitor_compliance_url, {}),
        ]
        
        for url, data in endpoints:
            if data:
                response = self.client.post(url, data)
            else:
                response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)