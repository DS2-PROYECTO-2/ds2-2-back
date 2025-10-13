from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from datetime import timedelta

from users.models import User
from schedule.models import Schedule
from .test_base import ScheduleTestBase


class AdminScheduleEndpointsTestCase(ScheduleTestBase):
    """
    Tests para endpoints específicos de administradores
    """
    
    def test_admin_overview_success(self):
        """Test de vista de resumen para administradores"""
        self.authenticate_as_admin()
        
        # Crear monitores adicionales
        monitor2 = User.objects.create_user(
            username='monitor2',
            email='monitor2@test.com',
            password='testpass123',
            role='monitor',
            identification='22222222',
            is_verified=True
        )
        
        # Crear turnos en diferentes estados
        current_schedule = Schedule.objects.create(
            user=self.monitor_user,
            room=self.room1,
            start_datetime=self.now - timedelta(hours=1),
            end_datetime=self.now + timedelta(hours=1),
            created_by=self.admin_user,
            status=Schedule.ACTIVE
        )
        
        upcoming_schedule = Schedule.objects.create(
            user=monitor2,
            room=self.room2,
            start_datetime=self.now + timedelta(hours=2),
            end_datetime=self.now + timedelta(hours=6),
            created_by=self.admin_user,
            status=Schedule.ACTIVE
        )
        
        completed_schedule = Schedule.objects.create(
            user=self.monitor_user,
            room=self.room1,
            start_datetime=self.now - timedelta(days=1),
            end_datetime=self.now - timedelta(days=1) + timedelta(hours=4),
            created_by=self.admin_user,
            status=Schedule.COMPLETED
        )
        
        cancelled_schedule = Schedule.objects.create(
            user=monitor2,
            room=self.room2,
            start_datetime=self.now + timedelta(days=2),
            end_datetime=self.now + timedelta(days=2, hours=4),
            created_by=self.admin_user,
            status=Schedule.CANCELLED
        )
        
        url = reverse('admin_schedules_overview')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verificar estructura de respuesta
        self.assertIn('overview', response.data)
        self.assertIn('upcoming_24h', response.data)
        self.assertIn('non_compliant_schedules', response.data)
        self.assertIn('generated_at', response.data)
        
        # Verificar estadísticas generales
        overview = response.data['overview']
        self.assertEqual(overview['total_schedules'], 4)
        self.assertEqual(overview['active_schedules'], 2)
        self.assertEqual(overview['current_schedules'], 1)
        
        # Verificar conteos por estado
        self.assertEqual(overview['schedules_by_status']['active'], 2)
        self.assertEqual(overview['schedules_by_status']['completed'], 1)
        self.assertEqual(overview['schedules_by_status']['cancelled'], 1)
        
        # Verificar turnos próximos (dentro de 24h)
        self.assertEqual(len(response.data['upcoming_24h']), 1)  # Solo el que está en 2 horas
        self.assertEqual(response.data['upcoming_24h'][0]['user_username'], monitor2.username)
    
    def test_admin_overview_non_compliant_schedules(self):
        """Test de turnos sin cumplimiento en overview"""
        self.authenticate_as_admin()
        
        # Crear turno completado pero sin entradas (no compliant)
        non_compliant_schedule = Schedule.objects.create(
            user=self.monitor_user,
            room=self.room1,
            start_datetime=self.now - timedelta(days=1),
            end_datetime=self.now - timedelta(days=1) + timedelta(hours=4),
            created_by=self.admin_user,
            status=Schedule.COMPLETED
        )
        
        url = reverse('admin_schedules_overview')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verificar que detecta el turno sin cumplimiento
        self.assertEqual(response.data['overview']['non_compliant_count'], 1)
        self.assertEqual(len(response.data['non_compliant_schedules']), 1)
        self.assertEqual(response.data['non_compliant_schedules'][0]['user_username'], self.monitor_user.username)
    
    def test_admin_overview_monitor_access_forbidden(self):
        """Test de acceso de monitor a overview (debe fallar)"""
        self.authenticate_as_monitor()
        
        url = reverse('admin_schedules_overview')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_admin_overview_unauthenticated_forbidden(self):
        """Test de acceso sin autenticación a overview"""
        self.clear_credentials()
        
        url = reverse('admin_schedules_overview')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_admin_overview_unverified_user_forbidden(self):
        """Test de acceso con usuario no verificado a overview"""
        self.authenticate_as_unverified()
        
        url = reverse('admin_schedules_overview')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_admin_can_view_all_schedules(self):
        """Test de que admin puede ver todos los turnos en listado"""
        self.authenticate_as_admin()
        
        # Crear monitor adicional
        monitor2 = User.objects.create_user(
            username='monitor2',
            email='monitor2@test.com',
            password='testpass123',
            role='monitor',
            identification='22222222',
            is_verified=True
        )
        
        # Crear turnos para diferentes monitores
        Schedule.objects.create(
            user=self.monitor_user,
            room=self.room1,
            start_datetime=self.now + timedelta(days=1),
            end_datetime=self.now + timedelta(days=1, hours=4),
            created_by=self.admin_user
        )
        
        Schedule.objects.create(
            user=monitor2,
            room=self.room2,
            start_datetime=self.now + timedelta(days=2),
            end_datetime=self.now + timedelta(days=2, hours=4),
            created_by=self.admin_user
        )
        
        url = reverse('schedule-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)  # Ve todos los turnos
        
        # Verificar que ve turnos de diferentes monitores
        usernames = [schedule['user_username'] for schedule in response.data['results']]
        self.assertIn(self.monitor_user.username, usernames)
        self.assertIn(monitor2.username, usernames)
    
    def test_admin_schedule_detail_includes_compliance(self):
        """Test de que el detalle incluye información de cumplimiento"""
        self.authenticate_as_admin()
        
        # Crear turno
        schedule = Schedule.objects.create(
            user=self.monitor_user,
            room=self.room1,
            start_datetime=self.now - timedelta(days=1),
            end_datetime=self.now - timedelta(days=1) + timedelta(hours=4),
            created_by=self.admin_user,
            status=Schedule.COMPLETED
        )
        
        url = reverse('schedule-detail', kwargs={'pk': schedule.id})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verificar campos específicos para admin
        self.assertIn('has_compliance', response.data)
        self.assertIn('room_entries', response.data)
        self.assertIn('user_details', response.data)
        self.assertIn('room_details', response.data)
        
        # Verificar que has_compliance es False (no hay entradas)
        self.assertFalse(response.data['has_compliance'])
        self.assertEqual(len(response.data['room_entries']), 0)
    
    def test_admin_can_create_schedule_for_any_monitor(self):
        """Test de que admin puede crear turnos para cualquier monitor"""
        self.authenticate_as_admin()
        
        # Crear otro monitor
        monitor2 = User.objects.create_user(
            username='monitor2',
            email='monitor2@test.com',
            password='testpass123',
            role='monitor',
            identification='22222222',
            is_verified=True
        )
        
        url = reverse('schedule-list')
        data = {
            'user': monitor2.id,
            'room': self.room1.id,
            'start_datetime': (self.now + timedelta(days=1)).isoformat(),
            'end_datetime': (self.now + timedelta(days=1, hours=4)).isoformat(),
            'notes': 'Turno para otro monitor'
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        schedule = Schedule.objects.first()
        self.assertEqual(schedule.user, monitor2)
        self.assertEqual(schedule.created_by, self.admin_user)
        self.assertEqual(schedule.notes, 'Turno para otro monitor')
    
    def test_admin_can_modify_any_schedule(self):
        """Test de que admin puede modificar cualquier turno"""
        self.authenticate_as_admin()
        
        # Crear otro admin y monitor
        admin2 = User.objects.create_user(
            username='admin2',
            email='admin2@test.com',
            password='testpass123',
            role='admin',
            identification='33333333',
            is_verified=True
        )
        
        monitor2 = User.objects.create_user(
            username='monitor2',
            email='monitor2@test.com',
            password='testpass123',
            role='monitor',
            identification='22222222',
            is_verified=True
        )
        
        # Crear turno creado por otro admin para otro monitor
        schedule = Schedule.objects.create(
            user=monitor2,
            room=self.room1,
            start_datetime=self.now + timedelta(days=1),
            end_datetime=self.now + timedelta(days=1, hours=4),
            created_by=admin2,
            notes='Original'
        )
        
        url = reverse('schedule-detail', kwargs={'pk': schedule.id})
        data = {
            'user': monitor2.id,
            'room': self.room2.id,
            'start_datetime': (self.now + timedelta(days=1)).isoformat(),
            'end_datetime': (self.now + timedelta(days=1, hours=6)).isoformat(),
            'notes': 'Modificado por otro admin',
            'status': 'active'
        }
        
        response = self.client.put(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        schedule.refresh_from_db()
        self.assertEqual(schedule.room, self.room2)
        self.assertEqual(schedule.notes, 'Modificado por otro admin')
        self.assertEqual(schedule.created_by, admin2)  # No cambia el creador original