"""
Tests esenciales para gestión completa de usuarios por administradores
"""
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from rest_framework.authtoken.models import Token
from users.models import User


class AdminUserManagementTestCase(TestCase):
    
    def setUp(self):
        """Configuración inicial para los tests"""
        # Crear usuarios de prueba
        self.admin_user = User.objects.create_user(
            username='admin_test',
            email='admin@test.com',
            password='testpass123',
            identification='12345678',
            role='admin',
            is_verified=True,
            first_name='Admin',
            last_name='Test'
        )
        
        self.monitor_user = User.objects.create_user(
            username='monitor_test', 
            email='monitor@test.com',
            password='testpass123',
            identification='87654321',
            role='monitor',
            is_verified=True,
            first_name='Monitor',
            last_name='Test',
            phone='1234567890'
        )
        
        self.unverified_monitor = User.objects.create_user(
            username='unverified_monitor',
            email='unverified@test.com', 
            password='testpass123',
            identification='11223344',
            role='monitor',
            is_verified=False,
            first_name='Unverified',
            last_name='Monitor'
        )
        
        # Crear tokens
        self.admin_token = Token.objects.create(user=self.admin_user)
        self.monitor_token = Token.objects.create(user=self.monitor_user)
        
        self.client = APIClient()
    
    def test_admin_can_edit_monitor_info(self):
        """Test: Admin puede editar información básica de monitores"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.admin_token.key}')
        
        url = reverse('admin_edit_user', kwargs={'user_id': self.monitor_user.id})
        data = {
            'first_name': 'Monitor Updated',
            'last_name': 'Test Updated',
            'email': 'monitor_updated@test.com',
            'phone': '9876543210'
        }
        response = self.client.patch(url, data)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('actualizado exitosamente', response.data['message'])
        
        # Verificar que se actualizó
        self.monitor_user.refresh_from_db()
        self.assertEqual(self.monitor_user.first_name, 'Monitor Updated')
        self.assertEqual(self.monitor_user.email, 'monitor_updated@test.com')
    
    def test_admin_cannot_edit_another_admin(self):
        """Test: Admin no puede editar otro admin"""
        another_admin = User.objects.create_user(
            username='admin2',
            email='admin2@test.com',
            password='testpass123',
            identification='99887766',
            role='admin',
            is_verified=True
        )
        
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.admin_token.key}')
        
        url = reverse('admin_edit_user', kwargs={'user_id': another_admin.id})
        data = {'first_name': 'Hacked Admin'}
        response = self.client.patch(url, data)
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertIn('No se puede editar información de otros administradores', response.data['error'])
    
    def test_admin_can_view_user_detail(self):
        """Test: Admin puede ver detalles de un usuario"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.admin_token.key}')
        
        url = reverse('admin_user_detail', kwargs={'user_id': self.monitor_user.id})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['user']['username'], 'monitor_test')
        self.assertEqual(response.data['user']['role'], 'monitor')
        self.assertIn('date_joined', response.data['user'])
    
    def test_admin_users_search_by_role(self):
        """Test: Admin puede filtrar usuarios por rol"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.admin_token.key}')
        
        url = reverse('admin_users_search')
        response = self.client.get(url, {'role': 'monitor'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['users']), 2)  # 2 monitores
        for user in response.data['users']:
            self.assertEqual(user['role'], 'monitor')
    
    def test_admin_users_search_by_verification_status(self):
        """Test: Admin puede filtrar usuarios por estado de verificación"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.admin_token.key}')
        
        url = reverse('admin_users_search')
        response = self.client.get(url, {'is_verified': 'false'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(len(response.data['users']) >= 1)
        unverified_users = [u for u in response.data['users'] if not u['is_verified']]
        self.assertTrue(len(unverified_users) >= 1)
    
    def test_admin_users_search_with_text(self):
        """Test: Admin puede buscar usuarios por texto"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.admin_token.key}')
        
        url = reverse('admin_users_search')
        response = self.client.get(url, {'search': 'monitor_test'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(len(response.data['users']) >= 1)
        found_user = next((u for u in response.data['users'] if u['username'] == 'monitor_test'), None)
        self.assertIsNotNone(found_user)
    
    def test_monitor_cannot_access_admin_endpoints(self):
        """Test: Monitor no puede acceder a endpoints de admin"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.monitor_token.key}')
        
        # Test edit
        url = reverse('admin_edit_user', kwargs={'user_id': self.monitor_user.id})
        response = self.client.patch(url, {'first_name': 'Hacked'})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        
        # Test detail
        url = reverse('admin_user_detail', kwargs={'user_id': self.monitor_user.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        
        # Test search
        url = reverse('admin_users_search')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_edit_user_invalid_fields(self):
        """Test: Editar usuario con campos completamente inválidos"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.admin_token.key}')
        
        url = reverse('admin_edit_user', kwargs={'user_id': self.monitor_user.id})
        data = {
            'password': 'newpass',  # Campo no permitido
            'username': 'newusername',  # Campo no permitido
            'invalid_field': 'value'  # Campo inexistente
        }
        response = self.client.patch(url, data)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('No se proporcionaron campos válidos', response.data['error'])
    
    def test_pagination_in_search(self):
        """Test: Paginación en búsqueda de usuarios"""
        # Crear usuarios adicionales
        for i in range(5):
            User.objects.create_user(
                username=f'test_user_{i}',
                email=f'test{i}@test.com',
                password='testpass123',
                identification=f'1000000{i}',
                role='monitor'
            )
        
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.admin_token.key}')
        
        url = reverse('admin_users_search')
        response = self.client.get(url, {'page_size': 3, 'page': 1})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['users']), 3)
        self.assertIn('pagination', response.data)
        self.assertEqual(response.data['pagination']['page'], 1)
        self.assertEqual(response.data['pagination']['page_size'], 3)
    
    def test_admin_can_promote_user_via_edit(self):
        """Test: Admin puede ascender monitor a admin via endpoint edit"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.admin_token.key}')
        
        url = reverse('admin_edit_user', kwargs={'user_id': self.monitor_user.id})
        data = {'role': 'admin'}
        response = self.client.patch(url, data)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('ascendido a admin', response.data['message'])
        
        # Verificar que se ascendió
        self.monitor_user.refresh_from_db()
        self.assertEqual(self.monitor_user.role, 'admin')
    
    def test_admin_can_verify_user_via_edit(self):
        """Test: Admin puede verificar/desverificar usuario via endpoint edit"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.admin_token.key}')
        
        # Verificar usuario no verificado
        url = reverse('admin_edit_user', kwargs={'user_id': self.unverified_monitor.id})
        data = {'is_verified': True}
        response = self.client.patch(url, data)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('verificado', response.data['message'])
        
        # Verificar que se verificó
        self.unverified_monitor.refresh_from_db()
        self.assertTrue(self.unverified_monitor.is_verified)
        self.assertEqual(self.unverified_monitor.verified_by, self.admin_user)
    
    def test_admin_can_unverify_user_via_edit(self):
        """Test: Admin puede desverificar usuario via endpoint edit"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.admin_token.key}')
        
        # Desverificar usuario verificado
        url = reverse('admin_edit_user', kwargs={'user_id': self.monitor_user.id})
        data = {'is_verified': False}
        response = self.client.patch(url, data)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('desverificado', response.data['message'])
        
        # Verificar que se desverificó
        self.monitor_user.refresh_from_db()
        self.assertFalse(self.monitor_user.is_verified)
        self.assertIsNone(self.monitor_user.verified_by)
    
    def test_admin_can_edit_multiple_fields_at_once(self):
        """Test: Admin puede editar múltiples campos a la vez"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.admin_token.key}')
        
        url = reverse('admin_edit_user', kwargs={'user_id': self.unverified_monitor.id})
        data = {
            'first_name': 'Updated Name',
            'email': 'updated@test.com',
            'role': 'admin',
            'is_verified': True
        }
        response = self.client.patch(url, data)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('ascendido a admin', response.data['message'])
        self.assertIn('verificado', response.data['message'])
        
        # Verificar todos los cambios
        self.unverified_monitor.refresh_from_db()
        self.assertEqual(self.unverified_monitor.first_name, 'Updated Name')
        self.assertEqual(self.unverified_monitor.email, 'updated@test.com')
        self.assertEqual(self.unverified_monitor.role, 'admin')
        self.assertTrue(self.unverified_monitor.is_verified)
    
    def test_invalid_role_change(self):
        """Test: Cambio de rol inválido debe fallar"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.admin_token.key}')
        
        url = reverse('admin_edit_user', kwargs={'user_id': self.monitor_user.id})
        data = {'role': 'invalid_role'}
        response = self.client.patch(url, data)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('Rol inválido', response.data['error'])
    
    def test_invalid_verification_value(self):
        """Test: Valor de verificación inválido debe fallar"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.admin_token.key}')
        
        url = reverse('admin_edit_user', kwargs={'user_id': self.monitor_user.id})
        data = {'is_verified': 'invalid_boolean'}
        response = self.client.patch(url, data)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('debe ser true o false', response.data['error'])
    
    def test_no_changes_made(self):
        """Test: Sin cambios debe retornar mensaje apropiado"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.admin_token.key}')
        
        url = reverse('admin_edit_user', kwargs={'user_id': self.monitor_user.id})
        data = {
            'first_name': self.monitor_user.first_name,  # Mismo valor
            'role': self.monitor_user.role,  # Mismo valor
            'is_verified': self.monitor_user.is_verified  # Mismo valor
        }
        response = self.client.patch(url, data)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('sin cambios realizados', response.data['message'])