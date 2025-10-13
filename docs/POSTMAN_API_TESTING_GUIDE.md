# 🚀 **API REST - Sistema de Gestión de Salas y Turnos**

## 📖 **Descripción del Proyecto**

Sistema completo de gestión de salas y turnos para monitores con validaciones avanzadas, notificaciones automáticas y control de acceso basado en horarios programados.

### ✨ **Características Principales**
- ✅ **Gestión completa de turnos** (CRUD para administradores)
- ✅ **Control de acceso a salas** basado en turnos asignados  
- ✅ **Validaciones automáticas** de conflictos y múltiples monitores
- ✅ **Notificaciones automáticas** por incumplimiento de turnos
- ✅ **Cierre automático de sesiones** cuando terminan los turnos
- ✅ **Respuestas detalladas** del servidor con información contextual
- ✅ **Sistema de autenticación** con tokens
- ✅ **161 tests** con cobertura completa

---

## 🔧 **Configuración del Entorno**

### **Prerrequisitos**
- Python 3.8+
- Django 4.2+
- PostgreSQL/SQLite

### **Instalación**
```bash
# Clonar repositorio
git clone <repo-url>
cd ds2-2-back

# Crear entorno virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac
# o
venv\\Scripts\\activate   # Windows

# Instalar dependencias
pip install -r requirements.txt

# Configurar base de datos
python manage.py migrate

# Crear superusuario
python manage.py createsuperuser

# Ejecutar servidor
python manage.py runserver
```

### **Variables de Entorno**
```env
SECRET_KEY=your-secret-key
DEBUG=True
DATABASE_URL=sqlite:///db.sqlite3
FRONTEND_BASE_URL=http://localhost:3000
```

---

## 🔐 **Autenticación**

Todas las APIs requieren autenticación por token:

```http
Authorization: Token <user_token>
Content-Type: application/json
```

### **Obtener Token de Autenticación**
```http
POST /api/auth/login/
Content-Type: application/json

{
  "username": "monitor1",
  "password": "password123"
}
```

**Respuesta:**
```json
{
  "token": "ec6acd1be5218377c8c4869f2702540aae452baa",
  "user": {
    "id": 3,
    "username": "monitor1",
    "role": "monitor",
    "is_verified": true
  }
}
```

---

## 📋 **CASOS DE PRUEBA EN POSTMAN**

### **🗂️ Colección: DS2 Backend API**

---

## 1️⃣ **MÓDULO: AUTHENTICATION**

### **📁 Carpeta: Auth**

#### **🟢 1.1 Login Exitoso**
```http
POST {{base_url}}/api/auth/login/
Content-Type: application/json

{
  "username": "monitor1",
  "password": "password123"
}
```
**Expected Status:** `200 OK`  
**Variables to Set:** `auth_token` = `{{response.token}}`

#### **🔴 1.2 Login - Credenciales Inválidas**
```http
POST {{base_url}}/api/auth/login/
Content-Type: application/json

{
  "username": "invalid_user",
  "password": "wrong_password"
}
```
**Expected Status:** `400 Bad Request`

#### **🟢 1.3 Perfil de Usuario**
```http
GET {{base_url}}/api/auth/profile/
Authorization: Token {{auth_token}}
```
**Expected Status:** `200 OK`

---

## 2️⃣ **MÓDULO: SCHEDULE (TURNOS)**

### **📁 Carpeta: Schedule - Admin**

#### **🟢 2.1 Listar Todos los Turnos (Admin)**
```http
GET {{base_url}}/api/schedule/schedules/
Authorization: Token {{admin_token}}
```
**Expected Status:** `200 OK`

#### **🟢 2.2 Crear Turno (Admin)**
```http
POST {{base_url}}/api/schedule/schedules/
Authorization: Token {{admin_token}}
Content-Type: application/json

{
  "user": 3,
  "room": 1,
  "start_datetime": "2025-10-08T14:00:00Z",
  "end_datetime": "2025-10-08T18:00:00Z",
  "notes": "Turno vespertino",
  "recurring": false
}
```
**Expected Status:** `201 Created`  
**Variables to Set:** `schedule_id` = `{{response.id}}`

