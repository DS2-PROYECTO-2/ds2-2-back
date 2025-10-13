from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from django.test import TestCase
from users.models import User
from rooms.models import Room
from equipment.models import Equipment, EquipmentReport
from django.utils import timezone


class EquipmentReportsAPITest(TestCase):
    def setUp(self):
        self.client = APIClient()
        # Crear admin y monitor
        self.admin = User.objects.create_user(
            username='admin_equipment', password='pass', role='admin', is_active=True,
            identification='A-100', email='admin_equipment@example.com'
        )
        self.monitor = User.objects.create_user(
            username='monitor_equipment', password='pass', role='monitor', is_active=True,
            identification='M-200', email='monitor_equipment@example.com'
        )
        # Autenticar como monitor por defecto
        self.client.force_authenticate(user=self.monitor)
        # Sala y equipo
        self.room = Room.objects.create(name='Sala X', code='SX01', capacity=10)
        self.equipment = Equipment.objects.create(
            serial_number='SN-XYZ-1',
            name='PC XYZ',
            description='',
            room=self.room,
            status=Equipment.OPERATIONAL,
            acquisition_date='2024-01-01'
        )

    def test_create_report_with_issue_type(self):
        url = '/api/equipment/reports/'
        payload = {
            'equipment': self.equipment.id,
            'reported_by': self.monitor.id,
            'issue_description': 'No enciende',
            'issue_type': 'hardware'
        }
        res = self.client.post(url, payload, format='json')
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(res.data['issue_type'], 'hardware')
        self.assertEqual(res.data['reported_by_name'], self.monitor.get_full_name() or self.monitor.username)

    def test_resolve_and_reopen_report(self):
        # Crear reporte
        report = EquipmentReport.objects.create(
            equipment=self.equipment,
            reported_by=self.monitor,
            issue_description='Pantalla negra'
        )
        # Resolver
        url_resolve = f'/api/equipment/reports/{report.id}/resolve/'
        res1 = self.client.post(url_resolve, {}, format='json')
        self.assertEqual(res1.status_code, status.HTTP_200_OK)
        self.assertTrue(res1.data['resolved'])
        self.assertIsNotNone(res1.data['resolved_date'])
        # Reabrir
        url_reopen = f'/api/equipment/reports/{report.id}/reopen/'
        res2 = self.client.post(url_reopen, {}, format='json')
        self.assertEqual(res2.status_code, status.HTTP_200_OK)
        self.assertFalse(res2.data['resolved'])
        self.assertIsNone(res2.data['resolved_date'])

    def test_delete_report_returns_204(self):
        # Crear reporte
        report = EquipmentReport.objects.create(
            equipment=self.equipment,
            reported_by=self.monitor,
            issue_description='Ruido extraño'
        )
        url_delete = f'/api/equipment/reports/{report.id}/'
        res = self.client.delete(url_delete)
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        # Confirmar que ya no existe
        self.assertFalse(EquipmentReport.objects.filter(id=report.id).exists())


