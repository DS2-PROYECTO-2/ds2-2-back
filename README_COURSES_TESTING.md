# **Guía de Pruebas - API de Gestión de Cursos**

## **🔧 Configuración Inicial**

### **1. Ejecutar Migraciones**
```bash
python manage.py makemigrations
python manage.py migrate
```

### **2. Crear Superusuario**
```bash
python manage.py createsuperuser
```

### **3. Ejecutar Servidor**
```bash
python manage.py runserver
```

---

## **👥 Datos de Usuario para Pruebas**

### **Crear Usuario Administrador**
```bash
# En Django Shell (python manage.py shell)
from django.contrib.auth import get_user_model
User = get_user_model()

admin_user = User.objects.create_user(
    identification='12345678',
    username='admin_test',
    email='admin@test.com',
    password='admin123',
    first_name='Admin',
    last_name='Pruebas',
    role='admin',
    is_verified=True
)
```

### **Crear Usuario Monitor**
```bash
# En Django Shell (python manage.py shell)
monitor_user = User.objects.create_user(
    identification='87654321',
    username='monitor_test',
    email='monitor@test.com',
    password='monitor123',
    first_name='Monitor',
    last_name='Pruebas',
    role='monitor',
    is_verified=True
)
```

---

## **🏢 Datos de Sala para Pruebas**

### **Crear Salas**
```bash
# En Django Shell (python manage.py shell)
from rooms.models import Room

# Sala 1
sala_a = Room.objects.create(
    name='Sala de Computadores A',
    code='SC-A01',
    capacity=30,
    description='Sala principal con 30 computadores'
)

# Sala 2
sala_b = Room.objects.create(
    name='Sala de Conferencias B',
    code='SC-B02',
    capacity=50,
    description='Sala para conferencias y presentaciones'
)

# Sala 3
sala_c = Room.objects.create(
    name='Laboratorio C',
    code='LAB-C03',
    capacity=20,
    description='Laboratorio especializado'
)
```

---

## **📅 Datos de Horarios para Pruebas**

### **Crear Horarios de Monitor**
```bash
# En Django Shell (python manage.py shell)
from schedule.models import Schedule
from django.utils import timezone
from datetime import datetime, timedelta

# Obtener usuarios y sala
from django.contrib.auth import get_user_model
from rooms.models import Room
User = get_user_model()

admin_user = User.objects.get(username='admin_test')
monitor_user = User.objects.get(username='monitor_test')
sala_a = Room.objects.get(code='SC-A01')

# Horario de Lunes
lunes_schedule = Schedule.objects.create(
    user=monitor_user,
    room=sala_a,
    start_datetime=timezone.now().replace(hour=8, minute=0, second=0, microsecond=0) + timedelta(days=1),
    end_datetime=timezone.now().replace(hour=12, minute=0, second=0, microsecond=0) + timedelta(days=1),
    created_by=admin_user,
    status='active'
)

# Horario de Martes  
martes_schedule = Schedule.objects.create(
    user=monitor_user,
    room=sala_a,
    start_datetime=timezone.now().replace(hour=14, minute=0, second=0, microsecond=0) + timedelta(days=2),
    end_datetime=timezone.now().replace(hour=18, minute=0, second=0, microsecond=0) + timedelta(days=2),
    created_by=admin_user,
    status='active'
)
```

---

## **🎓 Datos de Cursos para Pruebas**