#### **🟢 2.3 Ver Detalle de Turno**
```http
GET {{base_url}}/api/schedule/schedules/{{schedule_id}}/
Authorization: Token {{admin_token}}
```
**Expected Status:** `200 OK`

#### **🟢 2.4 Actualizar Turno (Admin)**
```http
PATCH {{base_url}}/api/schedule/schedules/{{schedule_id}}/
Authorization: Token {{admin_token}}
Content-Type: application/json

{
  "notes": "Turno actualizado",
  "status": "active"
}
```
**Expected Status:** `200 OK`

#### **🟢 2.5 Eliminar Turno (Admin)**
```http
DELETE {{base_url}}/api/schedule/schedules/{{schedule_id}}/
Authorization: Token {{admin_token}}
```
**Expected Status:** `204 No Content`

#### **🔴 2.6 Crear Turno - Conflicto de Horarios**
```http
POST {{base_url}}/api/schedule/schedules/
Authorization: Token {{admin_token}}
Content-Type: application/json

{
  "user": 3,
  "room": 1,
  "start_datetime": "2025-10-08T15:00:00Z",
  "end_datetime": "2025-10-08T19:00:00Z",
  "notes": "Turno que debería generar conflicto"
}
```
**Expected Status:** `400 Bad Request`  
**Expected Response:** Mensaje de conflicto de horarios

### **📁 Carpeta: Schedule - Monitor**

#### **🟢 2.7 Mis Turnos (Monitor)**
```http
GET {{base_url}}/api/schedule/my-schedules/
Authorization: Token {{monitor_token}}
```
**Expected Status:** `200 OK`

#### **🟢 2.8 Mis Turnos con Filtros**
```http
GET {{base_url}}/api/schedule/my-schedules/?date_from=2025-10-08&status=active
Authorization: Token {{monitor_token}}
```
**Expected Status:** `200 OK`

#### **🟢 2.9 Mi Turno Actual**
```http
GET {{base_url}}/api/schedule/my-current-schedule/
Authorization: Token {{monitor_token}}
```
**Expected Status:** `200 OK`

#### **🔴 2.10 Monitor No Puede Crear Turnos**
```http
POST {{base_url}}/api/schedule/schedules/
Authorization: Token {{monitor_token}}
Content-Type: application/json

{
  "user": 3,
  "room": 1,
  "start_datetime": "2025-10-08T14:00:00Z",
  "end_datetime": "2025-10-08T18:00:00Z"
}
```
**Expected Status:** `403 Forbidden`

### **📁 Carpeta: Schedule - ViewSet Actions**

#### **🟢 2.11 Turnos Próximos**
```http
GET {{base_url}}/api/schedule/schedules/upcoming/
Authorization: Token {{auth_token}}
```
**Expected Status:** `200 OK`

#### **🟢 2.12 Turnos Actuales**
```http
GET {{base_url}}/api/schedule/schedules/current/
Authorization: Token {{auth_token}}
```
**Expected Status:** `200 OK`

#### **🟢 2.13 Resumen Administrativo**
```http
GET {{base_url}}/api/schedule/admin/overview/
Authorization: Token {{admin_token}}
```
**Expected Status:** `200 OK`

---

## 3️⃣ **MÓDULO: ROOMS (SALAS)**

### **📁 Carpeta: Rooms - Basic Operations**

#### **🟢 3.1 Listar Salas**
```http
GET {{base_url}}/api/rooms/
Authorization: Token {{auth_token}}
```
**Expected Status:** `200 OK`

#### **🟢 3.2 Detalle de Sala**
```http
GET {{base_url}}/api/rooms/1/
Authorization: Token {{auth_token}}
```
**Expected Status:** `200 OK`

#### **🟢 3.3 Ocupantes Actuales de una Sala**
```http
GET {{base_url}}/api/rooms/1/occupants/
Authorization: Token {{auth_token}}
```
**Expected Status:** `200 OK`

### **📁 Carpeta: Rooms - Entry/Exit**

#### **🟢 3.4 Crear Entrada a Sala (Con Turno Válido)**
```http
POST {{base_url}}/api/rooms/entry/
Authorization: Token {{monitor_token}}
Content-Type: application/json

{
  "room": 1,
  "notes": "Inicio de turno matutino"
}
```
**Expected Status:** `201 Created`  
**Variables to Set:** `entry_id` = `{{response.entry.id}}`

