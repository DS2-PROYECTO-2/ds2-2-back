from django.test import TestCase, override_settings
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta
from users.models import ApprovalLink
from users.utils import generate_raw_token, hash_token
from django.core import mail
import hashlib

User = get_user_model()


@override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
class AdminApprovalLinksTests(TestCase):
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

    def test_approval_link_creation_on_registration(self):
        """Test que se crean enlaces de aprobación cuando un monitor se registra"""
        # El monitor ya fue creado en setUp, lo que debería haber disparado el signal
        # Forzar la ejecución del signal si no se ejecutó automáticamente
        from users.signals import notify_admin_new_user_registration
        from django.db.models.signals import post_save
        from users.models import User
        
        # Disparar el signal manualmente
        notify_admin_new_user_registration(
            sender=User,
            instance=self.monitor,
            created=True
        )
        
        approval_links = ApprovalLink.objects.filter(user=self.monitor)
        self.assertEqual(approval_links.count(), 2)
        
        # Verificar que tenemos ambos tipos de enlaces
        actions = [link.action for link in approval_links]
        self.assertIn(ApprovalLink.APPROVE, actions)
        self.assertIn(ApprovalLink.REJECT, actions)
        
        # Verificar que se envió email al admin
        self.assertGreaterEqual(len(mail.outbox), 1)
        self.assertIn('Nuevo monitor pendiente de verificación', mail.outbox[0].subject)

    def test_approval_link_expiration(self):
        """Test que los enlaces expiran correctamente"""
        # Crear enlace con expiración pasada
        expired_link = ApprovalLink.objects.create(
            user=self.monitor,
            action=ApprovalLink.APPROVE,
            token_hash="test_hash",
            expires_at=timezone.now() - timedelta(hours=1)
        )
        
        self.assertTrue(expired_link.is_expired())
        self.assertFalse(expired_link.is_valid())

    def test_approval_link_usage_tracking(self):
        """Test que se puede marcar un enlace como usado"""
        link = ApprovalLink.objects.create(
            user=self.monitor,
            action=ApprovalLink.APPROVE,
            token_hash="test_hash"
        )
        
        self.assertFalse(link.is_used())
        link.mark_as_used()
        self.assertTrue(link.is_used())
        self.assertFalse(link.is_valid())

    def test_approval_link_token_hashing(self):
        """Test que los tokens se hashean correctamente"""
        raw_token = generate_raw_token()
        token_hash = hash_token(raw_token)
        
        # Verificar que el hash es consistente
        self.assertEqual(hash_token(raw_token), token_hash)
        
        # Verificar que diferentes tokens producen diferentes hashes
        another_token = generate_raw_token()
        self.assertNotEqual(token_hash, hash_token(another_token))

    def test_approval_via_token_success(self):
        """Test aprobación exitosa via token"""
        # Crear enlace de aprobación
        raw_token = generate_raw_token()
        token_hash = hash_token(raw_token)
        
        ApprovalLink.objects.create(
            user=self.monitor,
            action=ApprovalLink.APPROVE,
            token_hash=token_hash
        )
        
        # Simular click en enlace de aprobación
        url = f"/api/auth/admin/users/activate/?token={raw_token}"
        response = self.client.get(url)
        
        # Debería redirigir al frontend con éxito
        self.assertEqual(response.status_code, 302)
        self.assertIn("admin/approval?action=approved", response.url)
        
        # Verificar que el usuario fue aprobado
        self.monitor.refresh_from_db()
        self.assertTrue(self.monitor.is_verified)
        
        # Verificar que los enlaces fueron eliminados
        self.assertEqual(ApprovalLink.objects.filter(user=self.monitor).count(), 0)

    def test_rejection_via_token_success(self):
        """Test rechazo exitoso via token"""
        # Crear enlace de rechazo
        raw_token = generate_raw_token()
        token_hash = hash_token(raw_token)
        
        ApprovalLink.objects.create(
            user=self.monitor,
            action=ApprovalLink.REJECT,
            token_hash=token_hash
        )
        
        # Simular click en enlace de rechazo
        url = f"/api/auth/admin/users/delete/?token={raw_token}"
        response = self.client.get(url)
        
        # Debería redirigir al frontend con éxito
        self.assertEqual(response.status_code, 302)
        self.assertIn("admin/approval?action=rejected", response.url)
        
        # Verificar que el usuario fue eliminado
        self.assertFalse(User.objects.filter(id=self.monitor.id).exists())

    def test_approval_invalid_token(self):
        """Test manejo de token inválido"""
        url = "/api/auth/admin/users/activate/?token=invalid_token"
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 302)
        self.assertIn("admin/approval?error=invalid_token", response.url)

    def test_approval_missing_token(self):
        """Test manejo de token faltante"""
        url = "/api/auth/admin/users/activate/"
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 302)
        self.assertIn("admin/approval?error=missing_token", response.url)

    def test_approval_expired_token(self):
        """Test manejo de token expirado"""
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
        self.assertIn("admin/approval?error=expired", response.url)

    def test_approval_used_token(self):
        """Test manejo de token ya usado"""
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
        self.assertIn("admin/approval?error=used", response.url)

    def test_approval_cleanup_on_use(self):
        """Test que se eliminan ambos enlaces cuando se usa uno"""
        # Crear ambos enlaces
        approve_token = generate_raw_token()
        reject_token = generate_raw_token()
        
        ApprovalLink.objects.create(
            user=self.monitor,
            action=ApprovalLink.APPROVE,
            token_hash=hash_token(approve_token)
        )
        ApprovalLink.objects.create(
            user=self.monitor,
            action=ApprovalLink.REJECT,
            token_hash=hash_token(reject_token)
        )
        
        # Usar enlace de aprobación
        url = f"/api/auth/admin/users/activate/?token={approve_token}"
        response = self.client.get(url)
        
        # Verificar que ambos enlaces fueron eliminados
        self.assertEqual(ApprovalLink.objects.filter(user=self.monitor).count(), 0)
