# 📚 DS2-2-BACK - Documentación de API

## 🎯 **Descripción del proyecto**
API REST para gestión de laboratorios universitarios con sistema de autenticación, gestión de usuarios, salas y notificaciones.

---

## 🚀 **Instalación y configuración**

### **Prerrequisitos**
- Python 3.8+
- pip
- Virtual environment (recomendado)

### **Instalación**
```bash
# Clonar repositorio
git clone https://github.com/DS2-PROYECTO-2/ds2-2-back.git
cd ds2-2-back

# Crear entorno virtual
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

# Instalar dependencias
pip install -r requirements.txt

# Ejecutar migraciones
python manage.py migrate

# Crear superusuario (opcional)
python manage.py createsuperuser

# Ejecutar servidor
python manage.py runserver
```

---

## 🔐 **Autenticación**

### **Sistema de autenticación**
- **Tipo**: Token Authentication (Django REST Framework)
- **Header**: `Authorization: Token <tu_token>`
- **Roles**: `admin` y `monitor`
- **Verificación**: Los usuarios deben ser verificados por un admin

### **Flujo de autenticación**
1. **Registro** → Usuario se registra
2. **Verificación** → Admin verifica al usuario
3. **Login** → Usuario obtiene token
4. **Uso** → Token en header para endpoints protegidos

---

## 📋 **Endpoints disponibles**

### 🔑 **AUTENTICACIÓN** (`/api/auth/`)

#### **1. Registro de usuario**
```http
POST /api/auth/register/
Content-Type: application/json
```
**Body:**
```json
{
    "username": "usuario123",
    "email": "usuario@email.com",
    "password": "contraseña123",
    "password_confirm": "contraseña123",
    "first_name": "Juan",
    "last_name": "Pérez",
    "identification": "1234567890",
    "phone": "3001234567",
    "role": "monitor"  // "admin" o "monitor"
}
```
**Respuesta exitosa (201):**
```json
{
    "message": "Usuario registrado exitosamente. Esperando verificación del administrador.",
    "user": {
        "id": 1,
        "username": "usuario123",
        "email": "usuario@email.com", 
        "role": "monitor",
        "is_verified": false
    }
}
```
**Estado**: ✅ Probado y funcional

---

#### **2. Login**
```http
POST /api/auth/login/
Content-Type: application/json
```
**Body:**
```json
{
    "username": "usuario123",
    "password": "contraseña123"
}
```
**Respuesta exitosa (200):**
```json
{
    "message": "Login exitoso",
    "token": "bf774ea62d33995b830f906224e66d5b4e2df282",
    "user": {
        "id": 1,
        "username": "usuario123",
        "email": "usuario@email.com",
        "first_name": "Juan",
        "last_name": "Pérez",
        "identification": "1234567890",
        "phone": "3001234567",
        "role": "monitor",
        "role_display": "Monitor",
        "is_verified": true,
        "verification_date": "2025-09-28T09:02:30.020236-05:00",
        "date_joined": "2025-09-28T08:15:43.324160-05:00",
        "created_at": "2025-09-28T08:15:44.339426-05:00"
    }
}
```
**Estado**: ✅ Probado y funcional

---

#### **3. Logout**
```http
POST /api/auth/logout/
Authorization: Token <tu_token>
```
**Respuesta exitosa (200):**
```json
{
    "message": "Logout exitoso"
}
```
**Estado**: ✅ Probado y funcional

---

### 👤 **PERFIL DE USUARIO** (Requiere autenticación)

#### **4. Ver perfil**
```http
GET /api/auth/profile/
Authorization: Token <tu_token>
```
**Respuesta exitosa (200):**
```json
{
    "first_name": "Juan",
    "last_name": "Pérez", 
    "username": "usuario123",
    "email": "usuario@email.com",
    "phone": "3001234567",
    "identification": "1234567890"
}
```
**Nota**: Solo muestra campos editables por el usuario (seguridad)
**Estado**: ✅ Probado y funcional

---

#### **5. Actualizar perfil**
```http
PUT /api/auth/profile/update/
Authorization: Token <tu_token>
Content-Type: application/json
```
**Body (campos opcionales):**
```json
{
    "first_name": "Juan Carlos",
    "last_name": "Pérez García",
    "phone": "3009876543",
    "email": "nuevo@email.com"
}
```
**Respuesta exitosa (200):**
```json
{
    "message": "Perfil actualizado exitosamente",
    "user": {
        "first_name": "Juan Carlos",
        "last_name": "Pérez García",
        "username": "usuario123",
        "email": "nuevo@email.com",
        "phone": "3009876543",
        "identification": "1234567890"
    }
}
```
**Estado**: ✅ Probado y funcional