**Expected Response:**
```json
{
  "success": true,
  "message": "Acceso concedido a Sala de Literatura (NS001)",
  "entry": {
    "id": 18,
    "room": 1,
    "user": 3,
    "entry_time": "2025-10-08T14:30:00Z",
    "exit_time": null,
    "is_active": true,
    "notes": "Inicio de turno matutino. Turno ID: 21"
  },
  "schedule": {
    "id": 21,
    "start_time": "14:00",
    "end_time": "18:00",
    "remaining_minutes": 210
  },
  "details": {
    "turno_valido_hasta": "18:00",
    "cierre_automatico": "La sesión se cerrará automáticamente a las 18:00"
  }
}
```

#### **🔴 3.5 Crear Entrada - Sin Turno Asignado**
```http
POST {{base_url}}/api/rooms/entry/
Authorization: Token {{monitor_token}}
Content-Type: application/json

{
  "room": 2,
  "notes": "Intento sin turno"
}
```
**Expected Status:** `400 Bad Request`

**Expected Response:**
```json
{
  "error": "Sin turno asignado para esta sala",
  "details": {
    "reason": "schedule_required",
    "current_time": "2025-10-08 14:30:00",
    "room": "NS002",
    "user": "monitor1"
  }
}
```

#### **🔴 3.6 Crear Entrada - Sala Ocupada**
```http
POST {{base_url}}/api/rooms/entry/
Authorization: Token {{monitor2_token}}
Content-Type: application/json

{
  "room": 1,
  "notes": "Intento con sala ocupada"
}
```
**Expected Status:** `400 Bad Request`

**Expected Response:**
```json
{
  "error": "Sala ocupada por otro monitor",
  "details": {
    "reason": "room_occupied",
    "requesting_user": "monitor2"
  },
  "current_occupant": {
    "username": "monitor1",
    "entry_time": "14:30:00",
    "duration_minutes": 15
  }
}
```

#### **🟢 3.7 Registrar Salida**
```http
PATCH {{base_url}}/api/rooms/entry/{{entry_id}}/exit/
Authorization: Token {{monitor_token}}
Content-Type: application/json

{
  "notes": "Fin de turno"
}
```
**Expected Status:** `200 OK`

**Expected Response:**
```json
{
  "message": "Salida registrada exitosamente",
  "entry": {
    "id": 18,
    "exit_time": "2025-10-08T17:45:00Z",
    "total_duration": "3 horas 15 minutos",
    "is_active": false
  },
  "duration_info": {
    "total_minutes": 195,
    "formatted_duration": "3 horas 15 minutos",
    "is_excessive": false
  }
}
```

### **📁 Carpeta: Rooms - User History**

#### **🟢 3.8 Mi Historial de Entradas**
```http
GET {{base_url}}/api/rooms/my-entries/
Authorization: Token {{monitor_token}}
```
**Expected Status:** `200 OK`

#### **🟢 3.9 Mi Entrada Activa**
```http
GET {{base_url}}/api/rooms/my-active-entry/
Authorization: Token {{monitor_token}}
```
**Expected Status:** `200 OK`

#### **🟢 3.10 Salir de Mi Entrada Activa**
```http
PATCH {{base_url}}/api/rooms/my-active-entry/exit/
Authorization: Token {{monitor_token}}
Content-Type: application/json

{
  "notes": "Salida rápida"
}
```
**Expected Status:** `200 OK`

#### **🟢 3.11 Resumen Diario**
```http
GET {{base_url}}/api/rooms/my-daily-summary/
Authorization: Token {{monitor_token}}
```
**Expected Status:** `200 OK`

### **📁 Carpeta: Rooms - Admin**

#### **🟢 3.12 Admin - Listar Todas las Salas**
```http
GET {{base_url}}/api/rooms/admin/rooms/
Authorization: Token {{admin_token}}
```
**Expected Status:** `200 OK`

