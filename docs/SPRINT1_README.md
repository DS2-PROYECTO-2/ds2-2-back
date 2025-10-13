# Sprint 1 - Autenticación y Dashboard

## 🎯 Funcionalidades Implementadas

### ✅ Sistema Completo de Autenticación
- **Registro de usuarios**: Monitores y administradores con validación completa
- **Login/logout**: Autenticación basada en tokens JWT/Token
- **Gestión de perfiles**: Visualización y actualización de datos personales
- **Cambio de contraseñas**: Con validación de contraseña actual

### ✅ Sistema de Verificación de Usuarios
- **Notificación automática**: Los administradores reciben notificaciones cuando un monitor se registra
- **Control de acceso**: Los monitores no pueden acceder hasta ser verificados
- **Panel de administrador**: Aprobar/rechazar usuarios desde el dashboard
- **Confirmación automática**: Los usuarios reciben notificación tras aprobación

### ✅ Dashboard Diferenciado por Roles
- **Dashboard de Administrador**: 
  - Estadísticas de usuarios totales
  - Verificaciones pendientes
  - Total de monitores
  - Monitores verificados
- **Dashboard de Monitor**: 
  - Estado de verificación
  - Información personal
  - Acceso a salas disponibles

## 🛠️ Arquitectura Técnica

### Modelos Implementados
```python
# users/models.py
class User(AbstractUser):
    role = CharField(choices=['admin', 'monitor'])
    identification = CharField(unique=True)
    is_verified = BooleanField(default=False)
    verified_by = ForeignKey('self')
    verification_date = DateTimeField()

# rooms/models.py  
class Room(Model):
    name = CharField()
    code = CharField(unique=True)
    capacity = IntegerField()
    is_active = BooleanField()

# notifications/models.py
class Notification(Model):
    user = ForeignKey(User)
    notification_type = CharField()
    title = CharField()
    message = TextField()
    read = BooleanField(default=False)
```

### Endpoints de API

#### Autenticación (`/api/auth/`)
- `POST /register/` - Registro de usuarios
- `POST /login/` - Inicio de sesión  
- `POST /logout/` - Cierre de sesión
- `GET /profile/` - Obtener perfil del usuario
- `PUT /profile/update/` - Actualizar perfil
- `POST /change-password/` - Cambiar contraseña
- `GET /dashboard/` - Dashboard diferenciado por rol

#### Administración (`/api/auth/admin/`)
- `GET /users/` - Lista de usuarios (filtrable)
- `PATCH /users/{id}/verify/` - Verificar/rechazar usuario

#### Salas (`/api/rooms/`)
- `GET /` - Lista de salas activas
- `GET /{id}/` - Detalle de sala específica

### Sistema de Permisos
```python
# users/permissions.py
class IsAdminUser(BasePermission):
    """Solo administradores verificados"""
    
class IsVerifiedUser(BasePermission):  
    """Usuarios verificados (admin o monitor)"""
    
class IsMonitorUser(BasePermission):
    """Monitores verificados"""
```

### Notificaciones Automáticas
- **Signal post_save**: Notifica a admins cuando se registra un monitor
- **Signal de verificación**: Notifica al usuario cuando es verificado
- **Sistema escalable**: Base para notificaciones en tiempo real

## 🔧 Configuración y Uso

### Requisitos
```txt
Django>=4.2,<5.0
djangorestframework==3.14.0
django-cors-headers==4.9.0
```

### 🚀 Instalación Automática (RECOMENDADA)
```bash
# 1. Clonar y configurar
git clone <repo-url>
cd ds2-2-back

# 2. Ejecutar configuración automática
python setup_project.py

# 3. Iniciar servidor
python manage.py runserver
```

**Credenciales automáticas:**
- Usuario: `admin` / Contraseña: `admin123`
- Email: `admin@ds2.com`

### 🔧 Instalación Manual (Alternativa)
```bash
# 1. Clonar y configurar entorno
git clone <repo-url>
cd ds2-2-back
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows

# 2. Instalar dependencias
pip install -r requirements.txt

# 3. Configurar base de datos
python manage.py makemigrations
python manage.py migrate

# 4. Crear superusuario (administrador)
python manage.py createsuperuser

# 5. Ejecutar servidor
python manage.py runserver
```

### 🧪 Verificación Automática
```bash
# Verificar que todos los endpoints funcionen
python test_endpoints.py
```

### Configuraciones Importantes
```python
# settings.py
AUTH_USER_MODEL = 'users.User'

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
}

CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",  # React
    "http://localhost:4200",  # Angular
]
```

## 🧪 Testing de APIs

