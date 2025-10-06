from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APITestCase
from rest_framework import status
from rest_framework.authtoken.models import Token
from datetime import timedelta
from rooms.models import Room, RoomEntry

User = get_user_model()


class RoomEntryModelTest(TestCase):
    """
    Tests para el modelo RoomEntry
    Tarea 1: Backend: Modelo y endpoints para Registro de ingreso/salida en sala
    """
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testmonitor',
            identification='123456789',
            email='monitor@test.com',
            password='testpass123',
            first_name='Test',
            last_name='Monitor',
            role='monitor',
            is_verified=True
        )
        self.room = Room.objects.create(
            name='Sala de Estudio 1',
            code='S101',
            capacity=20,
            description='Sala principal de estudio'
        )

    def test_room_entry_creation(self):
        """Test: Crear entrada a sala registra fecha y hora exacta"""
        entry = RoomEntry.objects.create(
            user=self.user,
            room=self.room,
            notes='Inicio de turno'
        )
        
        self.assertEqual(entry.user, self.user)
        self.assertEqual(entry.room, self.room)
        self.assertIsNotNone(entry.entry_time)
        self.assertIsNone(entry.exit_time)
        self.assertTrue(entry.is_active)
        self.assertEqual(entry.notes, 'Inicio de turno')

    def test_room_entry_duration_calculation(self):
        """Test: Cálculo correcto de duración de permanencia"""
        entry = RoomEntry.objects.create(
            user=self.user,
            room=self.room
        )
        
        # Simular salida después de 2 horas y 30 minutos
        entry.exit_time = entry.entry_time + timedelta(hours=2, minutes=30)
        entry.save()
        
        self.assertEqual(entry.duration_hours, 2.5)
        self.assertEqual(entry.duration_minutes, 150)
        self.assertEqual(entry.get_duration_formatted(), '2h 30m')
        self.assertFalse(entry.is_active)

    def test_room_entry_duration_only_minutes(self):
        """Test: Formato de duración solo en minutos"""
        entry = RoomEntry.objects.create(
            user=self.user,
            room=self.room
        )
        
        # Simular salida después de 45 minutos
        entry.exit_time = entry.entry_time + timedelta(minutes=45)
        entry.save()
        
        self.assertEqual(entry.duration_minutes, 45)
        self.assertEqual(entry.get_duration_formatted(), '45m')

    def test_room_entry_active_duration_format(self):
        """Test: Formato de duración para entradas activas"""
        entry = RoomEntry.objects.create(
            user=self.user,
            room=self.room
        )
        
        self.assertEqual(entry.get_duration_formatted(), 'En curso')
        self.assertIsNone(entry.duration_hours)
        self.assertIsNone(entry.duration_minutes)

    def test_room_entry_string_representation(self):
        """Test: Representación string del modelo"""
        entry = RoomEntry.objects.create(
            user=self.user,
            room=self.room
        )
        
        expected = f"{self.user} - {self.room} - {entry.entry_time.strftime('%d/%m/%Y %H:%M')}"
        self.assertEqual(str(entry), expected)