### **Script Completo de Datos**
```python
# Ejecutar en Django Shell (python manage.py shell)

from django.contrib.auth import get_user_model
from rooms.models import Room
from schedule.models import Schedule
from courses.models import Course
from django.utils import timezone
from datetime import datetime, timedelta

User = get_user_model()

# 1. Crear usuarios si no existen
try:
    admin_user = User.objects.get(username='admin_test')
except User.DoesNotExist:
    admin_user = User.objects.create_user(
        identification='12345678',
        username='admin_test',
        email='admin@test.com',
        password='admin123',
        first_name='Admin',
        last_name='Pruebas',
        role='admin',
        is_verified=True
    )

try:
    monitor_user = User.objects.get(username='monitor_test')
except User.DoesNotExist:
    monitor_user = User.objects.create_user(
        identification='87654321',
        username='monitor_test',
        email='monitor@test.com',
        password='monitor123',
        first_name='Monitor',
        last_name='Pruebas',
        role='monitor',
        is_verified=True
    )

# 2. Crear salas si no existen
sala_a, created = Room.objects.get_or_create(
    code='SC-A01',
    defaults={
        'name': 'Sala de Computadores A',
        'capacity': 30,
        'description': 'Sala principal con 30 computadores'
    }
)

# 3. Crear horario de monitor
now = timezone.now()
tomorrow = now + timedelta(days=1)

schedule1 = Schedule.objects.create(
    user=monitor_user,
    room=sala_a,
    start_datetime=tomorrow.replace(hour=8, minute=0, second=0, microsecond=0),
    end_datetime=tomorrow.replace(hour=12, minute=0, second=0, microsecond=0),
    created_by=admin_user,
    status='active'
)

# 4. Crear cursos de ejemplo
curso1 = Course.objects.create(
    name='Introducción a Python',
    description='Curso básico de programación en Python para principiantes',
    room=sala_a,
    monitor=monitor_user,
    schedule=schedule1,
    start_datetime=tomorrow.replace(hour=9, minute=0, second=0, microsecond=0),
    end_datetime=tomorrow.replace(hour=11, minute=0, second=0, microsecond=0),
    status='scheduled',
    created_by=admin_user
)

curso2 = Course.objects.create(
    name='Desarrollo Web con Django',
    description='Curso avanzado de desarrollo web usando Django framework',
    room=sala_a,
    monitor=monitor_user,
    schedule=schedule1,
    start_datetime=tomorrow.replace(hour=11, minute=30, second=0, microsecond=0),
    end_datetime=tomorrow.replace(hour=12, minute=0, second=0, microsecond=0),
    status='scheduled',
    created_by=admin_user
)

print("✅ Datos de prueba creados exitosamente:")
print(f"- Admin: {admin_user.username}")
print(f"- Monitor: {monitor_user.username}")
print(f"- Sala: {sala_a.name}")
print(f"- Horario: {schedule1.start_datetime}")
print(f"- Cursos creados: {Course.objects.count()}")
```

---

## **🔑 Obtener Tokens de Autenticación**

### **Crear Tokens para Testing**
```python
# En Django Shell (python manage.py shell)
from rest_framework.authtoken.models import Token
from django.contrib.auth import get_user_model

User = get_user_model()

# Token para admin
admin_user = User.objects.get(username='admin_test')
admin_token, created = Token.objects.get_or_create(user=admin_user)
print(f"Admin Token: {admin_token.key}")

# Token para monitor
monitor_user = User.objects.get(username='monitor_test')
monitor_token, created = Token.objects.get_or_create(user=monitor_user)
print(f"Monitor Token: {monitor_token.key}")
```

---

## **📋 Ejemplos de Testing con Postman/cURL**

### **Headers Requeridos**
```
Authorization: Token TU_TOKEN_AQUI
Content-Type: application/json
```

### **1. Listar Cursos (GET /api/courses/)**
```bash
curl -H "Authorization: Token TU_ADMIN_TOKEN" \
     -H "Content-Type: application/json" \
     http://127.0.0.1:8000/api/courses/
```

### **2. Crear Curso (POST /api/courses/)**
```bash
curl -X POST \
     -H "Authorization: Token TU_ADMIN_TOKEN" \
     -H "Content-Type: application/json" \
     -d '{
         "name": "Curso de Prueba API",
         "description": "Curso creado desde la API para testing",
         "room": 1,
         "monitor": 2,
         "schedule": 1,
         "start_datetime": "2025-10-12T10:00:00Z",
         "end_datetime": "2025-10-12T12:00:00Z"
     }' \
     http://127.0.0.1:8000/api/courses/
```

### **3. Cursos del Monitor (GET /api/courses/my_courses/)**
```bash
curl -H "Authorization: Token TU_MONITOR_TOKEN" \
     -H "Content-Type: application/json" \
     http://127.0.0.1:8000/api/courses/my_courses/
```

### **4. Próximos Cursos (GET /api/courses/upcoming/)**
```bash
curl -H "Authorization: Token TU_TOKEN" \
     -H "Content-Type: application/json" \
     http://127.0.0.1:8000/api/courses/upcoming/
```

### **5. Dashboard Admin (GET /api/admin/courses/overview/)**
```bash
curl -H "Authorization: Token TU_ADMIN_TOKEN" \
     -H "Content-Type: application/json" \
     http://127.0.0.1:8000/api/admin/courses/overview/
```

