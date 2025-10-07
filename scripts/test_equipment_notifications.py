#!/usr/bin/env python
"""
Script para probar las notificaciones de reportes de equipos
"""
import os
import sys
import django

# Configurar Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ds2_back.settings')
django.setup()

from equipment.models import Equipment, EquipmentReport
from users.models import User
from rooms.models import Room
from notifications.models import Notification
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_equipment_notifications():
    """
    Probar el sistema de notificaciones de reportes de equipos
    """
    print("Probando notificaciones de reportes de equipos...")
    
    try:
        # 1. Verificar que hay administradores
        admins = User.objects.filter(role='admin', is_active=True)
        print(f"Administradores encontrados: {admins.count()}")
        
        if not admins.exists():
            print("ERROR: No hay administradores en el sistema")
            return False
        
        # 2. Verificar que hay salas
        rooms = Room.objects.filter(is_active=True)
        print(f"Salas activas: {rooms.count()}")
        
        if not rooms.exists():
            print("ERROR: No hay salas en el sistema")
            return False
        
        # 3. Crear un equipo de prueba si no existe
        room = rooms.first()
        equipment, created = Equipment.objects.get_or_create(
            serial_number="TEST001",
            defaults={
                'name': 'Computadora de Prueba',
                'description': 'Equipo para pruebas de notificaciones',
                'room': room,
                'status': 'operational',
                'acquisition_date': '2024-01-01'
            }
        )
        
        if created:
            print(f"OK: Equipo de prueba creado: {equipment.name}")
        else:
            print(f"INFO: Equipo de prueba ya existe: {equipment.name}")
        
        # 4. Verificar que hay usuarios monitores
        monitors = User.objects.filter(role='monitor', is_active=True)
        print(f"Monitores disponibles: {monitors.count()}")
        
        if not monitors.exists():
            print("ERROR: No hay monitores en el sistema")
            return False
        
        # 5. Crear un reporte de falla
        monitor = monitors.first()
        print(f"Creando reporte de falla por {monitor.get_full_name()}...")
        
        # Contar notificaciones antes
        notifications_before = Notification.objects.filter(
            notification_type='equipment_report'
        ).count()
        print(f"Notificaciones de equipos antes: {notifications_before}")
        
        # Crear el reporte (esto debería disparar la señal)
        report = EquipmentReport.objects.create(
            equipment=equipment,
            reported_by=monitor,
            issue_description="La computadora no enciende, pantalla en negro. Se escucha el ventilador pero no hay imagen."
        )
        
        print(f"OK: Reporte creado: #{report.id}")
        
        # 6. Verificar que se crearon las notificaciones
        notifications_after = Notification.objects.filter(
            notification_type='equipment_report'
        ).count()
        print(f"Notificaciones de equipos después: {notifications_after}")
        
        if notifications_after > notifications_before:
            print(f"OK: Se crearon {notifications_after - notifications_before} notificaciones")
            
            # Mostrar las notificaciones creadas
            new_notifications = Notification.objects.filter(
                notification_type='equipment_report',
                related_object_id=report.id
            )
            
            for notification in new_notifications:
                print(f"  Notificación para {notification.user.get_full_name()}: {notification.title}")
        else:
            print("ERROR: No se crearon notificaciones")
            return False
        
        # 7. Verificar que se enviaron emails (simulado)
        print("Los emails se enviarían a:")
        for admin in admins:
            print(f"  - {admin.get_full_name()} ({admin.email})")
        
        print("OK: Prueba de notificaciones completada exitosamente")
        return True
        
    except Exception as e:
        print(f"ERROR: Error en la prueba: {e}")
        logger.error(f"Error probando notificaciones: {e}")
        return False

if __name__ == "__main__":
    success = test_equipment_notifications()
    sys.exit(0 if success else 1)
