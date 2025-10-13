# 📅 Documentación de API - Sistema de Turnos y Calendarios

## 🎯 **Tarea 1 Completada**: Backend: Modelo y endpoints para Integración con calendarios

### 📋 Funcionalidades Implementadas

✅ **Modelo de datos robusto** para turnos (monitor, sala, fecha, hora inicio/fin)  
✅ **Endpoints CRUD completos** para crear, editar y eliminar turnos (solo admins)  
✅ **Endpoints de consulta** para que monitores vean sus turnos  
✅ **Asociación con registros de ingreso** para validación automática  
✅ **Validaciones de negocio** y restricciones de permisos  
✅ **Tests comprehensivos** (39 tests específicos + integración)

---

## 🔐 **Autenticación y Permisos**

### **Roles y Permisos:**
- **Administradores** (`IsAdminUser`): CRUD completo de turnos
- **Monitores verificados** (`IsVerifiedUser`): Solo lectura de sus propios turnos
- **Usuarios no verificados**: Sin acceso

### **Headers Requeridos:**
```http
Authorization: Token <user_token>
Content-Type: application/json
```

---

## 🛠️ **Endpoints Disponibles**

### **Base URL**: `/api/schedule/`

---

## 1. 📋 **CRUD de Turnos (Administradores)**

### **Listar Turnos** → `GET` - Ver todos los turnos
```http
GET /api/schedule/schedules/
```

**Permisos**: Solo administradores  
**Respuesta**:
```json
{
  "count": 25,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "start_datetime": "2025-10-07T08:00:00Z",
      "end_datetime": "2025-10-07T12:00:00Z",
      "status": "active",
      "recurring": false,
      "notes": "Turno matutino",
      "user_full_name": "Juan Pérez",
      "user_username": "monitor123",
      "room_name": "Laboratorio 1",
      "room_code": "LAB001",
      "duration_hours": 4.0,
      "is_current": false,
      "is_upcoming": true,
      "created_at": "2025-10-06T15:30:00Z",
      "updated_at": "2025-10-06T15:30:00Z"
    }
  ]
}
```

### **Crear Turno** → `POST` - Crear nuevo turno
```http
POST /api/schedule/schedules/
```

**Permisos**: Solo administradores  
**Body**:
```json
{
  "user": 5,
  "room": 2,
  "start_datetime": "2025-10-07T14:00:00Z",
  "end_datetime": "2025-10-07T18:00:00Z",
  "notes": "Turno vespertino",
  "recurring": false
}
```

**Validaciones**:
- Usuario debe ser monitor verificado
- Fecha fin posterior a fecha inicio
- Duración máxima: 12 horas
- No crear turnos en fechas pasadas

### **Ver Detalle** → `GET` - Detalle completo con estadísticas
```http
GET /api/schedule/schedules/{id}/
```

**Respuesta**:
```json
{
  "id": 1,
  "start_datetime": "2025-10-07T08:00:00Z",
  "end_datetime": "2025-10-07T12:00:00Z",
  "status": "active",
  "recurring": false,
  "notes": "Turno matutino",
  "user_details": {
    "id": 5,
    "username": "monitor123",
    "full_name": "Juan Pérez",
    "email": "juan@example.com",
    "phone": "+1234567890"
  },
  "room_details": {
    "id": 2,
    "name": "Laboratorio 1",
    "code": "LAB001",
    "capacity": 30,
    "description": "Laboratorio equipado"
  },
  "created_by_name": "Admin Principal",
  "duration_hours": 4.0,
  "is_current": false,
  "is_upcoming": true,
  "has_compliance": false,
  "room_entries": [],
  "created_at": "2025-10-06T15:30:00Z",
  "updated_at": "2025-10-06T15:30:00Z"
}
```

### **Actualizar Turno** → `PUT/PATCH` - Modificar turno
```http
PUT /api/schedule/schedules/{id}/
PATCH /api/schedule/schedules/{id}/
```