### Registro de Monitor
```bash
POST /api/auth/register/
Content-Type: application/json

{
  "username": "monitor1",
  "email": "monitor@test.com", 
  "password": "password123",
  "password_confirm": "password123",
  "first_name": "Juan",
  "last_name": "Pérez", 
  "identification": "12345678",
  "phone": "3001234567",
  "role": "monitor"
}

# Respuesta
{
  "message": "Usuario registrado exitosamente. Esperando verificación del administrador.",
  "user": {
    "id": 1,
    "username": "monitor1",
    "email": "monitor@test.com",
    "role": "monitor", 
    "is_verified": false
  }
}
```

### Login
```bash
POST /api/auth/login/
Content-Type: application/json

{
  "username": "monitor1",
  "password": "password123"
}

# Respuesta (si está verificado)
{
  "message": "Login exitoso",
  "token": "9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b",
  "user": {
    "id": 1,
    "username": "monitor1",
    "role": "monitor",
    "is_verified": true
  }
}
```

### Dashboard
```bash
GET /api/auth/dashboard/
Authorization: Token 9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b

# Respuesta para Admin
{
  "user": {...},
  "dashboard_type": "admin",
  "stats": {
    "total_users": 5,
    "pending_verifications": 2, 
    "total_monitors": 3,
    "verified_monitors": 1
  },
  "message": "Bienvenido al panel de administrador, Juan Admin"
}

# Respuesta para Monitor
{
  "user": {...},
  "dashboard_type": "monitor", 
  "stats": {
    "account_status": "verified",
    "verification_date": "2025-01-15T10:30:00Z"
  },
  "message": "Bienvenido, Juan Pérez"
}
```

### Verificación de Usuario (Solo Admin)
```bash
PATCH /api/auth/admin/users/1/verify/
Authorization: Token admin_token
Content-Type: application/json

{
  "is_verified": true
}

# Respuesta
{
  "message": "Usuario monitor1 actualizado exitosamente",
  "user": {
    "id": 1,
    "username": "monitor1", 
    "is_verified": true,
    "verification_date": "2025-01-15T10:30:00Z"
  }
}
```

## 🎯 Validaciones Implementadas

### Registro
- ✅ Contraseñas coincidentes
- ✅ Identificación única  
- ✅ Email válido y único
- ✅ Campos obligatorios
- ✅ Verificación automática de admins

### Login
- ✅ Credenciales válidas
- ✅ Cuenta activa
- ✅ Verificación requerida para monitores
- ✅ Generación de token de autenticación

### Permisos
- ✅ Solo admins pueden verificar usuarios
- ✅ Solo usuarios verificados acceden al sistema
- ✅ Dashboard diferenciado por rol
- ✅ Protección de endpoints sensibles

## 🚀 Próximos Sprints

### Sprint 2 - Control de Ingreso/Salida
- Registro de entrada/salida de monitores
- Validación de simultaneidad (no en 2 salas)
- Cálculo automático de horas trabajadas
- Historial de entradas por monitor

### Sprint 3 - Gestión Completa  
- Gestión de equipos y reportes de fallas
- Subida de listados de asistencia
- Exportación de reportes (PDF/Excel)
- Integración con calendario de turnos
- Notificaciones en tiempo real

## 📁 Estructura del Proyecto

```
ds2-2-back/
├── users/                    # 🔐 Autenticación y usuarios
│   ├── models.py            # Modelo User personalizado
│   ├── serializers.py       # APIs de auth y perfil
│   ├── views.py             # Vistas de auth y dashboard
│   ├── permissions.py       # Permisos por rol
│   ├── managers.py          # Manager personalizado  
│   ├── signals.py           # Notificaciones automáticas
│   └── urls.py              # Rutas de autenticación
├── rooms/                   # 🏢 Gestión de salas  
│   ├── models.py            # Modelo Room
│   ├── serializers.py       # API de salas
│   ├── views.py             # Lista y detalle de salas
│   └── urls.py              # Rutas de salas
├── notifications/           # 🔔 Sistema de notificaciones
│   ├── models.py            # Modelo Notification
│   ├── serializers.py       # API de notificaciones
│   ├── views.py             # CRUD de notificaciones
│   └── urls.py              # Rutas de notificaciones
├── ds2_back/               # ⚙️ Configuración principal
│   ├── settings.py          # Configuración Django/DRF
│   └── urls.py              # URLs principales
├── requirements.txt         # 📦 Dependencias
├── README.md               # 📖 Documentación general
└── ER_GUIDE.md             # 📊 Guía para diagramas ER
```

Este Sprint 1 implementa una base sólida y escalable para el sistema completo de "Registro Monitores UV", cumpliendo todos los requisitos especificados con una arquitectura robusta y bien documentada.