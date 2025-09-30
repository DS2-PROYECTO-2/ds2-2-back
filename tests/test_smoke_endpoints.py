from django.test import TestCase, Client


class SmokeEndpointsTests(TestCase):
    def setUp(self):
        self.client = Client()

    def test_rooms_list_endpoint_exists(self):
        response = self.client.get("/api/rooms/")
        # At least should not be 404
        self.assertNotEqual(response.status_code, 404)

    def test_notifications_list_endpoint_exists(self):
        response = self.client.get("/api/notifications/")
        self.assertNotEqual(response.status_code, 404)

    def test_users_login_endpoint_exists(self):
        response = self.client.get("/api/auth/login/")
        # If it's POST-only it may be 405, but not 404
        self.assertNotEqual(response.status_code, 404)

