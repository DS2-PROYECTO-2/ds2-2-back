from django.test import TestCase
from rooms.models import Room


class RoomsApiTests(TestCase):
    def setUp(self):
        Room.objects.create(name="Sala 1", code="R001", capacity=10, description="Aula 1")

    def test_list_rooms(self):
        response = self.client.get("/api/rooms/")
        self.assertEqual(response.status_code, 200)

    def test_detail_room_exists(self):
        room = Room.objects.first()
        response = self.client.get(f"/api/rooms/{room.id}/")
        self.assertEqual(response.status_code, 200)

    def test_detail_room_not_found(self):
        response = self.client.get("/api/rooms/999999/")
        self.assertEqual(response.status_code, 404)

