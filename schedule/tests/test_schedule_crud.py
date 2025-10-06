from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from datetime import timedelta

from users.models import User
from schedule.models import Schedule
from .test_base import ScheduleTestBase


class ScheduleCRUDTestCase(ScheduleTestBase):
    """
    Tests para endpoints CRUD de Schedule
    """
    
    def test_create_schedule_as_admin_success(self):
        """Test de creación exitosa de turno por admin"""
        self.authenticate_as_admin()
        
        url = reverse('schedule-list')
        data = {
            'user': self.monitor_user.id,
            'room': self.room1.id,
            'start_datetime': (self.now + timedelta(days=1)).isoformat(),
            'end_datetime': (self.now + timedelta(days=1, hours=4)).isoformat(),
            'notes': 'Turno de prueba',
            'recurring': False
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Schedule.objects.count(), 1)
        
        schedule = Schedule.objects.first()
        self.assertEqual(schedule.user, self.monitor_user)
        self.assertEqual(schedule.room, self.room1)
        self.assertEqual(schedule.created_by, self.admin_user)
        self.assertEqual(schedule.notes, 'Turno de prueba')
    
    def test_create_schedule_as_monitor_forbidden(self):
        """Test de creación de turno por monitor (debe fallar)"""
        self.authenticate_as_monitor()
        
        url = reverse('schedule-list')
        data = {
            'user': self.monitor_user.id,
            'room': self.room1.id,
            'start_datetime': (self.now + timedelta(days=1)).isoformat(),
            'end_datetime': (self.now + timedelta(days=1, hours=4)).isoformat()
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Schedule.objects.count(), 0)
    
    def test_create_schedule_unverified_user_forbidden(self):
        """Test de creación por usuario no verificado"""
        self.authenticate_as_unverified()
        
        url = reverse('schedule-list')
        data = {
            'user': self.monitor_user.id,
            'room': self.room1.id,
            'start_datetime': (self.now + timedelta(days=1)).isoformat(),
            'end_datetime': (self.now + timedelta(days=1, hours=4)).isoformat()
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_create_schedule_validation_errors(self):
        """Test de errores de validación en creación"""
        self.authenticate_as_admin()
        
        url = reverse('schedule-list')
        
        # Test: fecha fin antes que fecha inicio
        data = {
            'user': self.monitor_user.id,
            'room': self.room1.id,
            'start_datetime': (self.now + timedelta(days=1)).isoformat(),
            'end_datetime': (self.now + timedelta(hours=12)).isoformat()  # Antes que start
        }
        
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('end_datetime', response.data)
        
        # Test: duración excesiva
        data = {
            'user': self.monitor_user.id,
            'room': self.room1.id,
            'start_datetime': (self.now + timedelta(days=1)).isoformat(),
            'end_datetime': (self.now + timedelta(days=1, hours=13)).isoformat()  # 13 horas
        }
        
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('end_datetime', response.data)
        
        # Test: usuario no monitor
        data = {
            'user': self.admin_user.id,  # Admin, no monitor
            'room': self.room1.id,
            'start_datetime': (self.now + timedelta(days=1)).isoformat(),
            'end_datetime': (self.now + timedelta(days=1, hours=4)).isoformat()
        }
        
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('user', response.data)
        
        # Test: monitor no verificado
        data = {
            'user': self.unverified_monitor.id,
            'room': self.room1.id,
            'start_datetime': (self.now + timedelta(days=1)).isoformat(),
            'end_datetime': (self.now + timedelta(days=1, hours=4)).isoformat()
        }
        
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('user', response.data)
    
    def test_list_schedules_as_admin(self):
        """Test de listado de turnos como admin"""
        self.authenticate_as_admin()
        
        # Crear turnos de prueba
        Schedule.objects.create(
            user=self.monitor_user,
            room=self.room1,
            start_datetime=self.now + timedelta(days=1),
            end_datetime=self.now + timedelta(days=1, hours=4),
            created_by=self.admin_user
        )
        
        url = reverse('schedule-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        
        schedule_data = response.data['results'][0]
        self.assertIn('user_full_name', schedule_data)
        self.assertIn('room_name', schedule_data)
        self.assertIn('duration_hours', schedule_data)
    
    def test_list_schedules_as_monitor(self):
        """Test de listado de turnos como monitor (solo propios)"""
        self.authenticate_as_monitor()
        
        # Crear turno para el monitor autenticado
        Schedule.objects.create(
            user=self.monitor_user,
            room=self.room1,
            start_datetime=self.now + timedelta(days=1),
            end_datetime=self.now + timedelta(days=1, hours=4),
            created_by=self.admin_user
        )
        
        # Crear turno para otro monitor
        other_monitor = User.objects.create_user(
            username='other_monitor',
            email='other@test.com',
            password='testpass123',
            role='monitor',
            identification='99999999',
            is_verified=True
        )
        
        Schedule.objects.create(
            user=other_monitor,
            room=self.room2,
            start_datetime=self.now + timedelta(days=2),
            end_datetime=self.now + timedelta(days=2, hours=4),
            created_by=self.admin_user
        )
        
        url = reverse('schedule-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)  # Solo ve su propio turno
        self.assertEqual(response.data['results'][0]['user_username'], self.monitor_user.username)
    
    def test_retrieve_schedule_detail(self):
        """Test de obtener detalle de turno"""
        self.authenticate_as_admin()
        
        schedule = Schedule.objects.create(
            user=self.monitor_user,
            room=self.room1,
            start_datetime=self.now + timedelta(days=1),
            end_datetime=self.now + timedelta(days=1, hours=4),
            created_by=self.admin_user,
            notes='Turno detallado'
        )
        
        url = reverse('schedule-detail', kwargs={'pk': schedule.id})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('user_details', response.data)
        self.assertIn('room_details', response.data)
        self.assertIn('created_by_name', response.data)
        self.assertIn('has_compliance', response.data)
        self.assertEqual(response.data['notes'], 'Turno detallado')
    
    def test_update_schedule_as_admin(self):
        """Test de actualización de turno por admin"""
        self.authenticate_as_admin()
        
        schedule = Schedule.objects.create(
            user=self.monitor_user,
            room=self.room1,
            start_datetime=self.now + timedelta(days=1),
            end_datetime=self.now + timedelta(days=1, hours=4),
            created_by=self.admin_user
        )
        
        url = reverse('schedule-detail', kwargs={'pk': schedule.id})
        data = {
            'user': self.monitor_user.id,
            'room': self.room2.id,  # Cambiar sala
            'start_datetime': (self.now + timedelta(days=1)).isoformat(),
            'end_datetime': (self.now + timedelta(days=1, hours=6)).isoformat(),  # Cambiar duración
            'notes': 'Turno actualizado',
            'status': 'active'
        }
        
        response = self.client.put(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        schedule.refresh_from_db()
        self.assertEqual(schedule.room, self.room2)
        self.assertEqual(schedule.duration_hours, 6.0)
        self.assertEqual(schedule.notes, 'Turno actualizado')
    
    def test_update_schedule_as_monitor_forbidden(self):
        """Test de actualización por monitor (debe fallar)"""
        self.authenticate_as_monitor()
        
        schedule = Schedule.objects.create(
            user=self.monitor_user,
            room=self.room1,
            start_datetime=self.now + timedelta(days=1),
            end_datetime=self.now + timedelta(days=1, hours=4),
            created_by=self.admin_user
        )
        
        url = reverse('schedule-detail', kwargs={'pk': schedule.id})
        data = {
            'notes': 'Intento de actualización'
        }
        
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_delete_schedule_as_admin(self):
        """Test de eliminación de turno por admin"""
        self.authenticate_as_admin()
        
        schedule = Schedule.objects.create(
            user=self.monitor_user,
            room=self.room1,
            start_datetime=self.now + timedelta(days=1),
            end_datetime=self.now + timedelta(days=1, hours=4),
            created_by=self.admin_user
        )
        
        url = reverse('schedule-detail', kwargs={'pk': schedule.id})
        response = self.client.delete(url)
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Schedule.objects.count(), 0)
    
    def test_delete_schedule_as_monitor_forbidden(self):
        """Test de eliminación por monitor (debe fallar)"""
        self.authenticate_as_monitor()
        
        schedule = Schedule.objects.create(
            user=self.monitor_user,
            room=self.room1,
            start_datetime=self.now + timedelta(days=1),
            end_datetime=self.now + timedelta(days=1, hours=4),
            created_by=self.admin_user
        )
        
        url = reverse('schedule-detail', kwargs={'pk': schedule.id})
        response = self.client.delete(url)
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Schedule.objects.count(), 1)
    
    def test_unauthenticated_access_forbidden(self):
        """Test de acceso sin autenticación"""
        self.clear_credentials()
        
        url = reverse('schedule-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)