#!/usr/bin/env python
"""
Script para crear datos simulados usando manage.py
"""
import os
import sys
import django
from datetime import datetime, date, timedelta
import random

# Agregar el directorio del proyecto al path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ds2_back.settings')
django.setup()

from django.contrib.auth import get_user_model
from django.utils import timezone
from users.models import User
from rooms.models import Room, RoomEntry
from schedule.models import Schedule
from courses.models import Course
from equipment.models import Equipment, EquipmentReport
from attendance.models import Attendance, Incapacity
from notifications.models import Notification

def create_test_users():
    """Crear usuarios de prueba"""
    print("👥 Creando usuarios de prueba...")
    
    User = get_user_model()
    
    # Usuarios administradores
    admin_users = [
        {
            'username': 'admin_coordinador',
            'email': 'coordinador@ds2.com',
            'first_name': 'María',
            'last_name': 'González',
            'identification': '12345678',
            'phone': '3001234567',
            'role': User.ADMIN,
            'is_verified': True
        }
    ]
    
    # Usuarios monitores
    monitor_users = [
        {
            'username': 'monitor_ana',
            'email': 'ana.martinez@ds2.com',
            'first_name': 'Ana',
            'last_name': 'Martínez',
            'identification': '1001234567',
            'phone': '3001111111',
            'role': User.MONITOR,
            'is_verified': True
        },
        {
            'username': 'monitor_luis',
            'email': 'luis.silva@ds2.com',
            'first_name': 'Luis',
            'last_name': 'Silva',
            'identification': '1002345678',
            'phone': '3002222222',
            'role': User.MONITOR,
            'is_verified': True
        },
        {
            'username': 'monitor_carla',
            'email': 'carla.torres@ds2.com',
            'first_name': 'Carla',
            'last_name': 'Torres',
            'identification': '1003456789',
            'phone': '3003333333',
            'role': User.MONITOR,
            'is_verified': True
        }
    ]
    
    created_users = []
    
    # Crear administradores
    for user_data in admin_users:
        user, created = User.objects.get_or_create(
            username=user_data['username'],
            defaults={
                'email': user_data['email'],
                'first_name': user_data['first_name'],
                'last_name': user_data['last_name'],
                'identification': user_data['identification'],
                'phone': user_data['phone'],
                'role': user_data['role'],
                'is_verified': user_data['is_verified'],
                'is_staff': True,
                'is_superuser': True
            }
        )
        if created:
            user.set_password('admin123')
            user.save()
            print(f"✅ Admin creado: {user.get_full_name()}")
        created_users.append(user)
    
    # Crear monitores
    for user_data in monitor_users:
        user, created = User.objects.get_or_create(
            username=user_data['username'],
            defaults={
                'email': user_data['email'],
                'first_name': user_data['first_name'],
                'last_name': user_data['last_name'],
                'identification': user_data['identification'],
                'phone': user_data['phone'],
                'role': user_data['role'],
                'is_verified': user_data['is_verified']
            }
        )
        if created:
            user.set_password('monitor123')
            user.save()
            print(f"✅ Monitor creado: {user.get_full_name()}")
        created_users.append(user)
    
    return created_users

def create_rooms():
    """Crear salas de trabajo"""
    print("🏢 Creando salas...")
    
    rooms_data = [
        {
            'name': 'Sala de Sistemas A',
            'code': 'SSA001',
            'capacity': 30,
            'description': 'Sala principal de sistemas con 30 computadores'
        },
        {
            'name': 'Sala de Sistemas B',
            'code': 'SSB001',
            'capacity': 25,
            'description': 'Sala secundaria de sistemas con 25 computadores'
        },
        {
            'name': 'Laboratorio de Redes',
            'code': 'LR001',
            'capacity': 20,
            'description': 'Laboratorio especializado en redes de computadores'
        }
    ]
    
    created_rooms = []
    for room_data in rooms_data:
        room, created = Room.objects.get_or_create(
            code=room_data['code'],
            defaults=room_data
        )
        if created:
            print(f"✅ Sala creada: {room.name}")
        created_rooms.append(room)
    
    return created_rooms

def create_equipment(rooms):
    """Crear equipos de computación"""
    print("💻 Creando equipos...")
    
    created_equipment = []
    
    for room in rooms:
        # Crear 10 equipos por sala
        for i in range(10):
            serial_number = f"{room.code}-PC-{i+1:03d}"
            
            equipment, created = Equipment.objects.get_or_create(
                serial_number=serial_number,
                defaults={
                    'name': f"PC {i+1} - {room.name}",
                    'room': room,
                    'equipment_type': 'desktop',
                    'status': random.choice(['available', 'in_use', 'maintenance']),
                    'purchase_date': date(2024, random.randint(1, 12), random.randint(1, 28)),
                    'location': f"Fila {random.randint(1, 3)}, Columna {random.randint(1, 5)}"
                }
            )
            if created:
                created_equipment.append(equipment)
    
    print(f"✅ {len(created_equipment)} equipos creados")
    return created_equipment

