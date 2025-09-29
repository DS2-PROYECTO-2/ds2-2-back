from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework.authtoken.models import Token


User = get_user_model()


class UsersApiTests(TestCase):
    def setUp(self):
        self.password = "testpass123"
        self.user = User.objects.create_user(
            identification="ID-0001",
            username="user1",
            email="user1@example.com",
            password=self.password,
            role="monitor",
            is_verified=True,
        )

    def test_login_success(self):
        url = "/api/auth/login/"
        response = self.client.post(url, {"username": "user1", "password": self.password})
        self.assertEqual(response.status_code, 200)
        self.assertIn("token", response.json())

    def test_login_invalid_credentials(self):
        url = "/api/auth/login/"
        response = self.client.post(url, {"username": "user1", "password": "wrong"})
        self.assertIn(response.status_code, (400, 401))

    def test_profile_requires_authentication(self):
        url = "/api/auth/profile/"
        response = self.client.get(url)
        self.assertIn(response.status_code, (401, 403))

    def test_profile_with_token_and_verified(self):
        token, _ = Token.objects.get_or_create(user=self.user)
        url = "/api/auth/profile/"
        response = self.client.get(url, HTTP_AUTHORIZATION=f"Token {token.key}")
        self.assertEqual(response.status_code, 200)

    def test_admin_users_list_public_allows_any(self):
        # Según views, AllowAny en admin_users_list_view
        url = "/api/auth/admin/users/"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

