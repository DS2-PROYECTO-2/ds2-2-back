"""
Script para generar datos de prueba para el sistema de gestión de cursos
Ejecutar con: python manage.py shell < scripts/create_test_data.py
"""

from django.contrib.auth import get_user_model
from rooms.models import Room
from schedule.models import Schedule
from courses.models import Course
from django.utils import timezone
from datetime import datetime, timedelta
from rest_framework.authtoken.models import Token

print("🚀 Iniciando creación de datos de prueba...")

User = get_user_model()

# ===== 1. CREAR USUARIOS =====
print("\n👥 Creando usuarios...")

# Usuario Administrador
admin_user, created = User.objects.get_or_create(
    username='admin_test',
    defaults={
        'identification': '12345678',
        'email': 'admin@test.com',
        'first_name': 'Admin',
        'last_name': 'Pruebas',
        'role': 'admin',
        'is_verified': True
    }
)
if created:
    admin_user.set_password('admin123')
    admin_user.save()
    print(f"✅ Admin creado: {admin_user.username}")
else:
    print(f"ℹ️  Admin ya existe: {admin_user.username}")

# Usuario Monitor
monitor_user, created = User.objects.get_or_create(
    username='monitor_test',
    defaults={
        'identification': '87654321',
        'email': 'monitor@test.com',
        'first_name': 'Monitor',
        'last_name': 'Pruebas',
        'role': 'monitor',
        'is_verified': True
    }
)
if created:
    monitor_user.set_password('monitor123')
    monitor_user.save()
    print(f"✅ Monitor creado: {monitor_user.username}")
else:
    print(f"ℹ️  Monitor ya existe: {monitor_user.username}")

# Usuario Monitor 2
monitor_user2, created = User.objects.get_or_create(
    username='monitor_test2',
    defaults={
        'identification': '11223344',
        'email': 'monitor2@test.com',
        'first_name': 'Monitor2',
        'last_name': 'Pruebas',
        'role': 'monitor',
        'is_verified': True
    }
)
if created:
    monitor_user2.set_password('monitor123')
    monitor_user2.save()
    print(f"✅ Monitor2 creado: {monitor_user2.username}")
else:
    print(f"ℹ️  Monitor2 ya existe: {monitor_user2.username}")

# ===== 2. CREAR TOKENS =====
print("\n🔑 Creando tokens de autenticación...")

admin_token, created = Token.objects.get_or_create(user=admin_user)
monitor_token, created = Token.objects.get_or_create(user=monitor_user)
monitor_token2, created = Token.objects.get_or_create(user=monitor_user2)

print(f"🔐 Admin Token: {admin_token.key}")
print(f"🔐 Monitor Token: {monitor_token.key}")
print(f"🔐 Monitor2 Token: {monitor_token2.key}")

# ===== 3. CREAR SALAS =====
print("\n🏢 Creando salas...")

sala_a, created = Room.objects.get_or_create(
    code='SC-A01',
    defaults={
        'name': 'Sala de Computadores A',
        'capacity': 30,
        'description': 'Sala principal con 30 computadores'
    }
)
if created:
    print(f"✅ Sala creada: {sala_a.name}")
else:
    print(f"ℹ️  Sala ya existe: {sala_a.name}")

sala_b, created = Room.objects.get_or_create(
    code='SC-B02',
    defaults={
        'name': 'Sala de Conferencias B',
        'capacity': 50,
        'description': 'Sala para conferencias y presentaciones'
    }
)
if created:
    print(f"✅ Sala creada: {sala_b.name}")
else:
    print(f"ℹ️  Sala ya existe: {sala_b.name}")

sala_c, created = Room.objects.get_or_create(
    code='LAB-C03',
    defaults={
        'name': 'Laboratorio C',
        'capacity': 20,
        'description': 'Laboratorio especializado'
    }
)
if created:
    print(f"✅ Sala creada: {sala_c.name}")
else:
    print(f"ℹ️  Sala ya existe: {sala_c.name}")

# ===== 4. CREAR HORARIOS =====
print("\n📅 Creando horarios de monitores...")

now = timezone.now()
tomorrow = now + timedelta(days=1)
day_after = now + timedelta(days=2)
next_week = now + timedelta(days=7)

# Horario Monitor 1 - Mañana
schedule1, created = Schedule.objects.get_or_create(
    user=monitor_user,
    room=sala_a,
    start_datetime=tomorrow.replace(hour=8, minute=0, second=0, microsecond=0),
    defaults={
        'end_datetime': tomorrow.replace(hour=12, minute=0, second=0, microsecond=0),
        'created_by': admin_user,
        'status': 'active'
    }
)
if created:
    print(f"✅ Horario creado: {monitor_user.first_name} - {schedule1.start_datetime}")
else:
    print(f"ℹ️  Horario ya existe: {monitor_user.first_name} - {schedule1.start_datetime}")

# Horario Monitor 1 - Tarde
schedule2, created = Schedule.objects.get_or_create(
    user=monitor_user,
    room=sala_a,
    start_datetime=day_after.replace(hour=14, minute=0, second=0, microsecond=0),
    defaults={
        'end_datetime': day_after.replace(hour=18, minute=0, second=0, microsecond=0),
        'created_by': admin_user,
        'status': 'active'
    }
)
if created:
    print(f"✅ Horario creado: {monitor_user.first_name} - {schedule2.start_datetime}")

