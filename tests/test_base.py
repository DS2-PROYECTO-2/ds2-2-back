from django.core.management import call_command
from django.test import TestCase, Client


class BaseProjectTests(TestCase):
    def setUp(self):
        self.client = Client()

    def test_django_check(self):
        # Should not raise system check errors
        call_command("check")

    def test_admin_redirects_when_not_authenticated(self):
        response = self.client.get("/admin/", follow=False)
        # Django admin redirects to login when unauthenticated
        self.assertIn(response.status_code, (301, 302))

    def test_404_for_unknown_route(self):
        response = self.client.get("/definitely-not-found/")
        self.assertEqual(response.status_code, 404)