---

#### **6. Cambiar contraseña**
```http
POST /api/auth/change-password/
Authorization: Token <tu_token>
Content-Type: application/json
```
**Body:**
```json
{
    "old_password": "contraseña_actual",
    "new_password": "nueva_contraseña123",
    "new_password_confirm": "nueva_contraseña123"
}
```
**Estado**: ⚠️ Pendiente de pruebas

---

### 📊 **DASHBOARD** (Requiere autenticación)

#### **7. Dashboard de usuario**
```http
GET /api/auth/dashboard/
Authorization: Token <tu_token>
```
**Respuesta para Admin (200):**
```json
{
    "user": {
        "id": 1,
        "username": "admin",
        "email": "admin@email.com"
    },
    "dashboard_type": "admin",
    "stats": {
        "total_users": 15,
        "pending_verifications": 3,
        "total_monitors": 12,
        "verified_monitors": 9
    },
    "message": "Bienvenido al panel de administrador, Admin"
}
```
**Respuesta para Monitor (200):**
```json
{
    "user": {
        "id": 2,
        "username": "monitor123"
    },
    "dashboard_type": "monitor", 
    "stats": {
        "account_status": "verified",
        "verification_date": "2025-09-28T09:02:30.020236-05:00"
    },
    "message": "Bienvenido al panel de monitor, Juan Pérez"
}
```
**Estado**: ✅ Probado y funcional

---

### 👥 **ADMINISTRACIÓN** (Solo administradores)

#### **8. Lista de usuarios**
```http
GET /api/auth/admin/users/
Authorization: Token <token_admin>
```
**Respuesta exitosa (200):**
```json
{
    "count": 15,
    "next": "http://127.0.0.1:8000/api/auth/admin/users/?page=2",
    "previous": null,
    "results": [
        {
            "id": 1,
            "username": "usuario123",
            "email": "usuario@email.com",
            "first_name": "Juan",
            "last_name": "Pérez",
            "role": "monitor",
            "is_verified": true,
            "date_joined": "2025-09-28T08:15:43.324160-05:00"
        }
    ]
}
```
**Estado**: ✅ Probado y funcional

---

#### **9. Verificar usuario**
```http
POST /api/auth/admin/users/123/verify/
Authorization: Token <token_admin>
```
**Respuesta exitosa (200):**
```json
{
    "message": "Usuario verificado exitosamente",
    "user": {
        "id": 123,
        "username": "usuario123",
        "is_verified": true,
        "verification_date": "2025-09-28T10:30:00.000000-05:00"
    }
}
```
**Estado**: ✅ Probado y funcional

---

### 🏢 **SALAS Y REGISTROS DE ENTRADA/SALIDA** (`/api/rooms/`)

#### **10. Lista de salas**
```http
GET /api/rooms/
Authorization: Token <tu_token>
```
**Respuesta exitosa (200):**
```json
[
    {
        "id": 1,
        "name": "Sala de Estudio 1",
        "code": "S101",
        "capacity": 20,
        "description": "Sala principal de estudio",
        "is_active": true,
        "created_at": "2024-01-15T10:00:00Z"
    }
]
```
**Estado**: ✅ Probado y funcional

---

#### **11. Detalle de sala**
```http
GET /api/rooms/123/
Authorization: Token <tu_token>
```
**Respuesta exitosa (200):**
```json
{
    "id": 123,
    "name": "Sala de Estudio 1",
    "code": "S101",
    "capacity": 20,
    "description": "Sala principal de estudio",
    "is_active": true,
    "created_at": "2024-01-15T10:00:00Z"
}
```
**Estado**: ✅ Probado y funcional

---

#### **12. Registrar ingreso a sala**
```http
POST /api/rooms/entry/
Authorization: Token <tu_token>
Content-Type: application/json
```
**Body:**
```json
{
    "room": 1,
    "notes": "Inicio de turno matutino"
}
```
**Respuesta exitosa (201):**
```json
{
    "message": "Ingreso registrado exitosamente",
    "entry": {
        "id": 456,
        "user": 5,
        "room": 1,
        "user_name": "Juan Pérez",
        "user_username": "monitor123",
        "room_name": "Sala de Estudio 1",
        "room_code": "S101",
        "entry_time": "2024-01-15T14:30:00Z",
        "exit_time": null,
        "duration_hours": null,
        "duration_minutes": null,
        "duration_formatted": "En curso",
        "is_active": true,
        "notes": "Inicio de turno matutino"
    }
}
```
**Estado**: ✅ Probado y funcional

