from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from datetime import timedelta

from schedule.models import Schedule
from .test_base import ScheduleTestBase


class MonitorScheduleEndpointsTestCase(ScheduleTestBase):
    """
    Tests para endpoints específicos de monitores
    """
    
    def test_monitor_schedules_view_success(self):
        """Test de vista de turnos del monitor"""
        self.authenticate_as_monitor()
        
        # Crear turnos para el monitor
        current_schedule = Schedule.objects.create(
            user=self.monitor_user,
            room=self.room1,
            start_datetime=self.now - timedelta(hours=1),
            end_datetime=self.now + timedelta(hours=1),
            created_by=self.admin_user,
            notes='Turno actual'
        )
        
        upcoming_schedule = Schedule.objects.create(
            user=self.monitor_user,
            room=self.room2,
            start_datetime=self.now + timedelta(days=1),
            end_datetime=self.now + timedelta(days=1, hours=4),
            created_by=self.admin_user,
            notes='Turno próximo'
        )
        
        past_schedule = Schedule.objects.create(
            user=self.monitor_user,
            room=self.room1,
            start_datetime=self.now - timedelta(days=1),
            end_datetime=self.now - timedelta(days=1) + timedelta(hours=4),
            created_by=self.admin_user,
            status=Schedule.COMPLETED,
            notes='Turno pasado'
        )
        
        url = reverse('monitor_schedules')
        response = self.client.get(url, {'status': 'all'})  # Ver todos los estados
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verificar estructura de respuesta
        self.assertIn('monitor', response.data)
        self.assertIn('summary', response.data)
        self.assertIn('current_schedules', response.data)
        self.assertIn('upcoming_schedules', response.data)
        self.assertIn('past_schedules', response.data)
        
        # Verificar conteos - debería mostrar todos los turnos del monitor
        self.assertEqual(response.data['summary']['total_schedules'], 3)
        self.assertEqual(response.data['summary']['current_schedules'], 1)
        self.assertEqual(response.data['summary']['upcoming_schedules'], 1)
        # El past_schedules puede variar dependiendo del orden de los últimos 20
        
        # Verificar datos del monitor
        self.assertEqual(response.data['monitor']['username'], self.monitor_user.username)
        
        # Verificar que solo aparecen turnos del monitor autenticado
        self.assertEqual(len(response.data['current_schedules']), 1)
        self.assertEqual(response.data['current_schedules'][0]['notes'], 'Turno actual')
    
    def test_monitor_schedules_with_filters(self):
        """Test de filtros en vista de turnos del monitor"""
        self.authenticate_as_monitor()
        
        # Crear turnos en diferentes fechas
        yesterday = self.now - timedelta(days=1)
        tomorrow = self.now + timedelta(days=1)
        
        Schedule.objects.create(
            user=self.monitor_user,
            room=self.room1,
            start_datetime=yesterday,
            end_datetime=yesterday + timedelta(hours=4),
            created_by=self.admin_user,
            status=Schedule.COMPLETED
        )
        
        Schedule.objects.create(
            user=self.monitor_user,
            room=self.room2,
            start_datetime=tomorrow,
            end_datetime=tomorrow + timedelta(hours=4),
            created_by=self.admin_user
        )
        
        # Test filtro por fecha desde (turnos desde hoy en adelante)
        url = reverse('monitor_schedules')
        response = self.client.get(url, {
            'date_from': self.now.date().strftime('%Y-%m-%d'),
            'status': 'all'
        })
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Debería mostrar solo el turno de mañana (el de ayer se filtra)
        self.assertEqual(response.data['summary']['total_schedules'], 1)
        
        # Test filtro por fecha hasta (turnos hasta ayer)
        response = self.client.get(url, {
            'date_to': yesterday.date().strftime('%Y-%m-%d'),
            'status': 'all'
        })
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Debería mostrar solo el turno de ayer (el de mañana se filtra)
        self.assertEqual(response.data['summary']['total_schedules'], 1)
        
        # Test filtro por estado
        response = self.client.get(url, {'status': 'completed'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['summary']['total_schedules'], 1)  # Solo el completado
    
    def test_monitor_schedules_invalid_date_filter(self):
        """Test de filtro con fecha inválida"""
        self.authenticate_as_monitor()
        
        url = reverse('monitor_schedules')
        response = self.client.get(url, {'date_from': 'invalid-date'})
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
    
    def test_monitor_current_schedule_with_active(self):
        """Test de turno actual cuando existe"""
        self.authenticate_as_monitor()
        
        # Crear turno actual
        Schedule.objects.create(
            user=self.monitor_user,
            room=self.room1,
            start_datetime=self.now - timedelta(hours=1),
            end_datetime=self.now + timedelta(hours=1),
            created_by=self.admin_user,
            notes='Turno en curso'
        )
        
        url = reverse('monitor_current')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['has_current_schedule'])
        self.assertIsNotNone(response.data['current_schedule'])
        self.assertEqual(response.data['current_schedule']['notes'], 'Turno en curso')
        self.assertIn('room_name', response.data['current_schedule'])
        self.assertIn('duration_hours', response.data['current_schedule'])
    
    def test_monitor_current_schedule_without_active(self):
        """Test de turno actual cuando no existe"""
        self.authenticate_as_monitor()
        
        # Crear solo turnos futuros
        Schedule.objects.create(
            user=self.monitor_user,
            room=self.room1,
            start_datetime=self.now + timedelta(hours=2),
            end_datetime=self.now + timedelta(hours=6),
            created_by=self.admin_user
        )
        
        url = reverse('monitor_current')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(response.data['has_current_schedule'])
        self.assertIsNone(response.data['current_schedule'])
    
    def test_monitor_endpoints_unauthenticated(self):
        """Test de acceso sin autenticación a endpoints de monitor"""
        self.clear_credentials()
        
        # Test my-schedules
        url = reverse('monitor_schedules')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        
        # Test my-current-schedule
        url = reverse('monitor_current')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_monitor_endpoints_unverified_user(self):
        """Test de acceso con usuario no verificado"""
        self.authenticate_as_unverified()
        
        # Test my-schedules
        url = reverse('monitor_schedules')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        
        # Test my-current-schedule
        url = reverse('monitor_current')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_viewset_upcoming_action(self):
        """Test de acción upcoming del ViewSet"""
        self.authenticate_as_monitor()
        
        # Crear turnos próximos y lejanos
        near_future = self.now + timedelta(days=2)
        far_future = self.now + timedelta(days=10)
        
        upcoming_schedule = Schedule.objects.create(
            user=self.monitor_user,
            room=self.room1,
            start_datetime=near_future,
            end_datetime=near_future + timedelta(hours=4),
            created_by=self.admin_user
        )
        
        far_schedule = Schedule.objects.create(
            user=self.monitor_user,
            room=self.room2,
            start_datetime=far_future,
            end_datetime=far_future + timedelta(hours=4),
            created_by=self.admin_user
        )
        
        url = reverse('schedule-upcoming')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('count', response.data)
        self.assertIn('upcoming_schedules', response.data)
        
        # Solo debe aparecer el turno próximo (dentro de 7 días)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(len(response.data['upcoming_schedules']), 1)
    
    def test_viewset_current_action(self):
        """Test de acción current del ViewSet"""
        self.authenticate_as_monitor()
        
        # Crear turno actual
        Schedule.objects.create(
            user=self.monitor_user,
            room=self.room1,
            start_datetime=self.now - timedelta(minutes=30),
            end_datetime=self.now + timedelta(minutes=30),
            created_by=self.admin_user
        )
        
        # Crear turno futuro
        Schedule.objects.create(
            user=self.monitor_user,
            room=self.room2,
            start_datetime=self.now + timedelta(hours=2),
            end_datetime=self.now + timedelta(hours=6),
            created_by=self.admin_user
        )
        
        url = reverse('schedule-current')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('count', response.data)
        self.assertIn('current_schedules', response.data)
        
        # Solo debe aparecer el turno actual
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(len(response.data['current_schedules']), 1)