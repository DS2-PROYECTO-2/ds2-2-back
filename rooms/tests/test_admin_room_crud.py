from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from rest_framework.authtoken.models import Token
from django.contrib.auth import get_user_model
from rooms.models import Room, RoomEntry
from django.utils import timezone
from datetime import timedelta

User = get_user_model()


class RoomAdminCRUDTestCase(TestCase):
    """
    Test case para los endpoints CRUD de salas para administradores
    """
    
    def setUp(self):
        """Configurar datos de prueba"""
        self.client = APIClient()
        
        # Crear usuarios de prueba
        self.admin = User.objects.create_user(
            username='admin_test',
            email='admin@test.com',
            identification='111111111',
            password='testpass123',
            first_name='Admin',
            last_name='Test',
            role='admin',
            is_verified=True
        )
        
        self.monitor = User.objects.create_user(
            username='monitor_test',
            email='monitor@test.com',
            identification='222222222',
            password='testpass123',
            first_name='Monitor',
            last_name='Test',
            role='monitor',
            is_verified=True
        )
        
        # Crear tokens
        self.admin_token = Token.objects.create(user=self.admin)
        self.monitor_token = Token.objects.create(user=self.monitor)
        
        # Crear salas de prueba
        self.room1 = Room.objects.create(
            name='Sala Test 1',
            code='ST001',
            capacity=20,
            description='Sala de prueba 1'
        )
        
        self.room2 = Room.objects.create(
            name='Sala Test 2',
            code='ST002',
            capacity=30,
            description='Sala de prueba 2'
        )
    
    def test_admin_create_room_success(self):
        """Test: Admin puede crear una sala exitosamente"""
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.admin_token.key)
        
        url = reverse('admin_room_create')
        data = {
            'name': 'Nueva Sala Admin',
            'code': 'NSA001',
            'capacity': 25,
            'description': 'Sala creada por admin'
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('message', response.data)
        self.assertIn('room', response.data)
        self.assertEqual(response.data['room']['name'], 'Nueva Sala Admin')
        self.assertEqual(response.data['room']['code'], 'NSA001')
        
        # Verificar que se creó en la base de datos
        self.assertTrue(Room.objects.filter(code='NSA001').exists())
    
    def test_monitor_cannot_create_room(self):
        """Test: Monitor no puede crear salas"""
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.monitor_token.key)
        
        url = reverse('admin_room_create')
        data = {
            'name': 'Sala No Permitida',
            'code': 'SNP001',
            'capacity': 25
        }
        
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_admin_create_room_duplicate_code(self):
        """Test: No se puede crear sala con código duplicado"""
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.admin_token.key)
        
        url = reverse('admin_room_create')
        data = {
            'name': 'Sala Duplicada',
            'code': 'ST001',  # Código ya existente
            'capacity': 25
        }
        
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('details', response.data)
        self.assertIn('code', response.data['details'])
    
    def test_admin_update_room_success(self):
        """Test: Admin puede actualizar una sala exitosamente"""
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.admin_token.key)
        
        url = reverse('admin_room_update', kwargs={'room_id': self.room1.id})
        data = {
            'name': 'Sala Actualizada',
            'capacity': 35,
            'description': 'Descripción actualizada'
        }
        
        response = self.client.patch(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('message', response.data)
        self.assertEqual(response.data['room']['name'], 'Sala Actualizada')
        self.assertEqual(response.data['room']['capacity'], 35)
        
        # Verificar en base de datos
        self.room1.refresh_from_db()
        self.assertEqual(self.room1.name, 'Sala Actualizada')
        self.assertEqual(self.room1.capacity, 35)
    
    def test_admin_cannot_deactivate_room_with_occupants(self):
        """Test: No se puede desactivar sala con ocupantes activos"""
        # Crear entrada activa
        RoomEntry.objects.create(
            user=self.monitor,
            room=self.room1
        )
        
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.admin_token.key)
        
        url = reverse('admin_room_update', kwargs={'room_id': self.room1.id})
        data = {'is_active': False}
        
        response = self.client.patch(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
        self.assertIn('ocupantes activos', response.data['error'])
    
    def test_admin_delete_room_soft_delete(self):
        """Test: Sala con historial se marca como eliminada (soft delete)"""
        # Crear entrada completada para generar historial
        entry = RoomEntry.objects.create(
            user=self.monitor,
            room=self.room1
        )
        entry.entry_time = timezone.now() - timedelta(hours=2)
        entry.exit_time = timezone.now() - timedelta(hours=1)
        entry.save()
        
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.admin_token.key)
        
        url = reverse('admin_room_delete', kwargs={'room_id': self.room1.id})
        response = self.client.delete(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('message', response.data)
        self.assertEqual(response.data['action'], 'soft_delete')
        
        # Verificar soft delete
        self.room1.refresh_from_db()
        self.assertFalse(self.room1.is_active)
        self.assertIn('ELIMINADA', self.room1.name)
    
    def test_admin_delete_room_hard_delete(self):
        """Test: Sala sin historial se elimina completamente (hard delete)"""
        # Crear sala sin historial
        empty_room = Room.objects.create(
            name='Sala Vacía',
            code='SV001',
            capacity=10
        )
        
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.admin_token.key)
        
        url = reverse('admin_room_delete', kwargs={'room_id': empty_room.id})
        response = self.client.delete(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['action'], 'hard_delete')
        
        # Verificar hard delete
        self.assertFalse(Room.objects.filter(id=empty_room.id).exists())
    
    def test_admin_cannot_delete_room_with_active_occupants(self):
        """Test: No se puede eliminar sala con ocupantes activos"""
        # Crear entrada activa
        RoomEntry.objects.create(
            user=self.monitor,
            room=self.room1
        )
        
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.admin_token.key)
        
        url = reverse('admin_room_delete', kwargs={'room_id': self.room1.id})
        response = self.client.delete(url)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('ocupantes activos', response.data['error'])
    
    def test_admin_rooms_list_success(self):
        """Test: Admin puede listar todas las salas"""
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.admin_token.key)
        
        url = reverse('admin_rooms_list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('count', response.data)
        self.assertIn('rooms', response.data)
        self.assertEqual(response.data['count'], 2)  # room1 y room2
    
    def test_admin_rooms_list_with_search(self):
        """Test: Admin puede buscar salas por nombre/código"""
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.admin_token.key)
        
        url = reverse('admin_rooms_list')
        response = self.client.get(url, {'search': 'Test 1'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['rooms'][0]['name'], 'Sala Test 1')
    
    def test_admin_rooms_list_include_inactive(self):
        """Test: Admin puede incluir salas inactivas en la lista"""
        # Desactivar una sala
        self.room2.is_active = False
        self.room2.save()
        
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.admin_token.key)
        
        # Sin incluir inactivas
        url = reverse('admin_rooms_list')
        response = self.client.get(url)
        self.assertEqual(response.data['count'], 1)  # Solo activas
        
        # Incluyendo inactivas
        response = self.client.get(url, {'include_inactive': 'true'})
        self.assertEqual(response.data['count'], 2)  # Todas
    
    def test_admin_room_detail_success(self):
        """Test: Admin puede ver detalles completos de una sala"""
        # Crear algunas entradas para estadísticas
        entry1 = RoomEntry.objects.create(user=self.monitor, room=self.room1)
        entry1.entry_time = timezone.now() - timedelta(hours=3)
        entry1.exit_time = timezone.now() - timedelta(hours=1)  # 2 horas
        entry1.save()
        
        # Entrada activa
        RoomEntry.objects.create(user=self.monitor, room=self.room1)
        
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.admin_token.key)
        
        url = reverse('admin_room_detail', kwargs={'room_id': self.room1.id})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('room', response.data)
        self.assertIn('statistics', response.data)
        
        stats = response.data['statistics']
        self.assertEqual(stats['current_occupants'], 1)
        self.assertEqual(stats['total_entries_historical'], 2)
        self.assertGreater(stats['total_hours_usage'], 0)
        self.assertEqual(len(stats['active_entries']), 1)
    
    def test_monitor_cannot_access_admin_endpoints(self):
        """Test: Monitor no puede acceder a ningún endpoint de admin"""
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.monitor_token.key)
        
        # Probar todos los endpoints de admin
        admin_urls = [
            reverse('admin_rooms_list'),
            reverse('admin_room_create'),
            reverse('admin_room_detail', kwargs={'room_id': self.room1.id}),
            reverse('admin_room_update', kwargs={'room_id': self.room1.id}),
            reverse('admin_room_delete', kwargs={'room_id': self.room1.id}),
        ]
        
        for url in admin_urls:
            for method in ['get', 'post', 'put', 'patch', 'delete']:
                if hasattr(self.client, method):
                    response = getattr(self.client, method)(url, {})
                    self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_unauthenticated_cannot_access_admin_endpoints(self):
        """Test: Usuario no autenticado no puede acceder a endpoints de admin"""
        # Sin credenciales
        admin_urls = [
            reverse('admin_rooms_list'),
            reverse('admin_room_create'),
            reverse('admin_room_detail', kwargs={'room_id': self.room1.id}),
            reverse('admin_room_update', kwargs={'room_id': self.room1.id}),
            reverse('admin_room_delete', kwargs={'room_id': self.room1.id}),
        ]
        
        for url in admin_urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_room_serializer_includes_occupants_count(self):
        """Test: El serializer de Room incluye el conteo de ocupantes"""
        # Crear entradas activas
        RoomEntry.objects.create(user=self.monitor, room=self.room1)
        
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.admin_token.key)
        
        url = reverse('admin_rooms_list')
        response = self.client.get(url)
        
        room_data = next(room for room in response.data['rooms'] if room['id'] == self.room1.id)
        self.assertIn('occupants_count', room_data)
        self.assertEqual(room_data['occupants_count'], 1)