#### **🟢 3.13 Admin - Crear Nueva Sala**
```http
POST {{base_url}}/api/rooms/admin/rooms/create/
Authorization: Token {{admin_token}}
Content-Type: application/json

{
  "name": "Sala de Prueba",
  "code": "TEST001",
  "capacity": 25,
  "description": "Sala creada para pruebas"
}
```
**Expected Status:** `201 Created`  
**Variables to Set:** `new_room_id` = `{{response.id}}`

#### **🟢 3.14 Admin - Ver Detalle de Sala**
```http
GET {{base_url}}/api/rooms/admin/rooms/{{new_room_id}}/
Authorization: Token {{admin_token}}
```
**Expected Status:** `200 OK`

#### **🟢 3.15 Admin - Actualizar Sala**
```http
PUT {{base_url}}/api/rooms/admin/rooms/{{new_room_id}}/update/
Authorization: Token {{admin_token}}
Content-Type: application/json

{
  "name": "Sala de Prueba Actualizada",
  "code": "TEST001",
  "capacity": 30,
  "description": "Sala actualizada",
  "is_active": true
}
```
**Expected Status:** `200 OK`

#### **🟢 3.16 Admin - Listar Todas las Entradas**
```http
GET {{base_url}}/api/rooms/entries/
Authorization: Token {{admin_token}}
```
**Expected Status:** `200 OK`

#### **🟢 3.17 Admin - Estadísticas de Entradas**
```http
GET {{base_url}}/api/rooms/entries/stats/
Authorization: Token {{admin_token}}
```
**Expected Status:** `200 OK`

---

## 4️⃣ **MÓDULO: SYSTEM MAINTENANCE**

### **📁 Carpeta: System - Automated Operations**

#### **🟢 4.1 Cerrar Sesiones Expiradas**
```http
POST {{base_url}}/api/rooms/close-expired-sessions/
Authorization: Token {{admin_token}}
```
**Expected Status:** `200 OK`

**Expected Response:**
```json
{
  "success": true,
  "message": "Se revisaron y cerraron 2 sesiones vencidas",
  "closed_sessions_count": 2,
  "closed_sessions": [
    {
      "user": "monitor1",
      "room": "NS001",
      "entry_id": 15,
      "schedule_end": "2025-10-08T16:00:00Z",
      "auto_closed_at": "2025-10-08T18:30:00Z"
    }
  ],
  "timestamp": "2025-10-08 18:30:00"
}
```

---

## 5️⃣ **MÓDULO: NOTIFICATIONS**

### **📁 Carpeta: Notifications**

#### **🟢 5.1 Listar Mis Notificaciones**
```http
GET {{base_url}}/api/notifications/notifications/
Authorization: Token {{admin_token}}
```
**Expected Status:** `200 OK`

#### **🟢 5.2 Marcar Notificación como Leída**
```http
PATCH {{base_url}}/api/notifications/notifications/{{notification_id}}/
Authorization: Token {{admin_token}}
Content-Type: application/json

{
  "read": true
}
```
**Expected Status:** `200 OK`

---

## 🧪 **ESCENARIOS DE PRUEBA COMPLETOS**

### **📋 Escenario 1: Flujo Completo de Monitor**

1. **Login como Monitor** → Obtener token
2. **Ver Mis Turnos** → Verificar turnos asignados
3. **Ver Mi Turno Actual** → Verificar si hay turno activo
4. **Crear Entrada a Sala** → Con turno válido
5. **Ver Mi Entrada Activa** → Verificar entrada creada
6. **Ver Resumen Diario** → Verificar estadísticas
7. **Registrar Salida** → Completar sesión

### **📋 Escenario 2: Validaciones de Seguridad**

1. **Intento de Entrada Sin Turno** → Debe fallar
2. **Intento de Entrada en Sala Ocupada** → Debe fallar
3. **Intento de Crear Turno como Monitor** → Debe fallar
4. **Acceso a APIs de Admin como Monitor** → Debe fallar

### **📋 Escenario 3: Gestión Administrativa**

1. **Login como Admin** → Obtener token admin
2. **Ver Resumen General** → Dashboard completo
3. **Crear Nuevo Turno** → Para un monitor
4. **Verificar Conflictos** → Intentar crear turno superpuesto
5. **Ver Todas las Entradas** → Monitoreo completo
6. **Cerrar Sesiones Expiradas** → Mantenimiento

