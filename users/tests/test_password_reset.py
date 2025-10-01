from django.test import TestCase, override_settings
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
from users.models import PasswordReset
from users.utils import hash_token, generate_raw_token

User = get_user_model()


@override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
class PasswordResetTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            identification="PR-001",
            username="pr_user",
            email="pr_user@example.com",
            password="oldpass123",
            role="monitor",
            is_verified=True,
        )

    def test_password_reset_request_success(self):
        """Test successful password reset request"""
        response = self.client.post('/api/auth/password/reset-request/', {
            'email': self.user.email
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn('Si el email existe', response.json()['message'])
        
        # Verify PasswordReset object was created
        self.assertTrue(PasswordReset.objects.filter(user=self.user).exists())
        
        # Verify email was sent
        from django.core import mail
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn('Restablece tu contraseña', mail.outbox[0].subject)

    def test_password_reset_request_nonexistent_email(self):
        """Test password reset request with non-existent email"""
        response = self.client.post('/api/auth/password/reset-request/', {
            'email': 'nonexistent@example.com'
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn('Si el email existe', response.json()['message'])
        
        # No PasswordReset should be created
        self.assertFalse(PasswordReset.objects.exists())
        
        # No email should be sent
        from django.core import mail
        self.assertEqual(len(mail.outbox), 0)

    def test_password_reset_request_invalid_email(self):
        """Test password reset request with invalid email format"""
        response = self.client.post('/api/auth/password/reset-request/', {
            'email': 'invalid-email'
        })
        self.assertEqual(response.status_code, 400)
        self.assertIn('email', response.json())

    def test_password_reset_confirm_success(self):
        """Test successful password reset confirmation"""
        # Create a valid password reset token
        raw_token = generate_raw_token()
        password_reset = PasswordReset.objects.create(
            user=self.user,
            token_hash=hash_token(raw_token),
            expires_at=timezone.now() + timedelta(hours=2)
        )
        
        response = self.client.post('/api/auth/password/reset-confirm/', {
            'token': raw_token,
            'new_password': 'newpass123',
            'new_password_confirm': 'newpass123'
        })
        
        self.assertEqual(response.status_code, 200)
        self.assertIn('actualizada correctamente', response.json()['message'])
        
        # Verify password was changed
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password('newpass123'))
        
        # Verify token was marked as used
        password_reset.refresh_from_db()
        self.assertTrue(password_reset.is_used())

    def test_password_reset_confirm_invalid_token(self):
        """Test password reset confirmation with invalid token"""
        response = self.client.post('/api/auth/password/reset-confirm/', {
            'token': 'invalid-token',
            'new_password': 'newpass123',
            'new_password_confirm': 'newpass123'
        })
        
        self.assertEqual(response.status_code, 400)
        self.assertIn('token', response.json())

    def test_password_reset_confirm_expired_token(self):
        """Test password reset confirmation with expired token"""
        raw_token = generate_raw_token()
        password_reset = PasswordReset.objects.create(
            user=self.user,
            token_hash=hash_token(raw_token),
            expires_at=timezone.now() - timedelta(minutes=1)  # Expired
        )
        
        response = self.client.post('/api/auth/password/reset-confirm/', {
            'token': raw_token,
            'new_password': 'newpass123',
            'new_password_confirm': 'newpass123'
        })
        
        self.assertEqual(response.status_code, 400)
        self.assertIn('token', response.json())

    def test_password_reset_confirm_used_token(self):
        """Test password reset confirmation with already used token"""
        raw_token = generate_raw_token()
        password_reset = PasswordReset.objects.create(
            user=self.user,
            token_hash=hash_token(raw_token),
            expires_at=timezone.now() + timedelta(hours=2),
            used_at=timezone.now()  # Already used
        )
        
        response = self.client.post('/api/auth/password/reset-confirm/', {
            'token': raw_token,
            'new_password': 'newpass123',
            'new_password_confirm': 'newpass123'
        })
        
        self.assertEqual(response.status_code, 400)
        self.assertIn('token', response.json())

    def test_password_reset_confirm_password_mismatch(self):
        """Test password reset confirmation with mismatched passwords"""
        raw_token = generate_raw_token()
        PasswordReset.objects.create(
            user=self.user,
            token_hash=hash_token(raw_token),
            expires_at=timezone.now() + timedelta(hours=2)
        )
        
        response = self.client.post('/api/auth/password/reset-confirm/', {
            'token': raw_token,
            'new_password': 'newpass123',
            'new_password_confirm': 'differentpass123'
        })
        
        self.assertEqual(response.status_code, 400)
        self.assertIn('new_password_confirm', response.json())

    def test_password_reset_confirm_weak_password(self):
        """Test password reset confirmation with weak password"""
        raw_token = generate_raw_token()
        PasswordReset.objects.create(
            user=self.user,
            token_hash=hash_token(raw_token),
            expires_at=timezone.now() + timedelta(hours=2)
        )
        
        response = self.client.post('/api/auth/password/reset-confirm/', {
            'token': raw_token,
            'new_password': '123',  # Too short
            'new_password_confirm': '123'
        })
        
        self.assertEqual(response.status_code, 400)
        self.assertIn('new_password', response.json())

    def test_password_reset_token_expiration(self):
        """Test that expired tokens are automatically cleaned up"""
        # Create an expired token
        raw_token = generate_raw_token()
        password_reset = PasswordReset.objects.create(
            user=self.user,
            token_hash=hash_token(raw_token),
            expires_at=timezone.now() - timedelta(hours=1)
        )
        
        # Try to use expired token
        response = self.client.post('/api/auth/password/reset-confirm/', {
            'token': raw_token,
            'new_password': 'newpass123',
            'new_password_confirm': 'newpass123'
        })
        
        self.assertEqual(response.status_code, 400)
        
        # Token should be deleted after failed attempt
        self.assertFalse(PasswordReset.objects.filter(id=password_reset.id).exists())

    def test_multiple_password_reset_requests(self):
        """Test that multiple password reset requests create new tokens"""
        # First request
        response1 = self.client.post('/api/auth/password/reset-request/', {
            'email': self.user.email
        })
        self.assertEqual(response1.status_code, 200)
        
        # Second request
        response2 = self.client.post('/api/auth/password/reset-request/', {
            'email': self.user.email
        })
        self.assertEqual(response2.status_code, 200)
        
        # Should have 2 PasswordReset objects
        self.assertEqual(PasswordReset.objects.filter(user=self.user).count(), 2)