# Horario Monitor 2
schedule3, created = Schedule.objects.get_or_create(
    user=monitor_user2,
    room=sala_b,
    start_datetime=tomorrow.replace(hour=9, minute=0, second=0, microsecond=0),
    defaults={
        'end_datetime': tomorrow.replace(hour=13, minute=0, second=0, microsecond=0),
        'created_by': admin_user,
        'status': 'active'
    }
)
if created:
    print(f"✅ Horario creado: {monitor_user2.first_name} - {schedule3.start_datetime}")

# ===== 5. CREAR CURSOS =====
print("\n🎓 Creando cursos de ejemplo...")

# Curso 1 - Programado
curso1, created = Course.objects.get_or_create(
    name='Introducción a Python',
    defaults={
        'description': 'Curso básico de programación en Python para principiantes. Incluye conceptos fundamentales, estructuras de datos y programación orientada a objetos.',
        'room': sala_a,
        'monitor': monitor_user,
        'schedule': schedule1,
        'start_datetime': tomorrow.replace(hour=9, minute=0, second=0, microsecond=0),
        'end_datetime': tomorrow.replace(hour=11, minute=0, second=0, microsecond=0),
        'status': 'scheduled',
        'created_by': admin_user
    }
)
if created:
    print(f"✅ Curso creado: {curso1.name}")

# Curso 2 - Programado
curso2, created = Course.objects.get_or_create(
    name='Desarrollo Web con Django',
    defaults={
        'description': 'Curso avanzado de desarrollo web usando Django framework. Cubre modelos, vistas, templates y API REST.',
        'room': sala_a,
        'monitor': monitor_user,
        'schedule': schedule1,
        'start_datetime': tomorrow.replace(hour=11, minute=30, second=0, microsecond=0),
        'end_datetime': tomorrow.replace(hour=12, minute=0, second=0, microsecond=0),
        'status': 'scheduled',
        'created_by': admin_user
    }
)
if created:
    print(f"✅ Curso creado: {curso2.name}")

# Curso 3 - En progreso
curso3, created = Course.objects.get_or_create(
    name='Base de Datos Relacionales',
    defaults={
        'description': 'Curso de diseño y administración de bases de datos relacionales con PostgreSQL y MySQL.',
        'room': sala_b,
        'monitor': monitor_user2,
        'schedule': schedule3,
        'start_datetime': now.replace(hour=10, minute=0, second=0, microsecond=0),
        'end_datetime': now.replace(hour=12, minute=30, second=0, microsecond=0),
        'status': 'in_progress',
        'created_by': admin_user
    }
)
if created:
    print(f"✅ Curso creado: {curso3.name}")

# Curso 4 - Completado
curso4, created = Course.objects.get_or_create(
    name='Git y Control de Versiones',
    defaults={
        'description': 'Curso completo de Git para control de versiones, trabajo en equipo y flujos de trabajo colaborativos.',
        'room': sala_a,
        'monitor': monitor_user,
        'schedule': schedule2,
        'start_datetime': now.replace(hour=15, minute=0, second=0, microsecond=0) - timedelta(days=1),
        'end_datetime': now.replace(hour=17, minute=0, second=0, microsecond=0) - timedelta(days=1),
        'status': 'completed',
        'created_by': admin_user
    }
)
if created:
    print(f"✅ Curso creado: {curso4.name}")

# Curso 5 - Próximo (siguiente semana)
curso5, created = Course.objects.get_or_create(
    name='Testing Automatizado',
    defaults={
        'description': 'Curso de pruebas automatizadas con pytest, unittest y testing de APIs REST.',
        'room': sala_c,
        'monitor': monitor_user2,
        'schedule': schedule3,
        'start_datetime': next_week.replace(hour=10, minute=0, second=0, microsecond=0),
        'end_datetime': next_week.replace(hour=13, minute=0, second=0, microsecond=0),
        'status': 'scheduled',
        'created_by': admin_user
    }
)
if created:
    print(f"✅ Curso creado: {curso5.name}")

# ===== 6. RESUMEN FINAL =====
print("\n📊 Resumen de datos creados:")
print(f"👥 Usuarios: {User.objects.filter(username__contains='test').count()}")
print(f"🏢 Salas: {Room.objects.filter(code__startswith='SC-').count() + Room.objects.filter(code__startswith='LAB-').count()}")
print(f"📅 Horarios: {Schedule.objects.filter(created_by=admin_user).count()}")
print(f"🎓 Cursos: {Course.objects.filter(created_by=admin_user).count()}")

print("\n🔑 Credenciales de prueba:")
print("=" * 50)
print("ADMIN:")
print(f"  Usuario: admin_test")
print(f"  Password: admin123")
print(f"  Token: {admin_token.key}")
print("\nMONITOR 1:")
print(f"  Usuario: monitor_test")
print(f"  Password: monitor123")
print(f"  Token: {monitor_token.key}")
print("\nMONITOR 2:")
print(f"  Usuario: monitor_test2")
print(f"  Password: monitor123")
print(f"  Token: {monitor_token2.key}")

print("\n🚀 URLs de prueba:")
print("=" * 50)
print("GET    http://127.0.0.1:8000/api/courses/")
print("POST   http://127.0.0.1:8000/api/courses/")
print("GET    http://127.0.0.1:8000/api/courses/my_courses/")
print("GET    http://127.0.0.1:8000/api/courses/upcoming/")
print("GET    http://127.0.0.1:8000/api/courses/current/")
print("GET    http://127.0.0.1:8000/api/admin/courses/overview/")

print("\n✅ ¡Datos de prueba creados exitosamente!")
print("💡 Tip: Guarda los tokens para usar en Postman o cURL")