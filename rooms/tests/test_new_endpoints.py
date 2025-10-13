"""
Tests esenciales para los nuevos endpoints implementados
"""

from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework.test import APIClient
from rest_framework import status
from rest_framework.authtoken.models import Token
from datetime import timedelta
import json

from rooms.models import Room, RoomEntry
from schedule.models import Schedule

User = get_user_model()


class NewEndpointsTest(TestCase):
    """Tests básicos para los nuevos endpoints de reportes y validación"""
    
    def setUp(self):
        """Configuración inicial"""
        # Crear usuarios
        self.monitor = User.objects.create_user(
            username='monitor_test',
            identification='123456789',
            email='monitor@test.com',
            password='test123',
            first_name='Test',
            last_name='Monitor',
            role='monitor',
            is_verified=True
        )
        
        self.admin = User.objects.create_user(
            username='admin_test',
            identification='987654321',
            email='admin@test.com', 
            password='admin123',
            first_name='Test',
            last_name='Admin',
            role='admin',
            is_verified=True,
            is_staff=True
        )
        
        # Crear tokens
        self.monitor_token = Token.objects.create(user=self.monitor)
        self.admin_token = Token.objects.create(user=self.admin)
        
        # Configurar cliente API
        self.client = APIClient()
        
        # Crear sala de prueba
        self.room = Room.objects.create(
            name='Sala Test',
            code='ST001',
            capacity=30,
            description='Sala de pruebas'
        )
    
    def test_turn_comparison_endpoint_admin(self):
        """Test del endpoint de comparación de turnos - Admin"""
        # Autenticar como admin
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.admin_token.key}')
        
        # Crear datos de prueba
        hoy = timezone.now().date()
        
        # Crear schedule
        Schedule.objects.create(
            user=self.monitor,
            room=self.room,
            start_datetime=timezone.now().replace(hour=8, minute=0, second=0, microsecond=0),
            end_datetime=timezone.now().replace(hour=12, minute=0, second=0, microsecond=0),
            status=Schedule.ACTIVE,
            created_by=self.admin
        )
        
        # Hacer request
        url = reverse('get_turn_comparison')
        response = self.client.get(url, {
            'date_from': hoy.strftime('%Y-%m-%d'),
            'date_to': hoy.strftime('%Y-%m-%d'),
            'user_id': self.monitor.id
        })
        
        # Verificar respuesta
        if response.status_code != status.HTTP_200_OK:
            print(f"Error response: {response.json()}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertIn('comparaciones', data)
        self.assertIn('total_registros', data)
        self.assertIn('filters_applied', data)
    
    def test_turn_comparison_endpoint_unauthorized(self):
        """Test del endpoint de comparación sin autorización"""
        url = reverse('get_turn_comparison')
        response = self.client.get(url, {
            'date_from': timezone.now().date().strftime('%Y-%m-%d'),
            'date_to': timezone.now().date().strftime('%Y-%m-%d'),
            'user_id': self.monitor.id
        })
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_validate_entry_access_endpoint(self):
        """Test del endpoint de validación de acceso"""
        # Autenticar como monitor
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.monitor_token.key}')
        
        # Crear schedule futuro (para probar acceso anticipado)
        start_time = timezone.now() + timedelta(minutes=5)
        end_time = start_time + timedelta(hours=4)
        
        schedule = Schedule.objects.create(
            user=self.monitor,
            room=self.room,
            start_datetime=start_time,
            end_datetime=end_time,
            status=Schedule.ACTIVE,
            created_by=self.admin
        )
        
        # Verificar que el schedule se creó correctamente
        self.assertIsNotNone(schedule)
        self.assertEqual(schedule.user, self.monitor)
        self.assertEqual(schedule.room, self.room)
        
        # Hacer request
        url = reverse('validate_entry_access')
        response = self.client.post(url, {
            'room_id': self.room.id
        })
        
        # Verificar respuesta
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertIn('permitido', data)
        self.assertIn('mensaje', data)
        self.assertTrue(data['permitido'])  # Debe permitir acceso anticipado
    
    def test_validate_entry_access_no_schedule(self):
        """Test validación de acceso sin schedule asignado"""
        # Autenticar como monitor
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.monitor_token.key}')
        
        # Hacer request sin schedule
        url = reverse('validate_entry_access')
        response = self.client.post(url, {
            'room_id': self.room.id
        })
        
        # Verificar respuesta
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertIn('permitido', data)
        self.assertIn('mensaje', data)
        self.assertFalse(data['permitido'])  # No debe permitir acceso sin schedule
    
    def test_id_statistics_endpoint_admin(self):
        """Test del endpoint de estadísticas de IDs - Solo admin"""
        # Autenticar como admin
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.admin_token.key}')
        
        # Crear algunas entradas para generar estadísticas
        RoomEntry.objects.create(
            user=self.monitor,
            room=self.room,
            entry_time=timezone.now()
        )
        
        # Hacer request
        url = reverse('get_id_statistics')
        response = self.client.get(url)
        
        # Verificar respuesta
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertIn('id_statistics', data)
        self.assertIn('database_info', data)
        self.assertIn('optimization', data)
    
    def test_id_statistics_endpoint_monitor_forbidden(self):
        """Test que monitor no puede acceder a estadísticas de IDs"""
        # Autenticar como monitor
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.monitor_token.key}')
        
        # Hacer request
        url = reverse('get_id_statistics')
        response = self.client.get(url)
        
        # Verificar que está prohibido
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_turn_comparison_with_real_data(self):
        """Test de comparación con datos reales de turnos y registros"""
        # Autenticar como admin
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.admin_token.key}')
        
        # Configurar datos de prueba
        hoy = timezone.now().date()
        inicio_turno = timezone.now().replace(hour=8, minute=0, second=0, microsecond=0)
        fin_turno = inicio_turno + timedelta(hours=4)
        
        # Crear schedule
        Schedule.objects.create(
            user=self.monitor,
            room=self.room,
            start_datetime=inicio_turno,
            end_datetime=fin_turno,
            status=Schedule.ACTIVE,
            created_by=self.admin
        )
        
        # Crear entrada (10 minutos tarde)
        RoomEntry.objects.create(
            user=self.monitor,
            room=self.room,
            entry_time=inicio_turno + timedelta(minutes=10),
            exit_time=fin_turno - timedelta(minutes=5)
        )
        
        # Hacer request
        url = reverse('get_turn_comparison')
        response = self.client.get(url, {
            'date_from': hoy.strftime('%Y-%m-%d'),
            'date_to': hoy.strftime('%Y-%m-%d'),
            'user_id': self.monitor.id
        })
        
        # Verificar que hay datos
        if response.status_code != status.HTTP_200_OK:
            print(f"Error response detailed: {response.json()}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        
        # Verificar que hay comparaciones
        self.assertGreater(len(data['comparaciones']), 0)
        
        # Verificar estructura de comparación
        comparacion = data['comparaciones'][0]
        self.assertIn('usuario', comparacion)
        self.assertIn('turno', comparacion)
        self.assertIn('diferencia', comparacion)
        self.assertIn('estado', comparacion)
    
    def test_validate_entry_missing_room_id(self):
        """Test validación con room_id faltante"""
        # Autenticar como monitor
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.monitor_token.key}')
        
        # Hacer request sin room_id
        url = reverse('validate_entry_access')
        response = self.client.post(url, {})
        
        # Debe retornar error
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class NewModelsMethodsTest(TestCase):
    """Tests para los nuevos métodos agregados a los modelos"""
    
    def setUp(self):
        """Configuración inicial"""
        self.user = User.objects.create_user(
            username='test_user',
            identification='111222333',
            email='test@test.com',
            password='test123',
            first_name='Test',
            last_name='User',
            role='monitor',
            is_verified=True
        )
        
        self.room = Room.objects.create(
            name='Test Room',
            code='TR001',
            capacity=20
        )
    
    def test_room_entry_create_with_reused_id(self):
        """Test del método create_with_reused_id"""
        # Crear entrada usando el método nuevo
        entry = RoomEntry.create_with_reused_id(
            user=self.user,
            room=self.room,
            entry_time=timezone.now()
        )
        
        # Verificar que se creó correctamente
        self.assertIsNotNone(entry)
        self.assertIsNotNone(entry.id)
        self.assertEqual(entry.user, self.user)
        self.assertEqual(entry.room, self.room)
    
    def test_room_entry_get_id_statistics(self):
        """Test del método get_id_statistics"""
        # Crear algunas entradas
        entry1 = RoomEntry.objects.create(
            user=self.user,
            room=self.room,
            entry_time=timezone.now()
        )
        
        entry2 = RoomEntry.objects.create(
            user=self.user,
            room=self.room,
            entry_time=timezone.now()
        )
        
        # Obtener estadísticas
        stats = RoomEntry.get_id_statistics()
        
        # Verificar estructura
        self.assertIsInstance(stats, dict)
        self.assertIn('total_records', stats)
        self.assertIn('efficiency', stats)
        self.assertIn('reusable_ids', stats)
        
        # Verificar valores
        self.assertGreaterEqual(stats['total_records'], 2)