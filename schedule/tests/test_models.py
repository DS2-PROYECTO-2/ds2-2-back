from django.test import TestCase
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import timedelta

from users.models import User
from rooms.models import Room
from schedule.models import Schedule
from .test_base import ScheduleTestBase


class ScheduleModelTestCase(ScheduleTestBase):
    """
    Tests para el modelo Schedule
    """
    
    def test_schedule_creation_success(self):
        """Test de creación exitosa de un turno"""
        schedule = Schedule.objects.create(
            user=self.monitor_user,
            room=self.room1,
            start_datetime=self.future_date,
            end_datetime=self.future_date + timedelta(hours=4),
            created_by=self.admin_user,
            notes='Turno de prueba'
        )
        
        self.assertEqual(schedule.user, self.monitor_user)
        self.assertEqual(schedule.room, self.room1)
        self.assertEqual(schedule.status, Schedule.ACTIVE)
        self.assertEqual(schedule.duration_hours, 4.0)
        self.assertTrue(schedule.is_active)
        self.assertFalse(schedule.is_current)
    
    def test_schedule_validation_end_before_start(self):
        """Test de validación: fecha fin antes que fecha inicio"""
        with self.assertRaises(ValidationError):
            schedule = Schedule(
                user=self.monitor_user,
                room=self.room1,
                start_datetime=self.future_date,
                end_datetime=self.future_date - timedelta(hours=1),
                created_by=self.admin_user
            )
            schedule.full_clean()
    
    def test_schedule_validation_duration_too_long(self):
        """Test de validación: duración excesiva (más de 12 horas)"""
        with self.assertRaises(ValidationError):
            schedule = Schedule(
                user=self.monitor_user,
                room=self.room1,
                start_datetime=self.future_date,
                end_datetime=self.future_date + timedelta(hours=13),
                created_by=self.admin_user
            )
            schedule.full_clean()
    
    def test_schedule_validation_non_monitor_user(self):
        """Test de validación: usuario no monitor"""
        with self.assertRaises(ValidationError):
            schedule = Schedule(
                user=self.admin_user,  # Admin, no monitor
                room=self.room1,
                start_datetime=self.future_date,
                end_datetime=self.future_date + timedelta(hours=4),
                created_by=self.admin_user
            )
            schedule.full_clean()
    
    def test_schedule_properties(self):
        """Test de propiedades del modelo"""
        # Turno actual
        current_schedule = Schedule.objects.create(
            user=self.monitor_user,
            room=self.room1,
            start_datetime=self.now - timedelta(hours=1),
            end_datetime=self.now + timedelta(hours=1),
            created_by=self.admin_user
        )
        
        self.assertTrue(current_schedule.is_current)
        self.assertEqual(current_schedule.duration_hours, 2.0)
        
        # Turno próximo
        upcoming_schedule = Schedule.objects.create(
            user=self.monitor_user,
            room=self.room2,
            start_datetime=self.now + timedelta(hours=2),
            end_datetime=self.now + timedelta(hours=4),
            created_by=self.admin_user
        )
        
        self.assertTrue(upcoming_schedule.is_upcoming)
        self.assertFalse(upcoming_schedule.is_current)
    
    def test_schedule_string_representation(self):
        """Test de representación string del modelo"""
        schedule = Schedule.objects.create(
            user=self.monitor_user,
            room=self.room1,
            start_datetime=self.future_date,
            end_datetime=self.future_date + timedelta(hours=4),
            created_by=self.admin_user
        )
        
        expected_str = f"{self.monitor_user} - {self.room1} - {self.future_date.strftime('%d/%m/%Y %H:%M')}"
        self.assertEqual(str(schedule), expected_str)
    
    def test_schedule_status_choices(self):
        """Test de opciones de estado"""
        schedule = Schedule.objects.create(
            user=self.monitor_user,
            room=self.room1,
            start_datetime=self.future_date,
            end_datetime=self.future_date + timedelta(hours=4),
            created_by=self.admin_user
        )
        
        # Test estado por defecto
        self.assertEqual(schedule.status, Schedule.ACTIVE)
        
        # Test cambio de estado
        schedule.status = Schedule.COMPLETED
        schedule.save()
        
        self.assertEqual(schedule.status, Schedule.COMPLETED)
        self.assertFalse(schedule.is_active)
    
    def test_schedule_has_compliance_without_entries(self):
        """Test compliance sin entradas de sala"""
        schedule = Schedule.objects.create(
            user=self.monitor_user,
            room=self.room1,
            start_datetime=self.past_date,
            end_datetime=self.past_date + timedelta(hours=4),
            created_by=self.admin_user,
            status=Schedule.COMPLETED
        )
        
        self.assertFalse(schedule.has_compliance())
    
    def test_schedule_recurring_property(self):
        """Test de turno recurrente"""
        schedule = Schedule.objects.create(
            user=self.monitor_user,
            room=self.room1,
            start_datetime=self.future_date,
            end_datetime=self.future_date + timedelta(hours=4),
            created_by=self.admin_user,
            recurring=True
        )
        
        self.assertTrue(schedule.recurring)