from django.test import TestCase, override_settings
from django.contrib.auth import get_user_model
from django.core import mail

User = get_user_model()


@override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
class RegistrationUpdatedTests(TestCase):
    def setUp(self):
        # Crear admin para recibir notificaciones
        self.admin = User.objects.create_user(
            identification="AD-001",
            username="adminuser",
            email="admin@example.com",
            password="adminpass123",
            role="admin",
            is_verified=True,
            is_staff=True,
            is_superuser=True
        )

    def test_monitor_registration_returns_json_response(self):
        """Test que el registro de monitor devuelve respuesta JSON"""
        url = "/api/auth/register/"
        data = {
            "identification": "MO-001",
            "username": "newmonitor",
            "email": "newmonitor@example.com",
            "password": "monitorpass123",
            "password_confirm": "monitorpass123",
            "first_name": "New",
            "last_name": "Monitor",
            "role": "monitor"
        }
        
        response = self.client.post(url, data)
        
        self.assertEqual(response.status_code, 201)
        response_data = response.json()
        
        # Verificar estructura de respuesta
        self.assertIn("message", response_data)
        self.assertIn("user", response_data)
        
        # Verificar mensaje específico para monitor
        self.assertIn("Esperando verificación", response_data["message"])
        
        # Verificar datos del usuario
        user_data = response_data["user"]
        self.assertEqual(user_data["username"], "newmonitor")
        self.assertEqual(user_data["email"], "newmonitor@example.com")
        self.assertEqual(user_data["role"], "monitor")
        self.assertFalse(user_data["is_verified"])  # Monitor no verificado inicialmente

    def test_admin_registration_returns_json_response(self):
        """Test que el registro de admin devuelve respuesta JSON"""
        url = "/api/auth/register/"
        data = {
            "identification": "AD-002",
            "username": "newadmin",
            "email": "newadmin@example.com",
            "password": "adminpass123",
            "password_confirm": "adminpass123",
            "first_name": "New",
            "last_name": "Admin",
            "role": "admin"
        }
        
        response = self.client.post(url, data)
        
        self.assertEqual(response.status_code, 201)
        response_data = response.json()
        
        # Verificar mensaje específico para admin
        self.assertIn("Administrador registrado y verificado", response_data["message"])
        
        # Verificar datos del usuario
        user_data = response_data["user"]
        self.assertEqual(user_data["username"], "newadmin")
        self.assertEqual(user_data["role"], "admin")
        self.assertTrue(user_data["is_verified"])  # Admin verificado automáticamente

    def test_monitor_registration_sends_email_to_admin(self):
        """Test que el registro de monitor envía email al admin"""
        url = "/api/auth/register/"
        data = {
            "identification": "MO-002",
            "username": "monitor2",
            "email": "monitor2@example.com",
            "password": "monitorpass123",
            "password_confirm": "monitorpass123",
            "first_name": "Monitor",
            "last_name": "User",
            "role": "monitor"
        }
        
        response = self.client.post(url, data)
        
        self.assertEqual(response.status_code, 201)
        
        # Verificar que se envió email al admin
        self.assertGreaterEqual(len(mail.outbox), 1)
        email = mail.outbox[0]
        self.assertIn("Nuevo monitor pendiente de verificación", email.subject)
        self.assertIn("admin@example.com", email.recipients())

    def test_admin_registration_no_email_sent(self):
        """Test que el registro de admin no envía email de verificación"""
        url = "/api/auth/register/"
        data = {
            "identification": "AD-003",
            "username": "admin2",
            "email": "admin2@example.com",
            "password": "adminpass123",
            "password_confirm": "adminpass123",
            "first_name": "Admin",
            "last_name": "User",
            "role": "admin"
        }
        
        # Limpiar outbox antes del test
        mail.outbox.clear()
        
        response = self.client.post(url, data)
        
        self.assertEqual(response.status_code, 201)
        
        # Verificar que NO se envió email de verificación
        self.assertEqual(len(mail.outbox), 0)

    def test_registration_validation_errors(self):
        """Test que los errores de validación se devuelven correctamente"""
        url = "/api/auth/register/"
        data = {
            "identification": "MO-003",
            "username": "monitor3",
            "email": "invalid-email",  # Email inválido
            "password": "short",  # Contraseña muy corta
            "password_confirm": "different",  # Contraseñas no coinciden
            "first_name": "Test",
            "last_name": "User",
            "role": "monitor"
        }
        
        response = self.client.post(url, data)
        
        self.assertEqual(response.status_code, 400)
        response_data = response.json()
        
        # Verificar que se devuelven errores específicos
        self.assertIn("email", response_data)
        self.assertIn("password", response_data)
        # password_confirm puede no aparecer si otros errores son más prioritarios
        # Verificar que al menos hay errores de validación
        self.assertGreater(len(response_data), 0)

    def test_registration_duplicate_username(self):
        """Test manejo de username duplicado"""
        # Crear usuario existente
        User.objects.create_user(
            identification="EX-001",
            username="existinguser",
            email="existing@example.com",
            password="existingpass123",
            role="monitor",
            is_verified=True
        )
        
        url = "/api/auth/register/"
        data = {
            "identification": "MO-004",
            "username": "existinguser",  # Username duplicado
            "email": "newuser@example.com",
            "password": "newpass123",
            "password_confirm": "newpass123",
            "first_name": "New",
            "last_name": "User",
            "role": "monitor"
        }
        
        response = self.client.post(url, data)
        
        self.assertEqual(response.status_code, 400)
        response_data = response.json()
        self.assertIn("username", response_data)

    def test_registration_duplicate_email(self):
        """Test manejo de email duplicado"""
        # Crear usuario existente
        User.objects.create_user(
            identification="EX-002",
            username="existinguser2",
            email="existing2@example.com",
            password="existingpass123",
            role="monitor",
            is_verified=True
        )
        
        url = "/api/auth/register/"
        data = {
            "identification": "MO-005",
            "username": "newuser",
            "email": "existing2@example.com",  # Email duplicado
            "password": "newpass123",
            "password_confirm": "newpass123",
            "first_name": "New",
            "last_name": "User",
            "role": "monitor"
        }
        
        response = self.client.post(url, data)
        
        self.assertEqual(response.status_code, 400)
        response_data = response.json()
        self.assertIn("email", response_data)

    def test_registration_duplicate_identification(self):
        """Test manejo de identificación duplicada"""
        # Crear usuario existente
        User.objects.create_user(
            identification="EX-003",
            username="existinguser3",
            email="existing3@example.com",
            password="existingpass123",
            role="monitor",
            is_verified=True
        )
        
        url = "/api/auth/register/"
        data = {
            "identification": "EX-003",  # Identificación duplicada
            "username": "newuser2",
            "email": "newuser2@example.com",
            "password": "newpass123",
            "password_confirm": "newpass123",
            "first_name": "New",
            "last_name": "User",
            "role": "monitor"
        }
        
        response = self.client.post(url, data)
        
        self.assertEqual(response.status_code, 400)
        response_data = response.json()
        self.assertIn("identification", response_data)
