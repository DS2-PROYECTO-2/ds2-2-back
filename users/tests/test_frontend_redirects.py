from django.test import TestCase, override_settings
from django.contrib.auth import get_user_model
from django.urls import reverse
from users.models import ApprovalLink
from users.utils import generate_raw_token, hash_token

User = get_user_model()


@override_settings(
    FRONTEND_BASE_URL="http://localhost:5173",
    EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend'
)
class FrontendRedirectsTests(TestCase):
    def setUp(self):
        # Crear admin
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
        
        # Crear monitor no verificado
        self.monitor = User.objects.create_user(
            identification="MO-001",
            username="monitoruser",
            email="monitor@example.com",
            password="monitorpass123",
            role="monitor",
            is_verified=False
        )

    def test_admin_approval_redirect_success(self):
        """Test redirección exitosa para aprobación de usuario"""
        # Crear enlace de aprobación
        raw_token = generate_raw_token()
        token_hash = hash_token(raw_token)
        
        ApprovalLink.objects.create(
            user=self.monitor,
            action=ApprovalLink.APPROVE,
            token_hash=token_hash
        )
        
        url = f"/api/auth/admin/users/activate/?token={raw_token}"
        response = self.client.get(url)
        
        # Verificar redirección
        self.assertEqual(response.status_code, 302)
        self.assertIn("localhost:5173", response.url)
        self.assertIn("admin/approval", response.url)
        self.assertIn("action=approved", response.url)
        self.assertIn(f"user={self.monitor.username}", response.url)

    def test_admin_rejection_redirect_success(self):
        """Test redirección exitosa para rechazo de usuario"""
        # Crear enlace de rechazo
        raw_token = generate_raw_token()
        token_hash = hash_token(raw_token)
        
        ApprovalLink.objects.create(
            user=self.monitor,
            action=ApprovalLink.REJECT,
            token_hash=token_hash
        )
        
        url = f"/api/auth/admin/users/delete/?token={raw_token}"
        response = self.client.get(url)
        
        # Verificar redirección
        self.assertEqual(response.status_code, 302)
        self.assertIn("localhost:5173", response.url)
        self.assertIn("admin/approval", response.url)
        self.assertIn("action=rejected", response.url)
        self.assertIn(f"user={self.monitor.username}", response.url)

    def test_admin_approval_redirect_missing_token(self):
        """Test redirección con error cuando falta el token"""
        url = "/api/auth/admin/users/activate/"
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 302)
        self.assertIn("localhost:5173", response.url)
        self.assertIn("admin/approval", response.url)
        self.assertIn("error=missing_token", response.url)

    def test_admin_approval_redirect_invalid_token(self):
        """Test redirección con error para token inválido"""
        url = "/api/auth/admin/users/activate/?token=invalid_token"
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 302)
        self.assertIn("localhost:5173", response.url)
        self.assertIn("admin/approval", response.url)
        self.assertIn("error=invalid_token", response.url)

    def test_admin_approval_redirect_expired_token(self):
        """Test redirección con error para token expirado"""
        from django.utils import timezone
        from datetime import timedelta
        
        # Crear enlace expirado
        raw_token = generate_raw_token()
        token_hash = hash_token(raw_token)
        
        ApprovalLink.objects.create(
            user=self.monitor,
            action=ApprovalLink.APPROVE,
            token_hash=token_hash,
            expires_at=timezone.now() - timedelta(hours=1)
        )
        
        url = f"/api/auth/admin/users/activate/?token={raw_token}"
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 302)
        self.assertIn("localhost:5173", response.url)
        self.assertIn("admin/approval", response.url)
        self.assertIn("error=expired", response.url)

    def test_admin_approval_redirect_used_token(self):
        """Test redirección con error para token ya usado"""
        # Crear enlace ya usado
        raw_token = generate_raw_token()
        token_hash = hash_token(raw_token)
        
        link = ApprovalLink.objects.create(
            user=self.monitor,
            action=ApprovalLink.APPROVE,
            token_hash=token_hash
        )
        link.mark_as_used()
        
        url = f"/api/auth/admin/users/activate/?token={raw_token}"
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 302)
        self.assertIn("localhost:5173", response.url)
        self.assertIn("admin/approval", response.url)
        self.assertIn("error=used", response.url)

    def test_password_reset_redirect_to_frontend(self):
        """Test que los enlaces de restablecimiento apuntan al frontend"""
        from users.utils import build_password_reset_url
        
        # Test que la URL se construye correctamente
        test_token = "test-token-123"
        reset_url = build_password_reset_url(test_token)
        
        self.assertIn("localhost:5173", reset_url)
        self.assertIn("reset-password", reset_url)
        self.assertIn(f"token={test_token}", reset_url)

    def test_frontend_base_url_configuration(self):
        """Test que la configuración de FRONTEND_BASE_URL se usa correctamente"""
        from django.conf import settings
        
        # Verificar que la configuración está presente
        self.assertIsNotNone(getattr(settings, 'FRONTEND_BASE_URL', None))
        self.assertEqual(settings.FRONTEND_BASE_URL, "http://localhost:5173")

    def test_redirect_url_encoding(self):
        """Test que los parámetros de URL se codifican correctamente"""
        # Crear enlace de aprobación
        raw_token = generate_raw_token()
        token_hash = hash_token(raw_token)
        
        ApprovalLink.objects.create(
            user=self.monitor,
            action=ApprovalLink.APPROVE,
            token_hash=token_hash
        )
        
        url = f"/api/auth/admin/users/activate/?token={raw_token}"
        response = self.client.get(url)
        
        # Verificar que la URL de redirección está correctamente formada
        self.assertEqual(response.status_code, 302)
        redirect_url = response.url
        
        # Verificar que contiene todos los componentes necesarios
        self.assertIn("localhost:5173", redirect_url)
        self.assertIn("admin/approval", redirect_url)
        self.assertIn("action=approved", redirect_url)
        self.assertIn("user=", redirect_url)
        
        # Verificar que no hay caracteres problemáticos
        self.assertNotIn(" ", redirect_url)
        self.assertNotIn("\n", redirect_url)
        self.assertNotIn("\r", redirect_url)

    def test_multiple_admin_redirects(self):
        """Test que múltiples redirecciones funcionan correctamente"""
        # Crear varios usuarios y enlaces
        users = []
        for i in range(3):
            user = User.objects.create_user(
                identification=f"MO-{i+2:03d}",
                username=f"monitor{i+2}",
                email=f"monitor{i+2}@example.com",
                password="monitorpass123",
                role="monitor",
                is_verified=False
            )
            users.append(user)
            
            # Crear enlaces para cada usuario
            raw_token = generate_raw_token()
            token_hash = hash_token(raw_token)
            
            ApprovalLink.objects.create(
                user=user,
                action=ApprovalLink.APPROVE,
                token_hash=token_hash
            )
            
            # Test redirección para cada usuario
            url = f"/api/auth/admin/users/activate/?token={raw_token}"
            response = self.client.get(url)
            
            self.assertEqual(response.status_code, 302)
            self.assertIn(f"user={user.username}", response.url)
