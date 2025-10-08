"""
Tests minimalistas para endpoint de promoción de usuarios
"""
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from rest_framework.authtoken.models import Token
from users.models import User


class AdminPromoteUserTestCase(TestCase):
    
    def setUp(self):
        """Configuración inicial para los tests"""
        # Crear usuarios de prueba
        self.admin_user = User.objects.create_user(
            username='admin_test',
            email='admin@test.com',
            password='testpass123',
            identification='12345678',
            role='admin',
            is_verified=True
        )
        
        self.monitor_user = User.objects.create_user(
            username='monitor_test', 
            email='monitor@test.com',
            password='testpass123',
            identification='87654321',
            role='monitor',
            is_verified=True
        )
        
        self.another_admin = User.objects.create_user(
            username='admin2_test',
            email='admin2@test.com', 
            password='testpass123',
            identification='11223344',
            role='admin',
            is_verified=True
        )
        
        # Crear tokens
        self.admin_token = Token.objects.create(user=self.admin_user)
        
        self.client = APIClient()
    
    def test_admin_can_promote_monitor_to_admin(self):
        """Test: Admin puede ascender monitor a administrador"""
        # Autenticar como admin
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.admin_token.key}')
        
        url = reverse('admin_promote_user', kwargs={'user_id': self.monitor_user.id})
        response = self.client.post(url)
        
        # Verificar respuesta exitosa
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('ascendido a administrador exitosamente', response.data['message'])
        
        # Verificar que el usuario fue promovido
        self.monitor_user.refresh_from_db()
        self.assertEqual(self.monitor_user.role, 'admin')
    
    def test_admin_cannot_change_another_admin_role(self):
        """Test: Admin no puede cambiar el rol de otro admin"""
        # Autenticar como admin
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.admin_token.key}')
        
        url = reverse('admin_promote_user', kwargs={'user_id': self.another_admin.id})
        response = self.client.post(url)
        
        # Verificar que falla
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('Solo se pueden ascender monitores', response.data['error'])
        
        # Verificar que el admin no cambió
        self.another_admin.refresh_from_db()
        self.assertEqual(self.another_admin.role, 'admin')
    
    def test_promote_nonexistent_user_fails(self):
        """Test: Intentar promover usuario inexistente falla"""
        # Autenticar como admin
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.admin_token.key}')
        
        url = reverse('admin_promote_user', kwargs={'user_id': 99999})
        response = self.client.post(url)
        
        # Verificar error 404
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn('no encontrado', response.data['error'])
    
    def test_non_admin_cannot_promote_users(self):
        """Test: Usuario no admin no puede usar el endpoint"""
        # Crear token para monitor
        monitor_token = Token.objects.create(user=self.monitor_user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {monitor_token.key}')
        
        url = reverse('admin_promote_user', kwargs={'user_id': self.monitor_user.id})
        response = self.client.post(url)
        
        # Verificar error de permisos
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)