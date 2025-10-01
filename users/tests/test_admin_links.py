from django.test import TestCase, override_settings
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
from users.models import ApprovalLink
from users.utils import hash_token, generate_raw_token
import hashlib

User = get_user_model()


@override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
class AdminLinksTests(TestCase):
    def setUp(self):
        self.admin = User.objects.create_user(
            identification="ADM-001",
            username="admin_user",
            email="admin@example.com",
            password="adminpass123",
            role="admin",
            is_verified=True,
        )
        
        self.monitor = User.objects.create_user(
            identification="MON-001",
            username="monitor_user",
            email="monitor@example.com",
            password="monitorpass123",
            role="monitor",
            is_verified=False,
        )

    def test_approval_link_creation_on_registration(self):
        """Test that approval links are created when a monitor registers"""
        # Create a new monitor (this should trigger the signal)
        new_monitor = User.objects.create_user(
            identification="MON-002",
            username="new_monitor",
            email="new_monitor@example.com",
            password="newpass123",
            role="monitor",
            is_verified=False,
        )
        
        # Check that approval links were created
        approval_links = ApprovalLink.objects.filter(user=new_monitor)
        self.assertEqual(approval_links.count(), 2)
        
        # Check that we have both approve and reject links
        actions = [link.action for link in approval_links]
        self.assertIn(ApprovalLink.APPROVE, actions)
        self.assertIn(ApprovalLink.REJECT, actions)
        
        # Check that email was sent to admin
        from django.core import mail
        self.assertGreaterEqual(len(mail.outbox), 1)
        self.assertIn('Nuevo monitor pendiente de verificación', mail.outbox[0].subject)

    def test_approve_user_via_token_success(self):
        """Test successful user approval via token"""
        # Create approval link manually
        raw_token = generate_raw_token()
        approval_link = ApprovalLink.objects.create(
            user=self.monitor,
            action=ApprovalLink.APPROVE,
            token_hash=hash_token(raw_token)
        )
        
        # Use the token to approve
        response = self.client.get(f'/api/auth/admin/users/activate/?token={raw_token}')
        
        self.assertEqual(response.status_code, 200)
        self.assertIn('ha sido verificado', response.content.decode())
        
        # Check user was verified
        self.monitor.refresh_from_db()
        self.assertTrue(self.monitor.is_verified)
        
        # Check that both approval links were deleted
        self.assertFalse(ApprovalLink.objects.filter(user=self.monitor).exists())

    def test_reject_user_via_token_success(self):
        """Test successful user rejection via token"""
        # Create approval link manually
        raw_token = generate_raw_token()
        approval_link = ApprovalLink.objects.create(
            user=self.monitor,
            action=ApprovalLink.REJECT,
            token_hash=hash_token(raw_token)
        )
        
        # Use the token to reject
        response = self.client.get(f'/api/auth/admin/users/delete/?token={raw_token}')
        
        self.assertEqual(response.status_code, 200)
        self.assertIn('ha sido eliminado', response.content.decode())
        
        # Check user was deleted
        self.assertFalse(User.objects.filter(id=self.monitor.id).exists())
        
        # Check that approval links were deleted
        self.assertFalse(ApprovalLink.objects.filter(user=self.monitor).exists())

    def test_approve_user_invalid_token(self):
        """Test approval with invalid token"""
        response = self.client.get('/api/auth/admin/users/activate/?token=invalid-token')
        
        self.assertEqual(response.status_code, 400)
        self.assertIn('Enlace inválido', response.content.decode())

    def test_approve_user_missing_token(self):
        """Test approval without token"""
        response = self.client.get('/api/auth/admin/users/activate/')
        
        self.assertEqual(response.status_code, 400)
        self.assertIn('Falta token', response.content.decode())

    def test_approve_user_expired_token(self):
        """Test approval with expired token"""
        raw_token = generate_raw_token()
        approval_link = ApprovalLink.objects.create(
            user=self.monitor,
            action=ApprovalLink.APPROVE,
            token_hash=hash_token(raw_token),
            expires_at=timezone.now() - timedelta(hours=1)  # Expired
        )
        
        response = self.client.get(f'/api/auth/admin/users/activate/?token={raw_token}')
        
        self.assertEqual(response.status_code, 400)
        self.assertIn('El enlace expiró', response.content.decode())
        
        # Token should be deleted
        self.assertFalse(ApprovalLink.objects.filter(id=approval_link.id).exists())

    def test_approve_user_used_token(self):
        """Test approval with already used token"""
        raw_token = generate_raw_token()
        approval_link = ApprovalLink.objects.create(
            user=self.monitor,
            action=ApprovalLink.APPROVE,
            token_hash=hash_token(raw_token),
            used_at=timezone.now()  # Already used
        )
        
        response = self.client.get(f'/api/auth/admin/users/activate/?token={raw_token}')
        
        self.assertEqual(response.status_code, 400)
        self.assertIn('ya fue usado', response.content.decode())

    def test_reject_user_invalid_token(self):
        """Test rejection with invalid token"""
        response = self.client.get('/api/auth/admin/users/delete/?token=invalid-token')
        
        self.assertEqual(response.status_code, 400)
        self.assertIn('Enlace inválido', response.content.decode())

    def test_reject_user_expired_token(self):
        """Test rejection with expired token"""
        raw_token = generate_raw_token()
        approval_link = ApprovalLink.objects.create(
            user=self.monitor,
            action=ApprovalLink.REJECT,
            token_hash=hash_token(raw_token),
            expires_at=timezone.now() - timedelta(hours=1)  # Expired
        )
        
        response = self.client.get(f'/api/auth/admin/users/delete/?token={raw_token}')
        
        self.assertEqual(response.status_code, 400)
        self.assertIn('El enlace expiró', response.content.decode())
        
        # Token should be deleted
        self.assertFalse(ApprovalLink.objects.filter(id=approval_link.id).exists())

    def test_approval_link_expiration(self):
        """Test that approval links expire after 24 hours"""
        approval_link = ApprovalLink.objects.create(
            user=self.monitor,
            action=ApprovalLink.APPROVE,
            token_hash=hash_token(generate_raw_token())
        )
        
        # Check initial state
        self.assertFalse(approval_link.is_expired())
        
        # Manually set expiration to past
        approval_link.expires_at = timezone.now() - timedelta(hours=1)
        approval_link.save()
        
        # Check expired state
        self.assertTrue(approval_link.is_expired())
        self.assertFalse(approval_link.is_valid())

    def test_approval_link_usage_tracking(self):
        """Test that approval links track usage"""
        approval_link = ApprovalLink.objects.create(
            user=self.monitor,
            action=ApprovalLink.APPROVE,
            token_hash=hash_token(generate_raw_token())
        )
        
        # Check initial state
        self.assertFalse(approval_link.is_used())
        self.assertTrue(approval_link.is_valid())
        
        # Mark as used
        approval_link.mark_as_used()
        
        # Check used state
        self.assertTrue(approval_link.is_used())
        self.assertFalse(approval_link.is_valid())

    def test_approval_link_cleanup_on_approval(self):
        """Test that both approval and reject links are deleted when one is used"""
        # Create both links
        approve_token = generate_raw_token()
        reject_token = generate_raw_token()
        
        approve_link = ApprovalLink.objects.create(
            user=self.monitor,
            action=ApprovalLink.APPROVE,
            token_hash=hash_token(approve_token)
        )
        
        reject_link = ApprovalLink.objects.create(
            user=self.monitor,
            action=ApprovalLink.REJECT,
            token_hash=hash_token(reject_token)
        )
        
        # Use approve link
        response = self.client.get(f'/api/auth/admin/users/activate/?token={approve_token}')
        self.assertEqual(response.status_code, 200)
        
        # Both links should be deleted
        self.assertFalse(ApprovalLink.objects.filter(user=self.monitor).exists())

    def test_approval_link_cleanup_on_rejection(self):
        """Test that both approval and reject links are deleted when one is used"""
        # Create both links
        approve_token = generate_raw_token()
        reject_token = generate_raw_token()
        
        approve_link = ApprovalLink.objects.create(
            user=self.monitor,
            action=ApprovalLink.APPROVE,
            token_hash=hash_token(approve_token)
        )
        
        reject_link = ApprovalLink.objects.create(
            user=self.monitor,
            action=ApprovalLink.REJECT,
            token_hash=hash_token(reject_token)
        )
        
        # Use reject link
        response = self.client.get(f'/api/auth/admin/users/delete/?token={reject_token}')
        self.assertEqual(response.status_code, 200)
        
        # Both links should be deleted
        self.assertFalse(ApprovalLink.objects.filter(user=self.monitor).exists())

    def test_approval_link_automatic_expiration_setting(self):
        """Test that approval links automatically set expiration to 24 hours"""
        approval_link = ApprovalLink.objects.create(
            user=self.monitor,
            action=ApprovalLink.APPROVE,
            token_hash=hash_token(generate_raw_token())
        )
        
        # Check that expiration is set to approximately 24 hours from now
        expected_expiration = timezone.now() + timedelta(hours=24)
        time_diff = abs((approval_link.expires_at - expected_expiration).total_seconds())
        self.assertLess(time_diff, 60)  # Within 1 minute

    def test_approval_link_token_hash_security(self):
        """Test that tokens are properly hashed for security"""
        raw_token = generate_raw_token()
        approval_link = ApprovalLink.objects.create(
            user=self.monitor,
            action=ApprovalLink.APPROVE,
            token_hash=hash_token(raw_token)
        )
        
        # The stored hash should not be the raw token
        self.assertNotEqual(approval_link.token_hash, raw_token)
        
        # The stored hash should be the SHA256 hash of the raw token
        expected_hash = hashlib.sha256(raw_token.encode()).hexdigest()
        self.assertEqual(approval_link.token_hash, expected_hash)