### **6. Historial de Curso (GET /api/courses/1/history/)**
```bash
curl -H "Authorization: Token TU_TOKEN" \
     -H "Content-Type: application/json" \
     http://127.0.0.1:8000/api/courses/1/history/
```

---

## **🧪 Casos de Prueba Específicos**

### **Caso 1: Conflicto de Sala**
```json
POST /api/courses/
{
    "name": "Curso Conflictivo",
    "description": "Este curso debería fallar por conflicto",
    "room": 1,
    "monitor": 2,
    "schedule": 1,
    "start_datetime": "2025-10-12T09:30:00Z",
    "end_datetime": "2025-10-12T11:30:00Z"
}
```
**Resultado Esperado:** Error 400 con mensaje de conflicto

### **Caso 2: Monitor No Disponible**
```json
POST /api/courses/
{
    "name": "Curso Sin Monitor",
    "description": "Monitor no tiene horario en esta fecha",
    "room": 1,
    "monitor": 2,
    "schedule": 1,
    "start_datetime": "2025-10-15T15:00:00Z",
    "end_datetime": "2025-10-15T17:00:00Z"
}
```
**Resultado Esperado:** Error 400 con mensaje de disponibilidad

### **Caso 3: Permisos de Monitor**
```bash
# Monitor intenta crear curso (debería fallar)
curl -X POST \
     -H "Authorization: Token TU_MONITOR_TOKEN" \
     -H "Content-Type: application/json" \
     -d '{"name": "Curso Denegado", ...}' \
     http://127.0.0.1:8000/api/courses/
```
**Resultado Esperado:** Error 403 Forbidden

---

## **📊 Validaciones a Probar**

### **✅ Validaciones Exitosas**
- [x] Curso con datos válidos se crea correctamente
- [x] Monitor ve solo sus cursos asignados
- [x] Admin ve todos los cursos
- [x] Historial se crea automáticamente
- [x] Estados de curso se actualizan correctamente

### **❌ Validaciones de Error**
- [x] Conflicto de sala genera error 400
- [x] Monitor sin permisos genera error 403
- [x] Fechas inválidas generan error 400
- [x] Duración fuera de límites genera error 400
- [x] Monitor no verificado genera error 400

---

## **🔄 Comandos de Limpieza**

### **Limpiar Datos de Prueba**
```python
# En Django Shell (python manage.py shell)
from courses.models import Course, CourseHistory
from schedule.models import Schedule
from rooms.models import Room
from django.contrib.auth import get_user_model

User = get_user_model()

# Limpiar cursos
Course.objects.filter(created_by__username='admin_test').delete()
CourseHistory.objects.all().delete()

# Limpiar horarios de prueba
Schedule.objects.filter(created_by__username='admin_test').delete()

# Limpiar usuarios de prueba
User.objects.filter(username__in=['admin_test', 'monitor_test']).delete()

# Limpiar salas de prueba
Room.objects.filter(code__startswith='SC-').delete()

print("🧹 Datos de prueba eliminados")
```

---

## **📝 Checklist de Testing**

### **Funcionalidades Básicas**
- [ ] Crear curso como admin
- [ ] Listar cursos como admin
- [ ] Listar cursos como monitor (solo propios)
- [ ] Ver detalle de curso
- [ ] Actualizar curso como admin
- [ ] Eliminar curso como admin

### **Validaciones**
- [ ] Conflicto de sala rechazado
- [ ] Monitor sin horario rechazado
- [ ] Permisos de monitor respetados
- [ ] Duraciones válidas aceptadas
- [ ] Duraciones inválidas rechazadas

### **Endpoints Especiales**
- [ ] Dashboard de monitor (/my_courses/)
- [ ] Cursos próximos (/upcoming/)
- [ ] Cursos actuales (/current/)
- [ ] Historial de curso (/history/)
- [ ] Dashboard admin (/admin/courses/overview/)

### **Auditoría**
- [ ] Historial se crea al crear curso
- [ ] Historial se crea al actualizar curso
- [ ] Historial se crea al eliminar curso
- [ ] Usuario correcto en historial

¡Con esta guía tendrás todo lo necesario para probar exhaustivamente el sistema de gestión de cursos! 🚀