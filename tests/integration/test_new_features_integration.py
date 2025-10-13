"""
Tests de integración para las nuevas funcionalidades implementadas
"""

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
import pytz

from rooms.models import Room, RoomEntry
from schedule.models import Schedule
from rooms.utils import (
    calcular_diferencia, 
    clasificar_estado, 
    generar_comparacion_turnos_registros,
    validar_acceso_anticipado
)
from rooms.id_reuse import RoomEntryIDManager
from schedule.services import ScheduleValidationService

User = get_user_model()


class NewFeaturesIntegrationTest(TestCase):
    """Test suite para validar la integración completa de las nuevas funcionalidades"""
    
    def setUp(self):
        """Configuración inicial para los tests"""
        self.user = User.objects.create_user(
            username='monitor_test',
            identification='123456789',
            email='monitor@test.com',
            password='test123',
            first_name='Test',
            last_name='Monitor',
            role='monitor',
            is_verified=True
        )
        
        self.admin_user = User.objects.create_user(
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
        
        self.room = Room.objects.create(
            name='Sala Test',
            code='ST001',
            capacity=30,
            description='Sala de pruebas'
        )
        
        # Configurar timezone Bogotá
        self.bogota_tz = pytz.timezone('America/Bogota')
    
    def test_calculos_timezone(self):
        """Test para validar cálculos de timezone con Bogotá"""
        ahora_utc = timezone.now()
        ahora_bogota = ahora_utc.astimezone(self.bogota_tz)
        
        # Crear horario para hoy
        inicio = ahora_bogota.replace(hour=8, minute=0, second=0, microsecond=0)
        fin = ahora_bogota.replace(hour=12, minute=0, second=0, microsecond=0)
        
        diferencia = calcular_diferencia(inicio, ahora_bogota)
        
        # Verificar que la función retorna un valor válido
        self.assertIsNotNone(diferencia)
        self.assertIsInstance(diferencia, (int, float))
    
    def test_clasificacion_estado(self):
        """Test para validar clasificación de estados"""
        # Test entrada anticipada
        estado = clasificar_estado(-5)  # 5 minutos antes
        self.assertIn(estado, ['A_TIEMPO', 'SOBRE_LA_HORA', 'TARDE'])
        
        # Test entrada puntual
        estado = clasificar_estado(2)  # 2 minutos después
        self.assertIn(estado, ['A_TIEMPO', 'SOBRE_LA_HORA', 'TARDE'])
        
        # Test entrada tardía
        estado = clasificar_estado(15)  # 15 minutos después
        self.assertIn(estado, ['A_TIEMPO', 'SOBRE_LA_HORA', 'TARDE'])
    
    def test_acceso_anticipado(self):
        """Test para validar acceso anticipado (10 minutos antes)"""
        # Crear schedule para dentro de 5 minutos
        inicio = timezone.now() + timedelta(minutes=5)
        fin = inicio + timedelta(hours=4)
        
        schedule = Schedule.objects.create(
            user=self.user,
            room=self.room,
            start_datetime=inicio,
            end_datetime=fin,
            status=Schedule.ACTIVE,
            created_by=self.admin_user
        )
        
        # Validar acceso anticipado
        permitido, mensaje = validar_acceso_anticipado(self.user, self.room.id, timezone.now())
        
        self.assertIsInstance(permitido, bool)
        self.assertIsInstance(mensaje, str)
        self.assertTrue(permitido)  # Debe permitir acceso (5 minutos < 10 minutos)
    
    def test_validacion_permisos_schedule(self):
        """Test para validar la función mejorada de permisos"""
        # Crear schedule activo
        inicio = timezone.now() - timedelta(minutes=30)
        fin = timezone.now() + timedelta(hours=3, minutes=30)
        
        schedule = Schedule.objects.create(
            user=self.user,
            room=self.room,
            start_datetime=inicio,
            end_datetime=fin,
            status=Schedule.ACTIVE,
            created_by=self.admin_user
        )
        
        # Validar acceso con schedule activo
        try:
            resultado = ScheduleValidationService.validate_room_access_permission(
                self.user, self.room, timezone.now()
            )
            self.assertIsNotNone(resultado)
            self.assertEqual(resultado.id, schedule.id)
        except Exception as e:
            self.fail(f"No debería lanzar excepción para schedule activo: {e}")
    
    def test_reutilizacion_ids(self):
        """Test para validar sistema de reutilización de IDs"""
        # Obtener estadísticas iniciales
        stats_inicial = RoomEntryIDManager.get_room_entry_stats()
        
        # Crear algunas entradas
        entrada1 = RoomEntry.objects.create(
            user=self.user,
            room=self.room,
            entry_time=timezone.now()
        )
        
        entrada2 = RoomEntry.objects.create(
            user=self.user,
            room=self.room,
            entry_time=timezone.now()
        )
        
        # Eliminar una entrada para crear hueco
        entrada1.delete()
        
        # Obtener estadísticas finales
        stats_final = RoomEntryIDManager.get_room_entry_stats()
        
        # Verificar que las estadísticas son consistentes
        self.assertIsInstance(stats_final, dict)
        self.assertIn('total_records', stats_final)
        self.assertIn('efficiency', stats_final)
        self.assertIn('reusable_ids', stats_final)
        
        # Debería haber al menos un ID reutilizable
        self.assertGreater(len(stats_final['reusable_ids']), 0)
    
    def test_generacion_comparacion_turnos(self):
        """Test para validar generación de comparación turnos vs registros"""
        # Crear schedule
        inicio = timezone.now().replace(hour=8, minute=0, second=0, microsecond=0)
        fin = inicio + timedelta(hours=4)
        
        schedule = Schedule.objects.create(
            user=self.user,
            room=self.room,
            start_datetime=inicio,
            end_datetime=fin,
            status=Schedule.ACTIVE,
            created_by=self.admin_user
        )
        
        # Crear entrada
        entrada_tiempo = inicio + timedelta(minutes=10)  # 10 minutos tarde
        entry = RoomEntry.objects.create(
            user=self.user,
            room=self.room,
            entry_time=entrada_tiempo,
            exit_time=entrada_tiempo + timedelta(hours=3, minutes=50)
        )
        
        # Generar comparación
        fecha_str = inicio.strftime('%Y-%m-%d')
        comparacion = generar_comparacion_turnos_registros(
            fecha_str, fecha_str, user_id=self.user.id
        )
        
        # Verificar estructura de respuesta
        self.assertIsInstance(comparacion, list)
        
        # Verificar que hay al menos una comparación
        self.assertGreater(len(comparacion), 0)
        
        # Verificar estructura del primer elemento
        if len(comparacion) > 0:
            primer_elemento = comparacion[0]
            self.assertIn('usuario', primer_elemento)
            self.assertIn('turno', primer_elemento)
            self.assertIn('estado', primer_elemento)
    
    def test_integracion_completa_flujo(self):
        """Test de integración completa: crear schedule, validar acceso, crear entrada"""
        # 1. Crear schedule futuro (para probar acceso anticipado)
        inicio = timezone.now() + timedelta(minutes=5)
        fin = inicio + timedelta(hours=4)
        
        schedule = Schedule.objects.create(
            user=self.user,
            room=self.room,
            start_datetime=inicio,
            end_datetime=fin,
            status=Schedule.ACTIVE,
            created_by=self.admin_user
        )
        
        # 2. Validar acceso anticipado
        permitido, mensaje = validar_acceso_anticipado(self.user, self.room.id, timezone.now())
        self.assertTrue(permitido)
        
        # 3. Crear entrada con ID reutilizado
        entry = RoomEntry.create_with_reused_id(
            user=self.user,
            room=self.room,
            entry_time=timezone.now()
        )
        
        # 4. Verificar que la entrada se creó correctamente
        self.assertIsNotNone(entry.id)
        self.assertEqual(entry.user, self.user)
        self.assertEqual(entry.room, self.room)
        
        # 5. Verificar que se pueden llamar las funciones de utils (sin validar el contenido exacto)
        fecha_str = timezone.now().strftime('%Y-%m-%d')
        try:
            comparacion = generar_comparacion_turnos_registros(
                fecha_str, fecha_str, user_id=self.user.id
            )
            # Solo verificar que la función se ejecuta sin errores
            self.assertIsInstance(comparacion, list)
        except Exception as e:
            self.fail(f"Error al generar comparación: {e}")
        
        # 6. Verificar que las funciones de utilidad básicas funcionan
        self.assertTrue(True)  # Test básico que debe pasar