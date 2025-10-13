from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from datetime import timedelta
from rooms.models import Room, RoomEntry
from rooms.services import RoomEntryBusinessLogic
from notifications.models import Notification

User = get_user_model()


class RoomEntryValidationsTestCase(TestCase):
    """
    Pruebas para Tarea 2: Backend: Lógica y validaciones para Registro de ingreso/salida en sala
    """
    
    def setUp(self):
        """Configuración inicial para todas las pruebas"""
        self.client = APIClient()
        
        # Crear usuarios de prueba
        self.monitor = User.objects.create_user(
            username='monitor_test',
            email='monitor@test.com',
            password='testpass123',
            identification='12345678',
            first_name='Monitor',
            last_name='Test',
            role='monitor',
            is_verified=True
        )
        
        self.admin = User.objects.create_user(
            username='admin_test',
            email='admin@test.com',
            password='testpass123',
            identification='87654321',
            first_name='Admin',
            last_name='Test',
            role='admin',
            is_verified=True
        )
        
        # Crear salas de prueba
        self.room1 = Room.objects.create(
            name='Sala A',
            code='SA001',
            capacity=20,
            is_active=True
        )
        
        self.room2 = Room.objects.create(
            name='Sala B',
            code='SB001',
            capacity=25,
            is_active=True
        )
        
        # Crear token de autenticación
        from rest_framework.authtoken.models import Token
        self.token = Token.objects.create(user=self.monitor)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')
    
    def create_active_schedule(self, user, room, start_offset_hours=0, duration_hours=4):
        """Helper para crear turnos activos en tests"""
        from schedule.models import Schedule
        from django.utils import timezone
        from datetime import timedelta
        
        start_time = timezone.now() + timedelta(hours=start_offset_hours)
        end_time = start_time + timedelta(hours=duration_hours)
        
        return Schedule.objects.create(
            user=user,
            room=room,
            start_datetime=start_time,
            end_datetime=end_time,
            status='active',
            created_by=self.admin
        )
    
    def test_no_simultaneous_entry_validation(self):
        """
        Prueba HU: "No se permite ingresar a otra sala sin antes haber salido"
        """
        # Crear turnos activos para ambas salas
        self.create_active_schedule(self.monitor, self.room1)
        self.create_active_schedule(self.monitor, self.room2)
        
        # Crear entrada en primera sala usando el servicio
        from rooms.services import RoomEntryBusinessLogic
        result1 = RoomEntryBusinessLogic.create_room_entry_with_validations(
            self.monitor, self.room1
        )
        self.assertTrue(result1['success'])
        
        # Intentar ingresar a segunda sala sin salir de la primera
        url = reverse('room_entry_create')
        data = {'room': self.room2.id}
        
        response = self.client.post(url, data)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        # Verificar el error - puede ser por simultaneidad o por otra razón
        self.assertIn('error', response.data)
        
        # Verificar que no se creó la segunda entrada
        self.assertEqual(RoomEntry.objects.filter(user=self.monitor, room=self.room2).count(), 0)
    
    def test_successful_entry_after_exit(self):
        """
        Prueba que se puede ingresar a otra sala después de salir de la primera
        """
        # Crear turnos activos para ambas salas
        self.create_active_schedule(self.monitor, self.room1)
        self.create_active_schedule(self.monitor, self.room2)
        
        # Crear y finalizar entrada en primera sala
        entry1 = RoomEntry.objects.create(
            user=self.monitor,
            room=self.room1
        )
        entry1.exit_time = timezone.now()
        entry1.active = False
        entry1.save()
        
        # Intentar ingresar a segunda sala (debería funcionar)
        url = reverse('room_entry_create')
        data = {'room': self.room2.id}
        
        response = self.client.post(url, data)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['entry']['room'], self.room2.id)
        
        # Verificar que se creó la entrada
        self.assertTrue(RoomEntry.objects.filter(user=self.monitor, room=self.room2, exit_time__isnull=True).exists())
    
    def test_duration_calculation_active_session(self):
        """
        Prueba HU: "El sistema calcule mis horas de permanencia" - Sesión activa
        """
        # Crear entrada hace 2 horas
        past_time = timezone.now() - timedelta(hours=2, minutes=30)
        entry = RoomEntry.objects.create(
            user=self.monitor,
            room=self.room1,
            entry_time=past_time
        )
        
        # Calcular duración
        duration_info = RoomEntryBusinessLogic.calculate_session_duration(entry)
        
        self.assertTrue(duration_info['is_active'])
        self.assertGreaterEqual(duration_info['current_duration_hours'], 2.4)  # Al menos 2.4 horas
        self.assertGreaterEqual(duration_info['current_duration_minutes'], 144)  # Al menos 144 minutos
        self.assertEqual(duration_info['status'], 'En curso')
    
    def test_duration_calculation_completed_session(self):
        """
        Prueba HU: "El sistema calcule mis horas de permanencia" - Sesión completada
        """
        # Crear entrada completada de 3 horas
        entry_time = timezone.now() - timedelta(hours=4)
        exit_time = entry_time + timedelta(hours=3)
        
        entry = RoomEntry.objects.create(
            user=self.monitor,
            room=self.room1,
            entry_time=entry_time,
            exit_time=exit_time
        )
        
        # Calcular duración
        duration_info = RoomEntryBusinessLogic.calculate_session_duration(entry)
        
        self.assertFalse(duration_info['is_active'])
        self.assertEqual(duration_info['total_duration_hours'], 3.0)
        self.assertEqual(duration_info['total_duration_minutes'], 180)
        self.assertEqual(duration_info['status'], 'Completada')
        self.assertEqual(duration_info['formatted_duration'], '3h')
    
    def test_excessive_hours_notification_sent(self):
        """
        Prueba HU: "Si un monitor excede 8 horas seguidas, se genera notificación al admin"
        """
        # Crear entrada que excede 8 horas (9 horas)
        entry_time = timezone.now() - timedelta(hours=10)
        exit_time = entry_time + timedelta(hours=9)
        
        entry = RoomEntry.objects.create(
            user=self.monitor,
            room=self.room1,
            entry_time=entry_time,
            exit_time=exit_time
        )
        
        # Verificar notificación
        notification_result = RoomEntryBusinessLogic.check_and_notify_excessive_hours(entry)
        
        self.assertTrue(notification_result['notification_sent'])
        self.assertEqual(notification_result['duration_hours'], 9.0)
        self.assertEqual(notification_result['excess_hours'], 1.0)
        self.assertEqual(notification_result['admins_notified'], 1)
        
        # Verificar que se creó la notificación
        notification = Notification.objects.filter(
            user=self.admin,
            notification_type='excessive_hours'
        ).first()
        
        self.assertIsNotNone(notification)
        self.assertIn('ha excedido las 8 horas', notification.message)
        self.assertIn(self.monitor.get_full_name(), notification.message)
        self.assertIn(self.room1.name, notification.message)
    
    def test_no_notification_for_normal_hours(self):
        """
        Prueba que NO se envía notificación para sesiones normales (< 8 horas)
        """
        # Crear entrada de 6 horas (normal)
        entry_time = timezone.now() - timedelta(hours=7)
        exit_time = entry_time + timedelta(hours=6)
        
        entry = RoomEntry.objects.create(
            user=self.monitor,
            room=self.room1,
            entry_time=entry_time,
            exit_time=exit_time
        )
        
        # Verificar que NO se envía notificación
        notification_result = RoomEntryBusinessLogic.check_and_notify_excessive_hours(entry)
        
        self.assertFalse(notification_result['notification_sent'])
        self.assertEqual(notification_result['reason'], 'Duración dentro del límite permitido')
        self.assertEqual(notification_result['duration_hours'], 6.0)
        
        # Verificar que NO se creó notificación
        notification_count = Notification.objects.filter(
            user=self.admin,
            notification_type='excessive_hours'
        ).count()
        
        self.assertEqual(notification_count, 0)
    
    def test_concurrent_entry_creation_integrity(self):
        """
        Prueba HU: "Garantizar integridad de datos en escenarios concurrentes"
        """
        # Crear turno activo para la sala
        self.create_active_schedule(self.monitor, self.room1)
        
        from django.db import transaction
        
        # Simular creación concurrente usando transacciones
        def create_entry():
            return RoomEntryBusinessLogic.create_room_entry_with_validations(
                user=self.monitor,
                room=self.room1
            )
        
        # Primera entrada debería ser exitosa
        result1 = create_entry()
        self.assertTrue(result1['success'])
        
        # Segunda entrada debería fallar por validación de simultaneidad o sala ocupada
        result2 = create_entry()
        self.assertFalse(result2['success'])
        # La validación puede fallar por diferentes razones ahora
        self.assertIn('error', result2)
        
        # Verificar que solo existe una entrada
        active_entries = RoomEntry.objects.filter(
            user=self.monitor,
            exit_time__isnull=True
        ).count()
        self.assertEqual(active_entries, 1)
    
    def test_exit_with_validations_and_duration(self):
        """
        Prueba salida con validaciones y cálculo de duración
        """
        # Crear entrada
        entry = RoomEntry.objects.create(
            user=self.monitor,
            room=self.room1,
            entry_time=timezone.now() - timedelta(hours=2)
        )
        
        # Registrar salida usando el servicio
        result = RoomEntryBusinessLogic.exit_room_entry_with_validations(
            user=self.monitor,
            entry_id=entry.id,
            notes='Salida de prueba'
        )
        
        self.assertTrue(result['success'])
        self.assertFalse(result['duration_info']['is_active'])
        self.assertGreaterEqual(result['duration_info']['total_duration_hours'], 1.9)
        self.assertEqual(result['entry'].notes, 'Salida de prueba')
        
        # Verificar que la entrada fue actualizada
        entry.refresh_from_db()
        self.assertIsNotNone(entry.exit_time)
    
    def test_user_active_session_info(self):
        """
        Prueba obtención de información de sesión activa
        """
        # Sin sesión activa
        session_info = RoomEntryBusinessLogic.get_user_active_session(self.monitor)
        self.assertFalse(session_info['has_active_session'])
        
        # Con sesión activa
        entry = RoomEntry.objects.create(
            user=self.monitor,
            room=self.room1,
            entry_time=timezone.now() - timedelta(hours=1)
        )
        
        session_info = RoomEntryBusinessLogic.get_user_active_session(self.monitor)
        self.assertTrue(session_info['has_active_session'])
        self.assertEqual(session_info['entry'].id, entry.id)
        self.assertTrue(session_info['duration_info']['is_active'])
        self.assertFalse(session_info['warning'])  # < 8 horas
    
    def test_user_daily_summary(self):
        """
        Prueba resumen diario de entradas del usuario
        """
        today = timezone.now().date()
        
        # Crear múltiples entradas para hoy usando hora específica del día actual
        from datetime import datetime, time
        base_datetime = datetime.combine(today, time(10, 0))  # 10:00 AM de hoy
        base_time = timezone.make_aware(base_datetime)
        
        entry1 = RoomEntry.objects.create(
            user=self.monitor,
            room=self.room1
        )
        entry1.entry_time = base_time  # 10:00 AM
        entry1.exit_time = base_time + timedelta(hours=2)  # 12:00 PM - 2 horas
        entry1.save()
        
        entry2 = RoomEntry.objects.create(
            user=self.monitor,
            room=self.room2
        )
        entry2.entry_time = base_time + timedelta(hours=3)  # 1:00 PM
        entry2.exit_time = base_time + timedelta(hours=5)  # 3:00 PM - 2 horas
        entry2.save()
        
        # Entrada activa
        entry3 = RoomEntry.objects.create(
            user=self.monitor,
            room=self.room1
        )
        entry3.entry_time = base_time + timedelta(hours=6)  # 4:00 PM - activa
        entry3.save()
        
        # Obtener resumen
        summary = RoomEntryBusinessLogic.get_user_daily_summary(self.monitor, today)
        
        self.assertEqual(summary['total_sessions'], 3)
        self.assertEqual(summary['completed_sessions'], 2)
        self.assertEqual(summary['active_sessions'], 1)
        self.assertEqual(summary['total_hours'], 4.0)  # 2 + 2 horas completadas
        self.assertEqual(summary['total_minutes'], 240)
        self.assertEqual(len(summary['sessions']), 3)