def create_schedules(monitors, rooms):
    """Crear turnos para agosto y septiembre 2025"""
    print("📅 Creando turnos...")
    
    # Fechas de agosto y septiembre 2025
    start_date = date(2025, 8, 1)
    end_date = date(2025, 9, 30)
    
    # Horarios de turnos (mínimo 3 horas)
    shift_times = [
        {'start': '06:00', 'end': '10:00'},
        {'start': '08:00', 'end': '12:00'},
        {'start': '12:00', 'end': '16:00'},
        {'start': '14:00', 'end': '18:00'},
        {'start': '16:00', 'end': '20:00'}
    ]
    
    created_schedules = []
    current_date = start_date
    
    while current_date <= end_date:
        # Solo días de semana
        if current_date.weekday() < 5:
            # Crear 2 turnos por día
            selected_shifts = random.sample(shift_times, 2)
            
            for shift in selected_shifts:
                monitor = random.choice(monitors)
                room = random.choice(rooms)
                
                start_time = datetime.combine(current_date, datetime.strptime(shift['start'], '%H:%M').time())
                end_time = datetime.combine(current_date, datetime.strptime(shift['end'], '%H:%M').time())
                
                start_time = timezone.make_aware(start_time)
                end_time = timezone.make_aware(end_time)
                
                schedule, created = Schedule.objects.get_or_create(
                    user=monitor,
                    room=room,
                    start_datetime=start_time,
                    defaults={
                        'end_datetime': end_time,
                        'status': 'completed',
                        'recurring': False,
                        'notes': f"Turno {shift['start']}-{shift['end']}",
                        'created_by': User.objects.filter(role=User.ADMIN).first()
                    }
                )
                if created:
                    created_schedules.append(schedule)
        
        current_date += timedelta(days=1)
    
    print(f"✅ {len(created_schedules)} turnos creados")
    return created_schedules

def create_room_entries(schedules):
    """Crear entradas y salidas con diferentes tipos de llegada"""
    print("🚪 Creando entradas y salidas...")
    
    created_entries = []
    
    for schedule in schedules:
        # Determinar tipo de llegada
        rand = random.random()
        if rand < 0.6:
            # Llegada a tiempo
            entry_offset = random.randint(-5, 5)
        elif rand < 0.75:
            # Llegada temprana
            entry_offset = -random.randint(10, 30)
        else:
            # Llegada tarde
            entry_offset = random.randint(5, 45)
        
        entry_time = schedule.start_datetime + timedelta(minutes=entry_offset)
        exit_time = schedule.end_datetime + timedelta(minutes=random.randint(-30, 30))
        
        entry, created = RoomEntry.objects.get_or_create(
            user=schedule.user,
            room=schedule.room,
            entry_time=entry_time,
            defaults={
                'exit_time': exit_time,
                'active': False,
                'notes': f"Llegada {'puntual' if entry_offset <= 5 else 'temprana' if entry_offset < 0 else 'tarde'}"
            }
        )
        if created:
            created_entries.append(entry)
    
    print(f"✅ {len(created_entries)} entradas/salidas creadas")
    return created_entries

def create_equipment_reports(equipment, monitors):
    """Crear reportes de problemas con equipos"""
    print("🔧 Creando reportes de equipos...")
    
    problem_types = [
        'No enciende',
        'Pantalla en blanco',
        'Teclado no funciona',
        'Mouse no responde',
        'Sin conexión a internet',
        'Sistema operativo lento'
    ]
    
    created_reports = []
    
    # Crear 15 reportes
    for i in range(15):
        equipment_item = random.choice(equipment)
        monitor = random.choice(monitors)
        problem = random.choice(problem_types)
        
        # Fecha aleatoria en agosto-septiembre 2025
        report_date = date(2025, random.randint(8, 9), random.randint(1, 28))
        report_time = datetime.combine(report_date, datetime.strptime(f"{random.randint(8, 18)}:{random.randint(0, 59):02d}", '%H:%M').time())
        report_time = timezone.make_aware(report_time)
        
        report, created = EquipmentReport.objects.get_or_create(
            equipment=equipment_item,
            reported_by=monitor,
            report_date=report_time,
            defaults={
                'problem_description': f"{problem} en {equipment_item.name}",
                'severity': random.choice(['low', 'medium', 'high']),
                'status': random.choice(['reported', 'in_progress', 'resolved'])
            }
        )
        if created:
            created_reports.append(report)
    
    print(f"✅ {len(created_reports)} reportes de equipos creados")
    return created_reports

def main():
    """Función principal"""
    print("🚀 Creando datos simulados para agosto-septiembre 2025...")
    
    try:
        # 1. Crear usuarios
        users = create_test_users()
        monitors = [user for user in users if user.role == User.MONITOR]
        
        # 2. Crear salas
        rooms = create_rooms()
        
        # 3. Crear equipos
        equipment = create_equipment(rooms)
        
        # 4. Crear turnos
        schedules = create_schedules(monitors, rooms)
        
        # 5. Crear entradas/salidas
        room_entries = create_room_entries(schedules)
        
        # 6. Crear reportes de equipos
        equipment_reports = create_equipment_reports(equipment, monitors)
        
        # Resumen final
        print("\n📊 RESUMEN DE DATOS CREADOS:")
        print(f"👥 Usuarios: {len(users)}")
        print(f"🏢 Salas: {len(rooms)}")
        print(f"💻 Equipos: {len(equipment)}")
        print(f"📅 Turnos: {len(schedules)}")
        print(f"🚪 Entradas/Salidas: {len(room_entries)}")
        print(f"🔧 Reportes de equipos: {len(equipment_reports)}")
        
        print("\n✅ ¡Datos simulados creados exitosamente!")
        print("\n🔑 CREDENCIALES DE PRUEBA:")
        for user in users:
            password = 'admin123' if user.role == User.ADMIN else 'monitor123'
            print(f"  - {user.username} / {password}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()