class RoomEntryAPITest(APITestCase):
    """
    Tests para los endpoints de RoomEntry
    Tarea 1: Backend: Modelo y endpoints para Registro de ingreso/salida en sala
    """
    
    def setUp(self):
        # Crear usuario monitor
        self.monitor = User.objects.create_user(
            username='testmonitor',
            identification='123456789',
            email='monitor@test.com',
            password='testpass123',
            first_name='Test',
            last_name='Monitor',
            role='monitor',
            is_verified=True
        )
        self.monitor_token = Token.objects.create(user=self.monitor)
        
        # Crear usuario admin
        self.admin = User.objects.create_user(
            username='testadmin',
            identification='987654321',
            email='admin@test.com',
            password='adminpass123',
            first_name='Test',
            last_name='Admin',
            role='admin',
            is_verified=True
        )
        self.admin_token = Token.objects.create(user=self.admin)
        
        # Crear salas de prueba
        self.room1 = Room.objects.create(
            name='Sala de Estudio 1',
            code='S101',
            capacity=20
        )
        self.room2 = Room.objects.create(
            name='Sala de Estudio 2', 
            code='S102',
            capacity=15
        )

    def test_create_room_entry_success(self):
        """Test: Crear entrada a sala exitosamente"""
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.monitor_token.key)
        
        url = reverse('room_entry_create')
        data = {
            'room': self.room1.id,
            'notes': 'Inicio de turno matutino'
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('message', response.data)
        self.assertIn('entry', response.data)
        self.assertEqual(response.data['entry']['room'], self.room1.id)
        self.assertEqual(response.data['entry']['user'], self.monitor.id)
        self.assertEqual(response.data['entry']['notes'], 'Inicio de turno matutino')
        self.assertIsNone(response.data['entry']['exit_time'])
        self.assertTrue(response.data['entry']['is_active'])
        
        # Verificar que se creó en la base de datos
        self.assertEqual(RoomEntry.objects.count(), 1)

    def test_create_room_entry_unauthorized(self):
        """Test: Crear entrada sin autenticación falla"""
        url = reverse('room_entry_create')
        data = {'room': self.room1.id}
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_room_entry_invalid_room(self):
        """Test: Crear entrada con sala inválida falla"""
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.monitor_token.key)
        
        url = reverse('room_entry_create')
        data = {'room': 999}  # Sala que no existe
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_exit_room_entry_success(self):
        """Test: Registrar salida exitosamente"""
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.monitor_token.key)
        
        # Crear entrada primero
        entry = RoomEntry.objects.create(
            user=self.monitor,
            room=self.room1,
            notes='Entrada inicial'
        )
        
        url = reverse('room_entry_exit', kwargs={'entry_id': entry.id})
        data = {'notes': 'Fin de turno'}
        
        response = self.client.patch(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('message', response.data)
        self.assertIn('entry', response.data)
        
        # Verificar que se registró la salida
        entry.refresh_from_db()
        self.assertIsNotNone(entry.exit_time)
        self.assertFalse(entry.is_active)

    def test_exit_room_entry_not_found(self):
        """Test: Registrar salida de entrada inexistente falla"""
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.monitor_token.key)
        
        url = reverse('room_entry_exit', kwargs={'entry_id': 999})
        
        response = self.client.patch(url, {}, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_exit_room_entry_different_user(self):
        """Test: Registrar salida de entrada de otro usuario falla"""
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.monitor_token.key)
        
        # Crear entrada con otro usuario
        entry = RoomEntry.objects.create(
            user=self.admin,
            room=self.room1
        )
        
        url = reverse('room_entry_exit', kwargs={'entry_id': entry.id})
        
        response = self.client.patch(url, {}, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_user_room_entries_list(self):
        """Test: Listar historial de entradas del usuario"""
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.monitor_token.key)
        
        # Crear múltiples entradas
        entry1 = RoomEntry.objects.create(
            user=self.monitor,
            room=self.room1,
            notes='Primera entrada'
        )
        entry2 = RoomEntry.objects.create(
            user=self.monitor,
            room=self.room2,
            notes='Segunda entrada'
        )
        # Entrada de otro usuario (no debe aparecer)
        RoomEntry.objects.create(
            user=self.admin,
            room=self.room1
        )
        
        url = reverse('user_room_entries')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 2)
        self.assertEqual(len(response.data['entries']), 2)
        
        # Verificar que solo aparecen las entradas del usuario autenticado
        entry_ids = [entry['id'] for entry in response.data['entries']]
        self.assertIn(entry1.id, entry_ids)
        self.assertIn(entry2.id, entry_ids)

    def test_user_active_entry_exists(self):
        """Test: Obtener entrada activa cuando existe"""
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.monitor_token.key)
        
        # Crear entrada activa
        active_entry = RoomEntry.objects.create(
            user=self.monitor,
            room=self.room1
        )
        
        url = reverse('user_active_entry')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['has_active_entry'])
        self.assertIsNotNone(response.data['active_entry'])
        self.assertEqual(response.data['active_entry']['id'], active_entry.id)

    def test_user_active_entry_not_exists(self):
        """Test: Obtener entrada activa cuando no existe"""
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.monitor_token.key)
        
        url = reverse('user_active_entry')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(response.data['has_active_entry'])
        self.assertIsNone(response.data['active_entry'])

    def test_room_current_occupants(self):
        """Test: Obtener ocupantes actuales de una sala"""
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.monitor_token.key)
        
        # Crear entradas activas en la sala
        entry1 = RoomEntry.objects.create(
            user=self.monitor,
            room=self.room1
        )
        entry2 = RoomEntry.objects.create(
            user=self.admin,
            room=self.room1
        )
        # Crear entrada en otra sala (no debe aparecer)
        RoomEntry.objects.create(
            user=self.monitor,
            room=self.room2
        )
        
        url = reverse('room_occupants', kwargs={'room_id': self.room1.id})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['current_occupants'], 2)
        self.assertIn('room', response.data)
        self.assertEqual(response.data['room']['id'], self.room1.id)
        self.assertEqual(len(response.data['entries']), 2)

    def test_room_occupants_invalid_room(self):
        """Test: Obtener ocupantes de sala inexistente falla"""
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.monitor_token.key)
        
        url = reverse('room_occupants', kwargs={'room_id': 999})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class RoomEntrySerializerTest(TestCase):
    """
    Tests para los serializadores de RoomEntry
    """
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            identification='123456789',
            email='test@test.com',
            password='testpass123',
            first_name='Test',
            last_name='User',
            role='monitor',
            is_verified=True
        )
        self.room = Room.objects.create(
            name='Sala Test',
            code='ST01',
            capacity=10
        )

    def test_room_entry_serializer_data(self):
        """Test: Serialización correcta de datos de RoomEntry"""
        from rooms.serializers import RoomEntrySerializer
        
        entry = RoomEntry.objects.create(
            user=self.user,
            room=self.room,
            notes='Test entry'
        )
        
        serializer = RoomEntrySerializer(entry)
        data = serializer.data
        
        self.assertEqual(data['id'], entry.id)
        self.assertEqual(data['user'], self.user.id)
        self.assertEqual(data['room'], self.room.id)
        self.assertEqual(data['user_name'], 'Test User')
        self.assertEqual(data['user_username'], 'testuser')
        self.assertEqual(data['room_name'], 'Sala Test')
        self.assertEqual(data['room_code'], 'ST01')
        self.assertEqual(data['notes'], 'Test entry')
        self.assertTrue(data['is_active'])
        self.assertEqual(data['duration_formatted'], 'En curso')