**Body** (PATCH ejemplo):
```json
{
  "notes": "Turno actualizado",
  "status": "completed"
}
```

### **Eliminar Turno** → `DELETE` - Eliminar turno
```http
DELETE /api/schedule/schedules/{id}/
```

**Respuesta**: `204 No Content`

---

## 2. 📊 **Acciones Especiales del ViewSet**

### **Turnos Próximos** → `GET` - Turnos en próximos 7 días
```http
GET /api/schedule/schedules/upcoming/
```

**Respuesta**:
```json
{
  "count": 5,
  "upcoming_schedules": [...]
}
```

### **Turnos Actuales** → `GET` - Turnos en curso
```http
GET /api/schedule/schedules/current/
```

**Respuesta**:
```json
{
  "count": 2,
  "current_schedules": [...]
}
```

---

## 3. 👤 **Endpoints para Monitores**

### **Mis Turnos** → `GET` - Turnos del monitor autenticado
```http
GET /api/schedule/my-schedules/
```

**Parámetros opcionales**:
- `date_from` (YYYY-MM-DD): Fecha desde
- `date_to` (YYYY-MM-DD): Fecha hasta  
- `status` (active|completed|cancelled|all): Filtrar por estado

**Respuesta**:
```json
{
  "monitor": {
    "username": "monitor123",
    "full_name": "Juan Pérez"
  },
  "summary": {
    "total_schedules": 15,
    "current_schedules": 1,
    "upcoming_schedules": 8,
    "past_schedules": 6
  },
  "current_schedules": [...],
  "upcoming_schedules": [...],
  "past_schedules": [...],
  "filters_applied": {
    "date_from": null,
    "date_to": null,
    "status": "active"
  }
}
```

### **Mi Turno Actual** → `GET` - Turno en curso del monitor
```http
GET /api/schedule/my-current-schedule/
```

**Respuesta con turno activo**:
```json
{
  "has_current_schedule": true,
  "current_schedule": {
    "id": 15,
    "start_datetime": "2025-10-06T14:00:00Z",
    "end_datetime": "2025-10-06T18:00:00Z",
    "status": "active",
    "room_name": "Laboratorio 2",
    "room_code": "LAB002",
    "duration_hours": 4.0,
    "is_current": true,
    "has_compliance": true
  }
}
```

**Respuesta sin turno activo**:
```json
{
  "has_current_schedule": false,
  "current_schedule": null
}
```

---

## 4. 🔧 **Endpoints para Administradores**

### **Resumen General** → `GET` - Dashboard administrativo
```http
GET /api/schedule/admin/overview/
```

**Permisos**: Solo administradores  
**Respuesta**:
```json
{
  "overview": {
    "total_schedules": 45,
    "active_schedules": 32,
    "current_schedules": 3,
    "schedules_by_status": {
      "active": 32,
      "completed": 10,
      "cancelled": 3
    },
    "non_compliant_count": 2
  },
  "upcoming_24h": [
    {
      "id": 20,
      "user_username": "monitor456",
      "room_name": "Laboratorio 3",
      "start_datetime": "2025-10-07T08:00:00Z",
      "duration_hours": 6.0
    }
  ],
  "non_compliant_schedules": [
    {
      "id": 18,
      "user_username": "monitor789",
      "room_name": "Laboratorio 1",
      "start_datetime": "2025-10-05T14:00:00Z",
      "end_datetime": "2025-10-05T18:00:00Z"
    }
  ],
  "generated_at": "2025-10-06T20:30:00Z"
}
```

---

## 📊 **Estados de Turnos**

| Estado | Descripción |
|--------|-------------|
| `active` | Turno activo y programado |
| `completed` | Turno completado |
| `cancelled` | Turno cancelado |

---

## 🧪 **Propiedades del Modelo Schedule**

### **Propiedades de Estado**:
- `duration_hours`: Duración en horas (decimal)
- `is_active`: Si el estado es 'active'
- `is_current`: Si está en horario actual
- `is_upcoming`: Si está en próximas 24 horas

