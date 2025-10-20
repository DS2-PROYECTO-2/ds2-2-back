from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import datetime, date, timedelta
import random
from users.models import User
from rooms.models import Room, RoomEntry
from schedule.models import Schedule
from courses.models import Course
from equipment.models import Equipment, EquipmentReport
from attendance.models import Attendance, Incapacity
from notifications.models import Notification


class Command(BaseCommand):
    help = 'Limpiar datos existentes y crear datos simulados para agosto y septiembre 2025'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clean-only',
            action='store_true',
            help='Solo limpiar datos existentes sin crear nuevos',
        )

    def handle(self, *args, **options):
        if options['clean_only']:
            self.stdout.write(self.style.WARNING('Limpiando datos existentes...'))
            self.clean_existing_data()
            self.stdout.write(self.style.SUCCESS('Datos limpiados exitosamente!'))
            return

        self.stdout.write(self.style.SUCCESS('Limpiando datos existentes y creando datos simulados...'))
        
        try:
            # Limpiar datos existentes
            self.clean_existing_data()
            
            # Crear nuevos datos
            users = self.create_test_users()
            monitors = [user for user in users if user.role == User.MONITOR]
            
            rooms = self.create_rooms()
            equipment = self.create_equipment(rooms)
            courses = self.create_courses()
            schedules = self.create_schedules(monitors, rooms)
            room_entries = self.create_room_entries(schedules)
            equipment_reports = self.create_equipment_reports(equipment, monitors)
            attendance_data = self.create_attendance_data(monitors)
            incapacity_data = self.create_incapacity_data(monitors)
            notifications = self.create_notifications(monitors)
            
            # Resumen final
            self.stdout.write(self.style.SUCCESS('\nRESUMEN DE DATOS CREADOS:'))
            self.stdout.write(f"Usuarios: {len(users)} (2 admins, {len(monitors)} monitores)")
            self.stdout.write(f"Salas: {len(rooms)}")
            self.stdout.write(f"Equipos: {len(equipment)}")
            self.stdout.write(f"Cursos: {len(courses)}")
            self.stdout.write(f"Turnos: {len(schedules)}")
            self.stdout.write(f"Entradas/Salidas: {len(room_entries)}")
            self.stdout.write(f"Reportes de equipos: {len(equipment_reports)}")
            self.stdout.write(f"Listados de asistencia: {len(attendance_data)}")
            self.stdout.write(f"Incapacidades: {len(incapacity_data)}")
            self.stdout.write(f"Notificaciones: {len(notifications)}")
            
            self.stdout.write(self.style.SUCCESS('\nDatos simulados creados exitosamente!'))
            self.stdout.write('\nCREDENCIALES DE PRUEBA:')
            for user in users:
                password = 'admin123' if user.role == User.ADMIN else 'monitor123'
                self.stdout.write(f"  - {user.username} / {password}")
            
            self.stdout.write('\nPERIODO DE DATOS: Agosto y Septiembre 2025')
            self.stdout.write('TURNOS: Minimo 3 horas de duracion')
            self.stdout.write('ENTRADAS: Incluye llegadas a tiempo, tempranas y tardias')
            self.stdout.write('EQUIPOS: Reportes de problemas con computadores')
            self.stdout.write('ESTADISTICAS: Datos completos para exportacion')
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error creando datos: {e}'))
            import traceback
            traceback.print_exc()

    def clean_existing_data(self):
        """Limpiar datos existentes"""
        self.stdout.write('Limpiando datos existentes...')
        
        # Limpiar en orden inverso para evitar problemas de foreign key
        Notification.objects.all().delete()
        Incapacity.objects.all().delete()
        Attendance.objects.all().delete()
        EquipmentReport.objects.all().delete()
        RoomEntry.objects.all().delete()
        Schedule.objects.all().delete()
        Equipment.objects.all().delete()
        Room.objects.all().delete()
        Course.objects.all().delete()
        
        # Limpiar usuarios (excepto superuser)
        User.objects.filter(role__in=[User.ADMIN, User.MONITOR]).exclude(is_superuser=True).delete()
        
        self.stdout.write('Datos limpiados')

    def create_test_users(self):
        """Crear usuarios de prueba"""
        self.stdout.write('Creando usuarios de prueba...')
        
        User = get_user_model()
        
        # Usuarios administradores
        admin_users = [
            {
                'username': 'admin_coordinador',
                'email': 'coordinador@ds2.com',
                'first_name': 'Maria',
                'last_name': 'Gonzalez',
                'identification': '12345678',
                'phone': '3001234567',
                'role': User.ADMIN,
                'is_verified': True
            },
            {
                'username': 'admin_supervisor',
                'email': 'supervisor@ds2.com',
                'first_name': 'Carlos',
                'last_name': 'Rodriguez',
                'identification': '87654321',
                'phone': '3007654321',
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
                'last_name': 'Martinez',
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
            },
            {
                'username': 'monitor_diego',
                'email': 'diego.ramirez@ds2.com',
                'first_name': 'Diego',
                'last_name': 'Ramirez',
                'identification': '1004567890',
                'phone': '3004444444',
                'role': User.MONITOR,
                'is_verified': True
            },
            {
                'username': 'monitor_sofia',
                'email': 'sofia.herrera@ds2.com',
                'first_name': 'Sofia',
                'last_name': 'Herrera',
                'identification': '1005678901',
                'phone': '3005555555',
                'role': User.MONITOR,
                'is_verified': True
            },
            {
                'username': 'monitor_miguel',
                'email': 'miguel.castro@ds2.com',
                'first_name': 'Miguel',
                'last_name': 'Castro',
                'identification': '1006789012',
                'phone': '3006666666',
                'role': User.MONITOR,
                'is_verified': True
            }
        ]
        
        created_users = []
        
        # Crear administradores
        for user_data in admin_users:
            user = User.objects.create_user(
                username=user_data['username'],
                email=user_data['email'],
                first_name=user_data['first_name'],
                last_name=user_data['last_name'],
                identification=user_data['identification'],
                phone=user_data['phone'],
                role=user_data['role'],
                is_verified=user_data['is_verified'],
                is_staff=True,
                is_superuser=True,
                password='admin123'
            )
            self.stdout.write(f"Admin creado: {user.get_full_name()}")
            created_users.append(user)
        
        # Crear monitores
        for user_data in monitor_users:
            user = User.objects.create_user(
                username=user_data['username'],
                email=user_data['email'],
                first_name=user_data['first_name'],
                last_name=user_data['last_name'],
                identification=user_data['identification'],
                phone=user_data['phone'],
                role=user_data['role'],
                is_verified=user_data['is_verified'],
                password='monitor123'
            )
            self.stdout.write(f"Monitor creado: {user.get_full_name()}")
            created_users.append(user)
        
        return created_users

    def create_rooms(self):
        """Crear salas de trabajo"""
        self.stdout.write('Creando salas...')
        
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
            },
            {
                'name': 'Sala de Programacion',
                'code': 'SP001',
                'capacity': 35,
                'description': 'Sala para programacion y desarrollo de software'
            },
            {
                'name': 'Aula Multimedia',
                'code': 'AM001',
                'capacity': 40,
                'description': 'Aula con proyector y equipos multimedia'
            }
        ]
        
        created_rooms = []
        for room_data in rooms_data:
            room = Room.objects.create(**room_data)
            self.stdout.write(f"Sala creada: {room.name}")
            created_rooms.append(room)
        
        return created_rooms

    def create_equipment(self, rooms):
        """Crear equipos de computacion"""
        self.stdout.write('Creando equipos...')
        
        equipment_types = [
            {'name': 'PC Dell OptiPlex', 'type': 'desktop'},
            {'name': 'PC HP ProDesk', 'type': 'desktop'},
            {'name': 'Laptop Lenovo ThinkPad', 'type': 'laptop'},
            {'name': 'Laptop Dell Latitude', 'type': 'laptop'},
            {'name': 'Monitor Samsung 24"', 'type': 'monitor'},
            {'name': 'Monitor LG 27"', 'type': 'monitor'},
            {'name': 'Proyector Epson', 'type': 'projector'},
            {'name': 'Switch Cisco 24 puertos', 'type': 'network'},
            {'name': 'Router TP-Link', 'type': 'network'},
            {'name': 'Impresora HP LaserJet', 'type': 'printer'}
        ]
        
        created_equipment = []
        
        for room in rooms:
            # Crear 15-20 equipos por sala
            num_equipment = random.randint(15, 20)
            
            for i in range(num_equipment):
                equipment_type = random.choice(equipment_types)
                serial_number = f"{room.code}-{equipment_type['type'].upper()}-{i+1:03d}"
                
                equipment = Equipment.objects.create(
                    serial_number=serial_number,
                    name=f"{equipment_type['name']} {i+1}",
                    room=room,
                    equipment_type=equipment_type['type'],
                    status=random.choice(['available', 'in_use', 'maintenance']),
                    purchase_date=date(2024, random.randint(1, 12), random.randint(1, 28)),
                    warranty_expiry=date(2026, random.randint(1, 12), random.randint(1, 28)),
                    location=f"Fila {random.randint(1, 5)}, Columna {random.randint(1, 8)}"
                )
                created_equipment.append(equipment)
        
        self.stdout.write(f"{len(created_equipment)} equipos creados")
        return created_equipment

    def create_courses(self):
        """Crear cursos"""
        self.stdout.write('Creando cursos...')
        
        courses_data = [
            {
                'name': 'Programacion en Python',
                'code': 'PYT001',
                'description': 'Curso introductorio de programacion en Python',
                'credits': 3,
                'schedule': 'Lunes y Miercoles 8:00-10:00',
                'instructor': 'Dr. Ana Martinez',
                'max_students': 30
            },
            {
                'name': 'Bases de Datos',
                'code': 'BD001',
                'description': 'Fundamentos de bases de datos relacionales',
                'credits': 4,
                'schedule': 'Martes y Jueves 10:00-12:00',
                'instructor': 'Dr. Carlos Rodriguez',
                'max_students': 25
            },
            {
                'name': 'Redes de Computadores',
                'code': 'RC001',
                'description': 'Principios de redes y protocolos de comunicacion',
                'credits': 3,
                'schedule': 'Lunes y Viernes 14:00-16:00',
                'instructor': 'Ing. Luis Silva',
                'max_students': 20
            },
            {
                'name': 'Desarrollo Web',
                'code': 'DW001',
                'description': 'Desarrollo de aplicaciones web modernas',
                'credits': 4,
                'schedule': 'Miercoles y Viernes 16:00-18:00',
                'instructor': 'Ing. Carla Torres',
                'max_students': 35
            },
            {
                'name': 'Inteligencia Artificial',
                'code': 'IA001',
                'description': 'Introduccion a la IA y machine learning',
                'credits': 3,
                'schedule': 'Martes y Jueves 18:00-20:00',
                'instructor': 'Dr. Diego Ramirez',
                'max_students': 25
            }
        ]
        
        created_courses = []
        for course_data in courses_data:
            course = Course.objects.create(**course_data)
            self.stdout.write(f"Curso creado: {course.name}")
            created_courses.append(course)
        
        return created_courses

    def create_schedules(self, monitors, rooms):
        """Crear turnos de minimo 3 horas para agosto y septiembre 2025"""
        self.stdout.write('Creando turnos...')
        
        # Fechas de agosto y septiembre 2025
        start_date = date(2025, 8, 1)
        end_date = date(2025, 9, 30)
        
        # Horarios de turnos (minimo 3 horas)
        shift_times = [
            {'start': '06:00', 'end': '10:00', 'name': 'Turno Madrugada'},
            {'start': '08:00', 'end': '12:00', 'name': 'Turno Manana'},
            {'start': '12:00', 'end': '16:00', 'name': 'Turno Tarde'},
            {'start': '14:00', 'end': '18:00', 'name': 'Turno Vespertino'},
            {'start': '16:00', 'end': '20:00', 'name': 'Turno Nocturno'},
            {'start': '18:00', 'end': '22:00', 'name': 'Turno Noche'}
        ]
        
        created_schedules = []
        current_date = start_date
        
        while current_date <= end_date:
            # Solo dias de semana (lunes a viernes)
            if current_date.weekday() < 5:
                # Crear 2-3 turnos por dia
                num_shifts = random.randint(2, 3)
                selected_shifts = random.sample(shift_times, num_shifts)
                
                for shift in selected_shifts:
                    # Seleccionar monitor aleatorio
                    monitor = random.choice(monitors)
                    
                    # Seleccionar sala aleatoria
                    room = random.choice(rooms)
                    
                    # Crear datetime para inicio y fin
                    start_time = datetime.combine(current_date, datetime.strptime(shift['start'], '%H:%M').time())
                    end_time = datetime.combine(current_date, datetime.strptime(shift['end'], '%H:%M').time())
                    
                    # Ajustar para timezone
                    start_time = timezone.make_aware(start_time)
                    end_time = timezone.make_aware(end_time)
                    
                    schedule = Schedule.objects.create(
                        user=monitor,
                        room=room,
                        start_datetime=start_time,
                        end_datetime=end_time,
                        status=random.choice(['active', 'completed']),
                        recurring=False,
                        notes=f"{shift['name']} - {monitor.get_full_name()} en {room.name}",
                        created_by=User.objects.filter(role=User.ADMIN).first()
                    )
                    created_schedules.append(schedule)
            
            current_date += timedelta(days=1)
        
        self.stdout.write(f"{len(created_schedules)} turnos creados")
        return created_schedules

    def create_room_entries(self, schedules):
        """Crear entradas y salidas con diferentes tipos de llegada"""
        self.stdout.write('Creando entradas y salidas...')
        
        entry_types = {
            'on_time': 0.6,      # 60% llegan a tiempo
            'early': 0.15,       # 15% llegan temprano
            'late': 0.25         # 25% llegan tarde
        }
        
        created_entries = []
        
        for schedule in schedules:
            if schedule.status == 'completed':
                # Determinar tipo de llegada
                rand = random.random()
                if rand < entry_types['on_time']:
                    # Llegada a tiempo (exacta o 5 minutos antes/despues)
                    entry_offset = random.randint(-5, 5)
                elif rand < entry_types['on_time'] + entry_types['early']:
                    # Llegada temprana (10-30 minutos antes)
                    entry_offset = -random.randint(10, 30)
                else:
                    # Llegada tarde (5-45 minutos despues)
                    entry_offset = random.randint(5, 45)
                
                # Calcular tiempo de entrada
                entry_time = schedule.start_datetime + timedelta(minutes=entry_offset)
                
                # Calcular tiempo de salida (puede salir antes o despues del turno)
                exit_offset = random.randint(-30, 60)  # -30 a +60 minutos
                exit_time = schedule.end_datetime + timedelta(minutes=exit_offset)
                
                # Crear entrada
                entry = RoomEntry.objects.create(
                    user=schedule.user,
                    room=schedule.room,
                    entry_time=entry_time,
                    exit_time=exit_time,
                    active=False,
                    notes=f"Turno {schedule.start_datetime.strftime('%d/%m/%Y %H:%M')} - {'Puntual' if entry_offset <= 5 else 'Temprano' if entry_offset < 0 else 'Tarde'}"
                )
                created_entries.append(entry)
        
        self.stdout.write(f"{len(created_entries)} entradas/salidas creadas")
        return created_entries

    def create_equipment_reports(self, equipment, monitors):
        """Crear reportes de problemas con equipos"""
        self.stdout.write('Creando reportes de equipos...')
        
        problem_types = [
            'No enciende',
            'Pantalla en blanco',
            'Teclado no funciona',
            'Mouse no responde',
            'Sin conexion a internet',
            'Sistema operativo lento',
            'Programa no abre',
            'Impresora no imprime',
            'Proyector no funciona',
            'Cable de red danado'
        ]
        
        severity_levels = ['low', 'medium', 'high', 'critical']
        
        created_reports = []
        
        # Crear 25-35 reportes
        num_reports = random.randint(25, 35)
        
        for i in range(num_reports):
            equipment_item = random.choice(equipment)
            monitor = random.choice(monitors)
            problem = random.choice(problem_types)
            severity = random.choice(severity_levels)
            
            # Fecha aleatoria en agosto-septiembre 2025
            report_date = date(2025, random.randint(8, 9), random.randint(1, 28))
            report_time = datetime.combine(report_date, datetime.strptime(f"{random.randint(6, 20)}:{random.randint(0, 59):02d}", '%H:%M').time())
            report_time = timezone.make_aware(report_time)
            
            report = EquipmentReport.objects.create(
                equipment=equipment_item,
                reported_by=monitor,
                report_date=report_time,
                problem_description=f"{problem} en {equipment_item.name}",
                severity=severity,
                status=random.choice(['reported', 'in_progress', 'resolved']),
                resolution_notes='Problema reportado y en proceso de resolucion' if severity in ['medium', 'high', 'critical'] else 'Problema menor, resuelto rapidamente',
                resolved_at=report_time + timedelta(hours=random.randint(1, 48)) if severity in ['low', 'medium'] else None
            )
            created_reports.append(report)
        
        self.stdout.write(f"{len(created_reports)} reportes de equipos creados")
        return created_reports

    def create_attendance_data(self, monitors):
        """Crear datos de asistencia"""
        self.stdout.write('Creando datos de asistencia...')
        
        # Crear algunos listados de asistencia
        attendance_dates = [
            date(2025, 8, 15),
            date(2025, 8, 30),
            date(2025, 9, 15),
            date(2025, 9, 30)
        ]
        
        created_attendance = []
        
        for attendance_date in attendance_dates:
            # Seleccionar monitor aleatorio para subir el listado
            uploader = random.choice(monitors)
            
            attendance = Attendance.objects.create(
                title=f"Listado de Asistencia - {attendance_date.strftime('%B %Y')}",
                date=attendance_date,
                uploaded_by=uploader,
                description=f"Listado de asistencia del mes de {attendance_date.strftime('%B %Y')}",
                reviewed=random.choice([True, False]),
                reviewed_by=User.objects.filter(role=User.ADMIN).first() if random.choice([True, False]) else None
            )
            created_attendance.append(attendance)
        
        self.stdout.write(f"{len(created_attendance)} listados de asistencia creados")
        return created_attendance

    def create_incapacity_data(self, monitors):
        """Crear datos de incapacidades"""
        self.stdout.write('Creando datos de incapacidades...')
        
        created_incapacities = []
        
        # Crear 4-6 incapacidades
        num_incapacities = random.randint(4, 6)
        
        for i in range(num_incapacities):
            monitor = random.choice(monitors)
            
            # Fecha de inicio aleatoria en agosto-septiembre
            start_date = date(2025, random.randint(8, 9), random.randint(1, 25))
            duration_days = random.randint(1, 5)
            end_date = start_date + timedelta(days=duration_days)
            
            incapacity = Incapacity.objects.create(
                user=monitor,
                start_date=start_date,
                end_date=end_date,
                description=f"Incapacidad medica por {random.choice(['gripe', 'dolor de cabeza', 'fiebre', 'resfriado', 'dolor de espalda'])}",
                approved=random.choice([True, False]),
                approved_by=User.objects.filter(role=User.ADMIN).first() if random.choice([True, False]) else None
            )
            created_incapacities.append(incapacity)
        
        self.stdout.write(f"{len(created_incapacities)} incapacidades creadas")
        return created_incapacities

    def create_notifications(self, monitors):
        """Crear notificaciones del sistema"""
        self.stdout.write('Creando notificaciones...')
        
        notification_types = [
            'schedule_reminder',
            'equipment_maintenance',
            'system_update',
            'meeting_reminder',
            'deadline_approaching'
        ]
        
        created_notifications = []
        
        # Crear 15-20 notificaciones
        num_notifications = random.randint(15, 20)
        
        for i in range(num_notifications):
            monitor = random.choice(monitors)
            notification_type = random.choice(notification_types)
            
            # Fecha aleatoria en agosto-septiembre
            notification_date = date(2025, random.randint(8, 9), random.randint(1, 28))
            notification_time = datetime.combine(notification_date, datetime.strptime(f"{random.randint(8, 18)}:{random.randint(0, 59):02d}", '%H:%M').time())
            notification_time = timezone.make_aware(notification_time)
            
            notification = Notification.objects.create(
                user=monitor,
                title=f"Notificacion {i+1}",
                message=f"Recordatorio importante del sistema - {notification_type}",
                notification_type=notification_type,
                created_at=notification_time,
                is_read=random.choice([True, False]),
                priority=random.choice(['low', 'medium', 'high'])
            )
            created_notifications.append(notification)
        
        self.stdout.write(f"{len(created_notifications)} notificaciones creadas")
        return created_notifications