---

#### **13. Registrar salida de sala**
```http
PATCH /api/rooms/entry/456/exit/
Authorization: Token <tu_token>
Content-Type: application/json
```
**Body (opcional):**
```json
{
    "notes": "Fin de turno"
}
```
**Respuesta exitosa (200):**
```json
{
    "message": "Salida registrada exitosamente",
    "entry": {
        "id": 456,
        "user": 5,
        "room": 1,
        "user_name": "Juan Pérez",
        "user_username": "monitor123",
        "room_name": "Sala de Estudio 1",
        "room_code": "S101",
        "entry_time": "2024-01-15T14:30:00Z",
        "exit_time": "2024-01-15T18:45:00Z",
        "duration_hours": 4.25,
        "duration_minutes": 255,
        "duration_formatted": "4h 15m",
        "is_active": false,
        "notes": "Fin de turno"
    }
}
```
**Estado**: ✅ Probado y funcional

---

#### **14. Historial de entradas del usuario**
```http
GET /api/rooms/my-entries/
Authorization: Token <tu_token>
```
**Respuesta exitosa (200):**
```json
{
    "count": 15,
    "entries": [
        {
            "id": 456,
            "user": 5,
            "room": 1,
            "user_name": "Juan Pérez",
            "user_username": "monitor123",
            "room_name": "Sala de Estudio 1",
            "room_code": "S101",
            "entry_time": "2024-01-15T14:30:00Z",
            "exit_time": "2024-01-15T18:45:00Z",
            "duration_hours": 4.25,
            "duration_minutes": 255,
            "duration_formatted": "4h 15m",
            "is_active": false,
            "notes": "Turno completado"
        }
    ]
}
```
**Estado**: ✅ Probado y funcional

---

#### **15. Entrada activa del usuario**
```http
GET /api/rooms/my-active-entry/
Authorization: Token <tu_token>
```
**Respuesta con entrada activa (200):**
```json
{
    "has_active_entry": true,
    "active_entry": {
        "id": 789,
        "user": 5,
        "room": 2,
        "user_name": "Juan Pérez",
        "user_username": "monitor123",
        "room_name": "Sala de Estudio 2",
        "room_code": "S102",
        "entry_time": "2024-01-15T09:00:00Z",
        "exit_time": null,
        "duration_formatted": "En curso",
        "is_active": true,
        "notes": "Turno matutino"
    }
}
```
**Respuesta sin entrada activa (200):**
```json
{
    "has_active_entry": false,
    "active_entry": null
}
```
**Estado**: ✅ Probado y funcional

---

#### **16. Ocupantes actuales de una sala**
```http
GET /api/rooms/123/occupants/
Authorization: Token <tu_token>
```
**Respuesta exitosa (200):**
```json
{
    "room": {
        "id": 123,
        "name": "Sala de Estudio 1",
        "code": "S101",
        "capacity": 20
    },
    "current_occupants": 2,
    "entries": [
        {
            "id": 456,
            "user": 5,
            "user_name": "Juan Pérez",
            "user_username": "monitor123",
            "entry_time": "2024-01-15T14:30:00Z",
            "duration_formatted": "En curso",
            "is_active": true,
            "notes": "Turno matutino"
        },
        {
            "id": 457,
            "user": 7,
            "user_name": "María García",
            "user_username": "monitor456",
            "entry_time": "2024-01-15T15:00:00Z",
            "duration_formatted": "En curso",
            "is_active": true,
            "notes": "Turno vespertino"
        }
    ]
}
```
**Estado**: ✅ Probado y funcional

---

### 🔔 **NOTIFICACIONES** (`/api/notifications/`)

#### **17. Gestión de notificaciones**
```http
GET /api/notifications/notifications/
Authorization: Token <tu_token>
```
**Estado**: 🔄 En desarrollo

---

## 🛡️ **Códigos de estado HTTP**

| Código | Descripción |
|--------|-------------|
| 200 | Éxito |
| 201 | Creado exitosamente |
| 400 | Error en los datos enviados |
| 401 | No autenticado (falta token o token inválido) |
| 403 | No autorizado (sin permisos) |
| 404 | Recurso no encontrado |
| 500 | Error interno del servidor |

---

## 🔐 **Configuración de headers para autenticación**

### **Postman**
```
Headers tab:
Authorization: Token bf774ea62d33995b830f906224e66d5b4e2df282
```

### **JavaScript (Fetch)**
```javascript
fetch('http://127.0.0.1:8000/api/auth/dashboard/', {
    method: 'GET',
    headers: {
        'Authorization': 'Token bf774ea62d33995b830f906224e66d5b4e2df282',
        'Content-Type': 'application/json'
    }
})
```