### **Propiedades de Validación**:
- `has_compliance()`: Si el monitor cumplió (tiene entradas en sala)
- `get_room_entries()`: Entradas de sala durante el turno

---

## ⚠️ **Validaciones del Sistema**

### **Modelo Schedule**:
- ✅ Fecha fin posterior a fecha inicio
- ✅ Duración máxima: 12 horas
- ✅ Solo monitores verificados pueden tener turnos
- ✅ Constraint DB: `end_datetime > start_datetime`

### **API Endpoints**:
- ✅ No crear turnos en fechas pasadas
- ✅ Solo admins pueden hacer CRUD
- ✅ Monitores solo ven sus propios turnos
- ✅ Validación de formato de fechas en filtros

---

## 🔗 **Integración con Registros de Sala**

El modelo Schedule se integra automáticamente con `RoomEntry` para:

1. **Verificar cumplimiento**: `has_compliance()` verifica si hay entradas durante el turno
2. **Obtener registros**: `get_room_entries()` devuelve entradas de sala del turno
3. **Validación futura**: Base para Task 2 (validar entrada solo con turno activo)

---

## 🧪 **Tests Implementados**

### **Cobertura de Tests** (39 tests):
- ✅ **Modelo**: Validaciones, propiedades, métodos (18 tests)
- ✅ **CRUD Admin**: Crear, leer, actualizar, eliminar (18 tests)  
- ✅ **Endpoints Monitor**: Consultas propias, filtros (12 tests)
- ✅ **Endpoints Admin**: Overview, estadísticas (9 tests)
- ✅ **Permisos**: Acceso, roles, autenticación (validado en todos)

### **Ejecutar Tests**:
```bash
# Tests específicos de Schedule
python manage.py test schedule.tests

# Tests completos del proyecto
python manage.py test
```

---

## 🎯 **Task 1 - Criterios de Aceptación Cumplidos**

✅ **Modelo robusto**: Schedule con validaciones y estados  
✅ **CRUD completo**: Crear, editar, eliminar (solo admins)  
✅ **Consulta de turnos**: Monitores ven sus turnos en dashboard  
✅ **Asociación con registros**: Método `has_compliance()` y `get_room_entries()`  
✅ **Permisos apropiados**: IsAdminUser para CRUD, IsVerifiedUser para lectura  
✅ **Tests comprehensivos**: 39 tests + integración con 145 tests totales

---

## 🚀 **URLs Completas de la API**

| Método | URL | Descripción | Permisos |
|--------|-----|-------------|----------|
| `GET` | `/api/schedule/schedules/` | Listar turnos | Admin |
| `POST` | `/api/schedule/schedules/` | Crear turno | Admin |
| `GET` | `/api/schedule/schedules/{id}/` | Detalle turno | Admin/Monitor |
| `PUT/PATCH` | `/api/schedule/schedules/{id}/` | Actualizar turno | Admin |
| `DELETE` | `/api/schedule/schedules/{id}/` | Eliminar turno | Admin |
| `GET` | `/api/schedule/schedules/upcoming/` | Turnos próximos | Verificado |
| `GET` | `/api/schedule/schedules/current/` | Turnos actuales | Verificado |
| `GET` | `/api/schedule/my-schedules/` | Mis turnos | Monitor |
| `GET` | `/api/schedule/my-current-schedule/` | Mi turno actual | Monitor |
| `GET` | `/api/schedule/admin/overview/` | Resumen admin | Admin |

---

## ✨ **Próximos Pasos (Task 2)**

La implementación actual provee la base perfecta para Task 2:

1. **Validación de conflictos** - Detectar turnos superpuestos
2. **Comparación con registros** - Usar `has_compliance()` existente  
3. **Notificaciones automáticas** - Para turnos no cumplidos
4. **Restricción de entrada** - Solo permitir entrada con turno activo

El sistema está listo para estas validaciones avanzadas! 🎉