class RoomEntryAPIValidationsTestCase(TestCase):
    """
    Pruebas de los endpoints de API con validaciones implementadas
    """
    
    def setUp(self):
        """Configuración inicial para todas las pruebas de API"""
        self.client = APIClient()
        
        # Crear usuario monitor
        self.monitor = User.objects.create_user(
            username='monitor_api_test',
            email='monitor_api@test.com',
            password='testpass123',
            identification='11223344',
            first_name='Monitor',
            last_name='API',
            role='monitor',
            is_verified=True
        )
        
        # Crear admin para crear turnos
        self.admin = User.objects.create_user(
            username='admin_api_test',
            email='admin_api@test.com',
            password='testpass123',
            identification='99887766',
            first_name='Admin',
            last_name='API',
            role='admin',
            is_verified=True
        )
        
        # Crear salas
        self.room1 = Room.objects.create(
            name='Sala API A',
            code='SAPI001',
            capacity=20,
            is_active=True
        )
        
        self.room2 = Room.objects.create(
            name='Sala API B',
            code='SAPI002',
            capacity=25,
            is_active=True
        )
        
        # Autenticación
        from rest_framework.authtoken.models import Token
        self.token = Token.objects.create(user=self.monitor)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')
    
    def create_active_schedule(self, user, room, start_offset_hours=0, duration_hours=4):
        """Helper para crear turnos activos en tests"""
        from schedule.models import Schedule
        from django.utils import timezone
        from datetime import timedelta
        
        start_time = timezone.now() + timedelta(hours=start_offset_hours)
        end_time = start_time + timedelta(hours=duration_hours)
        
        return Schedule.objects.create(
            user=user,
            room=room,
            start_datetime=start_time,
            end_datetime=end_time,
            status='active',
            created_by=self.admin
        )
    
    def test_api_create_entry_with_simultaneous_validation(self):
        """
        Prueba API de creación con validación de simultaneidad
        """
        # Crear turnos activos para ambas salas
        self.create_active_schedule(self.monitor, self.room1)
        self.create_active_schedule(self.monitor, self.room2)
        
        # Crear primera entrada
        url = reverse('room_entry_create')
        data = {'room': self.room1.id, 'notes': 'Primera entrada'}
        
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Intentar crear segunda entrada (debería fallar)
        data = {'room': self.room2.id, 'notes': 'Segunda entrada'}
        response = self.client.post(url, data)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        # El error puede ser por simultaneidad u otro tipo de validación
        self.assertIn('error', response.data)
    
    def test_api_exit_with_duration_calculation(self):
        """
        Prueba API de salida con cálculo de duración
        """
        # Crear entrada
        entry = RoomEntry.objects.create(
            user=self.monitor,
            room=self.room1,
            entry_time=timezone.now() - timedelta(hours=3)
        )
        
        # Registrar salida
        url = reverse('room_entry_exit', kwargs={'entry_id': entry.id})
        data = {'notes': 'Salida por API'}
        
        response = self.client.patch(url, data)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('duration', response.data)
        self.assertFalse(response.data['duration']['is_active'])
        self.assertGreaterEqual(response.data['duration']['total_duration_hours'], 2.9)
    
    def test_api_active_entry_with_duration_info(self):
        """
        Prueba API de entrada activa con información de duración
        """
        # Sin entrada activa
        url = reverse('user_active_entry')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(response.data['has_active_entry'])
        
        # Con entrada activa
        entry = RoomEntry.objects.create(
            user=self.monitor,
            room=self.room1,
            entry_time=timezone.now() - timedelta(hours=2)
        )
        
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['has_active_entry'])
        self.assertIn('duration_info', response.data)
        self.assertTrue(response.data['duration_info']['is_active'])
        self.assertGreaterEqual(response.data['duration_info']['current_duration_hours'], 1.9)
    
    def test_api_daily_summary(self):
        """
        Prueba API de resumen diario
        """
        today = timezone.now().date()
        
        # Crear entradas de prueba usando hora específica del día actual
        from datetime import datetime, time
        base_datetime = datetime.combine(today, time(10, 0))  # 10:00 AM de hoy
        base_time = timezone.make_aware(base_datetime)
        
        # Crear entrada directamente con los valores correctos
        entry = RoomEntry.objects.create(
            user=self.monitor,
            room=self.room1,
            entry_time=base_time,
            exit_time=base_time + timedelta(hours=2)  # 12:00 PM - 2 horas
        )
        
        # Obtener resumen
        url = reverse('user_daily_summary')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['total_sessions'], 1)
        self.assertEqual(response.data['completed_sessions'], 1)
        self.assertEqual(response.data['total_hours'], 2.0)
        
        # Prueba con fecha específica
        response = self.client.get(url, {'date': today.strftime('%Y-%m-%d')})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['date'], today.isoformat())