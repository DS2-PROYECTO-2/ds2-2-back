from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework.authtoken.models import Token


User = get_user_model()


class NotificationsApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            identification="ID-NOTIF-1",
            username="notifuser",
            email="notif@example.com",
            password="pass12345",
            role="monitor",
            is_verified=True,
        )
        # Autenticación por token para endpoints que requieren IsAuthenticated
        token, _ = Token.objects.get_or_create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {token.key}")

    def test_list(self):
        response = self.client.get("/api/notifications/notifications/")
        self.assertEqual(response.status_code, 200)

    def test_create_retrieve_update_delete_notification(self):
        # Create
        payload = {
            "user": self.user.id,
            "notification_type": "room_entry",
            "title": "Entrada",
            "message": "Usuario entró a sala",
        }
        create_resp = self.client.post("/api/notifications/notifications/", payload, format="json")
        self.assertEqual(create_resp.status_code, 201)
        notif_id = create_resp.data.get("id")
        self.assertIsNotNone(notif_id)

        # Retrieve
        retrieve_resp = self.client.get(f"/api/notifications/notifications/{notif_id}/")
        self.assertEqual(retrieve_resp.status_code, 200)
        self.assertEqual(retrieve_resp.data["title"], "Entrada")

        # Update (partial)
        patch_resp = self.client.patch(
            f"/api/notifications/notifications/{notif_id}/",
            {"read": True},
            format="json",
        )
        self.assertIn(patch_resp.status_code, (200, 202))
        self.assertTrue(patch_resp.data["read"])  # read actualizado

        # Delete
        delete_resp = self.client.delete(f"/api/notifications/notifications/{notif_id}/")
        self.assertIn(delete_resp.status_code, (204,))

        # Not found after delete
        not_found_resp = self.client.get(f"/api/notifications/notifications/{notif_id}/")
        self.assertEqual(not_found_resp.status_code, 404)

    def test_create_invalid_payload_returns_400(self):
        bad_payload = {
            # Falta user y notification_type
            "title": "Sin tipo",
            "message": "Mensaje",
        }
        resp = self.client.post("/api/notifications/notifications/", bad_payload, format="json")
        self.assertEqual(resp.status_code, 400)