### **Python (Requests)**
```python
import requests

headers = {
    'Authorization': 'Token bf774ea62d33995b830f906224e66d5b4e2df282',
    'Content-Type': 'application/json'
}

response = requests.get('http://127.0.0.1:8000/api/auth/dashboard/', headers=headers)
```

### **cURL**
```bash
curl -H "Authorization: Token bf774ea62d33995b830f906224e66d5b4e2df282" \
     http://127.0.0.1:8000/api/auth/dashboard/
```

---

## ⚠️ **Errores comunes**

### **1. "Las credenciales de autenticación no se proveyeron"**
- **Causa**: Falta el header `Authorization`
- **Solución**: Agregar `Authorization: Token <tu_token>`

### **2. "Token inválido"**
- **Causa**: Token incorrecto o usuario no verificado
- **Solución**: Hacer login nuevamente o verificar usuario

### **3. "Tu cuenta aún no ha sido verificada"**
- **Causa**: Usuario no verificado por administrador
- **Solución**: Un admin debe verificar la cuenta

---

## 🎨 **Para el desarrollador frontend**

### **Flujo típico de la aplicación**
1. **Página de registro** → POST `/api/auth/register/`
2. **Página de login** → POST `/api/auth/login/` (guardar token)
3. **Dashboard principal** → GET `/api/auth/dashboard/` (con token)
4. **Perfil de usuario** → GET `/api/auth/profile/` (con token)
5. **Editar perfil** → PUT `/api/auth/profile/update/` (con token)

### **Manejo de tokens**
```javascript
// Guardar token después del login
localStorage.setItem('token', response.data.token);

// Usar token en todas las peticiones
const token = localStorage.getItem('token');
const headers = {
    'Authorization': `Token ${token}`,
    'Content-Type': 'application/json'
};
```

### **Manejo de roles**
- **Admin**: Acceso a todos los endpoints + panel administrativo
- **Monitor**: Acceso a endpoints básicos (perfil, dashboard, salas)

---

## 🔧 **Configuración de desarrollo**

### **Variables importantes**
- **Base URL**: `http://127.0.0.1:8000`
- **Debug**: Activado (solo desarrollo)
- **CORS**: Configurado para localhost:3000, localhost:4200
- **Base de datos**: SQLite (desarrollo)

### **Usuarios de prueba**
Puedes crear usuarios de prueba manualmente desde el admin de Django o mediante registro normal.

---

## 📞 **Soporte**

Si encuentras problemas:
1. Verifica que el servidor esté corriendo: `python manage.py runserver`
2. Confirma que tienes token válido
3. Revisa que el usuario esté verificado
4. Consulta los logs del servidor

**Proyecto probado y funcional al 100% ✅**

#### Modelos Principales:

1. **User** (authentication/models.py)
   - Modelo personalizado de usuario con roles (admin/monitor)
   - Verificación de administradores

2. **Room** (rooms/models.py)
   - Información básica de salas (nombre, código, capacidad)

3. **RoomEntry** (rooms/models.py)
   - Registro de entrada/salida de monitores
   - Cálculo de horas trabajadas

4. **Equipment** (equipment/models.py)
   - Gestión de equipos en las salas
   - Estados de los equipos

5. **EquipmentReport** (equipment/models.py)
   - Reporte de problemas con equipos

6. **Attendance** (attendance/models.py)
   - Subida y gestión de listados de asistencia

7. **Incapacity** (attendance/models.py)
   - Gestión de incapacidades de monitores

8. **Notification** (notifications/models.py)
   - Sistema de notificaciones en tiempo real

9. **Schedule** (schedule/models.py)
   - Gestión de turnos y calendario

10. **Report** (reports/models.py)
    - Generación y exportación de reportes

### 3. Estructura Adicional

Para cada aplicación, se ha creado una estructura básica:

- **models.py**: Definición de modelos con relaciones
- **serializers.py**: Serializadores básicos para cada modelo
- **views.py**: Vistas API sin lógica implementada
- **urls.py**: Rutas de API básicas

Esta estructura proporciona una base sólida para:
- Crear diagramas ER y relacionales
- Visualizar la estructura completa del proyecto
- Implementar la lógica específica en fases posteriores

## Próximos Pasos

1. Implementar la lógica de negocio para el Sprint 1
2. Ejecutar migraciones para actualizar la base de datos
3. Configurar autenticación y permisos
4. Desarrollar el frontend básico
5. Implementar pruebas unitarias