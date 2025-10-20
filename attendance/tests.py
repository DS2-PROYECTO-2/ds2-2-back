import os
import tempfile
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.test import APITestCase
from rest_framework import status
from rest_framework.authtoken.models import Token
from attendance.models import Attendance
from rooms.models import Room

User = get_user_model()


class AttendanceListUploadTestCase(APITestCase):
    """
    Tests para la funcionalidad de subida de listados de asistencia (US-5)
    """
    
    def setUp(self):
        """Configuración inicial para los tests"""
        # Crear usuarios con diferentes roles
        self.admin_user = User.objects.create_user(
            identification='12345678',
            username='admin_test',
            email='admin@test.com',
            password='admin123',
            role='admin',
            is_verified=True
        )
        
        self.monitor_user = User.objects.create_user(
            identification='87654321',
            username='monitor_test',
            email='monitor@test.com',
            password='monitor123',
            role='monitor',
            is_verified=True
        )
        
        # Crear tokens para autenticación
        self.admin_token = Token.objects.create(user=self.admin_user)
        self.monitor_token = Token.objects.create(user=self.monitor_user)
        
        # Crear una sala de prueba
        self.test_room = Room.objects.create(
            name='Sala de Prueba',
            code='SP001',
            capacity=30,
            description='Sala para testing'
        )
        
        # URLs para los endpoints
        self.attendance_list_url = '/api/attendance/attendances/'
        
    def test_monitor_can_upload_attendance_list(self):
        """Test: Monitor puede subir listado de asistencia (Criterio 1 - PDF/Excel)"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.monitor_token.key}')
        
        # Crear archivo PDF simulado
        pdf_content = b'%PDF-1.4 fake pdf content for testing'
        pdf_file = SimpleUploadedFile(
            "listado_asistencia.pdf",
            pdf_content,
            content_type="application/pdf"
        )
        
        data = {
            'title': 'Listado Asistencia - Sala Prueba',
            'room': self.test_room.id,
            'date': '2025-10-20',
            'file': pdf_file,
            'description': 'Listado de asistencia de la sesión matutina'
        }
        
        response = self.client.post(self.attendance_list_url, data, format='multipart')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Attendance.objects.count(), 1)
        
        attendance = Attendance.objects.first()
        self.assertEqual(attendance.title, 'Listado Asistencia - Sala Prueba')
        self.assertEqual(attendance.room, self.test_room)
        self.assertEqual(attendance.uploaded_by, self.monitor_user)
        self.assertFalse(attendance.reviewed)  # No debe estar marcado como revisado
        
    def test_monitor_can_upload_excel_file(self):
        """Test: Monitor puede subir archivo Excel (Criterio 1 - PDF/Excel)"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.monitor_token.key}')
        
        # Crear archivo Excel simulado
        excel_content = b'PK\x03\x04fake xlsx content for testing'
        excel_file = SimpleUploadedFile(
            "listado_asistencia.xlsx",
            excel_content,
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        
        data = {
            'title': 'Listado Excel - Sala Prueba',
            'room': self.test_room.id,
            'date': '2025-10-20',
            'file': excel_file,
            'description': 'Listado en formato Excel'
        }
        
        response = self.client.post(self.attendance_list_url, data, format='multipart')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        attendance = Attendance.objects.first()
        self.assertTrue(attendance.file.name.endswith('.xlsx'))
        
    def test_attendance_associated_with_room_and_date(self):
        """Test: Archivo se asocia a sala y fecha (Criterio 2)"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.monitor_token.key}')
        
        pdf_file = SimpleUploadedFile(
            "test.pdf",
            b'test content',
            content_type="application/pdf"
        )
        
        data = {
            'title': 'Test Asociación',
            'room': self.test_room.id,
            'date': '2025-10-20',
            'file': pdf_file
        }
        
        response = self.client.post(self.attendance_list_url, data, format='multipart')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        attendance = Attendance.objects.first()
        self.assertEqual(attendance.room.id, self.test_room.id)
        self.assertEqual(str(attendance.date), '2025-10-20')
        
    def test_admin_can_view_all_attendance_lists(self):
        """Test: Admin puede ver todos los listados (Criterio 3)"""
        # Crear algunos listados de asistencia
        Attendance.objects.create(
            title='Listado 1',
            room=self.test_room,
            date='2025-10-20',
            uploaded_by=self.monitor_user,
            description='Test 1'
        )
        Attendance.objects.create(
            title='Listado 2',
            room=self.test_room,
            date='2025-10-19',
            uploaded_by=self.monitor_user,
            description='Test 2'
        )
        
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.admin_token.key}')
        response = self.client.get(self.attendance_list_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)
        
    def test_monitor_only_sees_own_uploads(self):
        """Test: Monitor solo ve sus propios uploads"""
        # Crear otro monitor
        other_monitor = User.objects.create_user(
            identification='11111111',
            username='other_monitor',
            email='other@test.com',
            password='other123',
            role='monitor'
        )
        
        # Crear listados de diferentes monitores
        Attendance.objects.create(
            title='Mi Listado',
            room=self.test_room,
            date='2025-10-20',
            uploaded_by=self.monitor_user
        )
        Attendance.objects.create(
            title='Listado Otro Monitor',
            room=self.test_room,
            date='2025-10-19',
            uploaded_by=other_monitor
        )
        
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.monitor_token.key}')
        response = self.client.get(self.attendance_list_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['title'], 'Mi Listado')
        
    def test_admin_can_mark_as_reviewed(self):
        """Test: Admin puede marcar listado como revisado"""
        attendance = Attendance.objects.create(
            title='Test Review',
            room=self.test_room,
            date='2025-10-20',
            uploaded_by=self.monitor_user
        )
        
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.admin_token.key}')
        url = f'/api/attendance/attendances/{attendance.pk}/mark_as_reviewed/'
        response = self.client.post(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        attendance.refresh_from_db()
        self.assertTrue(attendance.reviewed)
        self.assertEqual(attendance.reviewed_by, self.admin_user)
        
    def test_monitor_cannot_mark_as_reviewed(self):
        """Test: Monitor no puede marcar como revisado"""
        attendance = Attendance.objects.create(
            title='Test Review',
            room=self.test_room,
            date='2025-10-20',
            uploaded_by=self.monitor_user
        )
        
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.monitor_token.key}')
        url = f'/api/attendance/attendances/{attendance.pk}/mark_as_reviewed/'
        response = self.client.post(url)
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        
        attendance.refresh_from_db()
        self.assertFalse(attendance.reviewed)
        
    def test_admin_can_download_attendance_file(self):
        """Test: Admin puede descargar archivos (Criterio 3)"""
        # Crear archivo de prueba
        test_content = b'Test file content for download'
        test_file = SimpleUploadedFile(
            "test_download.pdf",
            test_content,
            content_type="application/pdf"
        )
        
        attendance = Attendance.objects.create(
            title='Test Download',
            room=self.test_room,
            date='2025-10-20',
            uploaded_by=self.monitor_user,
            file=test_file
        )
        
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.admin_token.key}')
        url = f'/api/attendance/attendances/{attendance.pk}/download/'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response['Content-Type'], 'application/pdf')
        self.assertIn('attachment', response['Content-Disposition'])
        
    def test_history_recorded_for_monitor(self):
        """Test: Sistema guarda registro en historial del monitor (Criterio 4)"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.monitor_token.key}')
        
        pdf_file = SimpleUploadedFile(
            "historial_test.pdf",
            b'test content',
            content_type="application/pdf"
        )
        
        data = {
            'title': 'Test Historial',
            'room': self.test_room.id,
            'date': '2025-10-20',
            'file': pdf_file
        }
        
        response = self.client.post(self.attendance_list_url, data, format='multipart')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Verificar que el historial está disponible
        url = '/api/attendance/attendances/my_uploads/'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['title'], 'Test Historial')
        self.assertEqual(response.data[0]['uploaded_by_username'], 'monitor_test')
        
    def test_unauthenticated_user_cannot_upload(self):
        """Test: Usuario no autenticado no puede subir archivos"""
        pdf_file = SimpleUploadedFile(
            "unauthorized.pdf",
            b'test content',
            content_type="application/pdf"
        )
        
        data = {
            'title': 'Unauthorized Test',
            'room': self.test_room.id,
            'date': '2025-10-20',
            'file': pdf_file
        }
        
        response = self.client.post(self.attendance_list_url, data, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        
    def test_file_upload_validation(self):
        """Test: Validación de campos requeridos"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.monitor_token.key}')
        
        # Test sin archivo
        data = {
            'title': 'Test Sin Archivo',
            'room': self.test_room.id,
            'date': '2025-10-20'
        }
        
        response = self.client.post(self.attendance_list_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
        # Test sin sala
        pdf_file = SimpleUploadedFile(
            "test.pdf",
            b'test content',
            content_type="application/pdf"
        )
        
        data = {
            'title': 'Test Sin Sala',
            'date': '2025-10-20',
            'file': pdf_file
        }
        
        response = self.client.post(self.attendance_list_url, data, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)