### **📋 Escenario 4: Notificaciones Automáticas**

1. **Crear Turno que Inicie en el Pasado** → Para simular incumplimiento
2. **Ejecutar Comando de Verificación** → `python manage.py check_schedule_compliance`
3. **Verificar Notificaciones Generadas** → Para administradores
4. **Marcar Notificaciones como Leídas** → Gestión de notificaciones

---

## 🔧 **VARIABLES DE ENTORNO PARA POSTMAN**

### **Variables Globales:**
```json
{
  "base_url": "http://127.0.0.1:8000",
  "auth_token": "",
  "admin_token": "",
  "monitor_token": "",
  "monitor2_token": "",
  "schedule_id": "",
  "entry_id": "",
  "room_id": "",
  "notification_id": ""
}
```

### **Variables por Entorno:**

#### **🟢 Development**
```json
{
  "base_url": "http://127.0.0.1:8000"
}
```

#### **🟡 Staging**
```json
{
  "base_url": "https://staging-api.example.com"
}
```

#### **🔴 Production**
```json
{
  "base_url": "https://api.example.com"
}
```

---

## ⚠️ **CÓDIGOS DE RESPUESTA**

### **Exitosas (2xx)**
- `200 OK` - Solicitud exitosa
- `201 Created` - Recurso creado exitosamente
- `204 No Content` - Eliminación exitosa

### **Errores del Cliente (4xx)**
- `400 Bad Request` - Datos inválidos o validación fallida
- `401 Unauthorized` - Token de autenticación faltante o inválido
- `403 Forbidden` - Sin permisos para la operación
- `404 Not Found` - Recurso no encontrado
- `405 Method Not Allowed` - Método HTTP no permitido

### **Errores del Servidor (5xx)**
- `500 Internal Server Error` - Error interno del servidor

---

## 📊 **ESTRUCTURA DE RESPUESTAS**

### **Respuesta Exitosa Estándar:**
```json
{
  "success": true,
  "message": "Operación completada exitosamente",
  "data": { /* datos específicos */ },
  "timestamp": "2025-10-08T14:30:00Z"
}
```

### **Respuesta de Error Estándar:**
```json
{
  "success": false,
  "error": "Descripción del error",
  "details": {
    "reason": "codigo_de_error",
    "field": "campo_con_error",
    "additional_info": "información adicional"
  },
  "timestamp": "2025-10-08T14:30:00Z"
}
```

### **Respuesta de Validación:**
```json
{
  "success": false,
  "error": "Errores de validación",
  "validation_errors": {
    "field1": ["Error en campo 1"],
    "field2": ["Error en campo 2"]
  }
}
```

---

## 🔄 **COMANDOS DE MANTENIMIENTO**

### **Verificar Cumplimiento de Turnos:**
```bash
python manage.py check_schedule_compliance --verbose
```

### **Cerrar Sesiones Expiradas:**
```bash
python manage.py close_expired_sessions --verbose
```

### **Ejecutar Tests:**
```bash
# Todos los tests
python manage.py test

# Tests específicos
python manage.py test schedule.tests
python manage.py test rooms.tests
```

---

## 📚 **DOCUMENTACIÓN ADICIONAL**

- **API de Turnos:** `SCHEDULE_API_DOCUMENTATION.md`
- **Solución de Sesiones:** `SOLUCION_SESIONES_AUTOMATICAS.md`
- **Implementación Completa:** `SOLUCION_COMPLETA_IMPLEMENTADA.md`

---

## 🎯 **Notas Importantes**

1. **Autenticación Requerida:** Todas las APIs requieren token válido
2. **Validación de Turnos:** Solo se permite entrada con turno activo
3. **Un Monitor por Sala:** Sistema previene múltiples monitores simultáneos
4. **Cierre Automático:** Las sesiones se cierran cuando expira el turno
5. **Notificaciones:** Se generan automáticamente por incumplimientos
6. **Respuestas Detalladas:** El servidor proporciona información contextual completa

---

**🚀 Sistema listo para producción con 161 tests exitosos y funcionalidad completa implementada.**