from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from rest_framework.authtoken.models import Token
from datetime import datetime, timedelta

from users.models import User
from rooms.models import Room
from schedule.models import Schedule


class ScheduleTestBase(APITestCase):
    """
    Clase base para tests de Schedule con setup común
    """
    
    def setUp(self):
        """Setup común para todos los tests de Schedule"""
        # Crear usuarios de prueba
        self.admin_user = User.objects.create_user(
            username='admin_test',
            email='admin@test.com',
            password='testpass123',
            role='admin',
            identification='12345678',
            is_verified=True
        )
        
        self.monitor_user = User.objects.create_user(
            username='monitor_test',
            email='monitor@test.com',
            password='testpass123',
            role='monitor',
            identification='87654321',
            is_verified=True
        )
        
        self.unverified_monitor = User.objects.create_user(
            username='unverified_monitor',
            email='unverified@test.com',
            password='testpass123',
            role='monitor',
            identification='11111111',
            is_verified=False
        )
        
        # Crear tokens de autenticación
        self.admin_token = Token.objects.create(user=self.admin_user)
        self.monitor_token = Token.objects.create(user=self.monitor_user)
        self.unverified_token = Token.objects.create(user=self.unverified_monitor)
        
        # Crear salas de prueba
        self.room1 = Room.objects.create(
            name='Laboratorio 1',
            code='LAB001',
            capacity=30,
            description='Laboratorio de prueba'
        )
        
        self.room2 = Room.objects.create(
            name='Laboratorio 2',
            code='LAB002',
            capacity=25,
            description='Segundo laboratorio'
        )
        
        # Configurar cliente API
        self.client = APIClient()
        
        # Fechas de prueba
        self.now = timezone.now()
        self.future_date = self.now + timedelta(days=1)
        self.past_date = self.now - timedelta(days=1)
    
    def authenticate_as_admin(self):
        """Autenticar cliente como administrador"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.admin_token.key}')
    
    def authenticate_as_monitor(self):
        """Autenticar cliente como monitor"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.monitor_token.key}')
    
    def authenticate_as_unverified(self):
        """Autenticar cliente como monitor no verificado"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.unverified_token.key}')
    
    def clear_credentials(self):
        """Limpiar credenciales de autenticación"""
        self.client.credentials()