# 📚 API de Cursos - Documentación para Postman

## 🔧 Configuración Inicial

### Headers Requeridos
```
Content-Type: application/json
Authorization: Token YOUR_TOKEN_HERE
```

### Base URL
```
http://localhost:8000/api
```

---

## 📋 Endpoints Disponibles

### 1. 📝 **Crear Curso** (Solo Administradores)
**POST** `/courses/`

#### Request Body:
```json
{
    "name": "Programación Avanzada",
    "description": "Curso de programación con Python y Django",
    "room": 1,
    "schedule": 2,
    "start_datetime": "2025-10-15T08:00:00Z",
    "end_datetime": "2025-10-15T10:00:00Z",
    "status": "scheduled",
    "notes": "Llevar laptops y material de apoyo"
}
```

#### Response (201 Created):
```json
{
    "id": 5,
    "name": "Programación Avanzada",
    "description": "Curso de programación con Python y Django",
    "room": {
        "id": 1,
        "name": "Sala A",
        "code": "SALA_A",
        "capacity": 30
    },
    "schedule": {
        "id": 2,
        "user": {
            "id": 3,
            "username": "monitor_carlos",
            "full_name": "Carlos Rodriguez"
        },
        "start_datetime": "2025-10-15T08:00:00Z",
        "end_datetime": "2025-10-15T12:00:00Z"
    },
    "monitor": {
        "id": 3,
        "username": "monitor_carlos",
        "full_name": "Carlos Rodriguez"
    },
    "start_datetime": "2025-10-15T08:00:00Z",
    "end_datetime": "2025-10-15T10:00:00Z",
    "status": "scheduled",
    "notes": "Llevar laptops y material de apoyo",
    "created_by": {
        "id": 1,
        "username": "admin",
        "full_name": "Administrador Sistema"
    },
    "created_at": "2025-10-10T14:30:00Z",
    "updated_at": "2025-10-10T14:30:00Z"
}
```

#### Errores Comunes:
```json
// Error 400 - Datos inválidos
{
    "name": ["Este campo es requerido."],
    "start_datetime": ["La fecha de inicio debe ser futura."]
}

// Error 403 - Sin permisos
{
    "error": "Solo administradores pueden crear cursos"
}

// Error 409 - Conflicto de horario
{
    "error": "Conflicto de horario detectado",
    "details": "La sala ya está ocupada en este horario"
}
```

---

### 2. 📖 **Listar Cursos**
**GET** `/courses/`

#### Query Parameters (opcionales):
```
?room=1&status=scheduled&ordering=-start_datetime&search=programacion
```

#### Response (200 OK):
```json
{
    "count": 25,
    "next": "http://localhost:8000/api/courses/?page=2",
    "previous": null,
    "results": [
        {
            "id": 5,
            "name": "Programación Avanzada",
            "room_name": "Sala A",
            "room_code": "SALA_A",
            "monitor_name": "Carlos Rodriguez", 
            "start_datetime": "2025-10-15T08:00:00Z",
            "end_datetime": "2025-10-15T10:00:00Z",
            "status": "scheduled",
            "created_at": "2025-10-10T14:30:00Z"
        },
        {
            "id": 4,
            "name": "Bases de Datos",
            "room_name": "Sala B",
            "room_code": "SALA_B", 
            "monitor_name": "Ana Martinez",
            "start_datetime": "2025-10-14T14:00:00Z",
            "end_datetime": "2025-10-14T16:00:00Z",
            "status": "in_progress",
            "created_at": "2025-10-09T10:15:00Z"
        }
    ]
}
```

---

### 3. 🔍 **Detalle de Curso**
**GET** `/courses/{id}/`

#### Response (200 OK):
```json
{
    "id": 5,
    "name": "Programación Avanzada",
    "description": "Curso de programación con Python y Django",
    "room": {
        "id": 1,
        "name": "Sala A",
        "code": "SALA_A",
        "capacity": 30,
        "is_active": true
    },
    "schedule": {
        "id": 2,
        "user": {
            "id": 3,
            "username": "monitor_carlos",
            "full_name": "Carlos Rodriguez",
            "email": "carlos@example.com"
        },
        "room": {
            "id": 1,
            "name": "Sala A"
        },
        "start_datetime": "2025-10-15T08:00:00Z",
        "end_datetime": "2025-10-15T12:00:00Z",
        "status": "active",
        "duration_hours": 4.0
    },
    "monitor": {
        "id": 3,
        "username": "monitor_carlos",
        "full_name": "Carlos Rodriguez",
        "email": "carlos@example.com"
    },
    "start_datetime": "2025-10-15T08:00:00Z",
    "end_datetime": "2025-10-15T10:00:00Z",
    "duration_hours": 2.0,
    "status": "scheduled",
    "notes": "Llevar laptops y material de apoyo",
    "is_current": false,
    "is_upcoming": true,
    "created_by": {
        "id": 1,
        "username": "admin",
        "full_name": "Administrador Sistema"
    },
    "created_at": "2025-10-10T14:30:00Z",
    "updated_at": "2025-10-10T14:30:00Z"
}
```

---

### 4. ✏️ **Actualizar Curso** (Solo Administradores)
**PUT** `/courses/{id}/` o **PATCH** `/courses/{id}/`

#### Request Body (PUT - todos los campos):
```json
{
    "name": "Programación Avanzada - Actualizado",
    "description": "Curso actualizado de programación con Python y Django",
    "room": 1,
    "schedule": 2,
    "start_datetime": "2025-10-15T09:00:00Z",
    "end_datetime": "2025-10-15T11:00:00Z",
    "status": "scheduled",
    "notes": "Material actualizado - incluir notebooks"
}
```

#### Request Body (PATCH - campos parciales):
```json
{
    "name": "Programación Avanzada - Modificado",
    "notes": "Nuevas instrucciones para el curso"
}
```

#### Response (200 OK):
```json
{
    "id": 5,
    "name": "Programación Avanzada - Modificado",
    "description": "Curso actualizado de programación con Python y Django",
    "room": {
        "id": 1,
        "name": "Sala A",
        "code": "SALA_A",
        "capacity": 30
    },
    "notes": "Nuevas instrucciones para el curso",
    "updated_at": "2025-10-10T15:45:00Z"
}
```

---

### 5. 🗑️ **Eliminar Curso** (Solo Administradores)
**DELETE** `/courses/{id}/`

#### Response (204 No Content):
```
(Sin contenido de respuesta)
```

#### Error (404 Not Found):
```json
{
    "detail": "No encontrado."
}
```

---

### 6. 👨‍🏫 **Mis Cursos** (Solo Monitores)
**GET** `/courses/my_courses/`

#### Response (200 OK):
```json
{
    "courses": [
        {
            "id": 5,
            "name": "Programación Avanzada",
            "room_name": "Sala A",
            "start_datetime": "2025-10-15T08:00:00Z",
            "end_datetime": "2025-10-15T10:00:00Z",
            "status": "scheduled",
            "duration_hours": 2.0,
            "is_upcoming": true
        },
        {
            "id": 7,
            "name": "Algoritmos y Estructuras",
            "room_name": "Sala B",
            "start_datetime": "2025-10-16T14:00:00Z",
            "end_datetime": "2025-10-16T17:00:00Z",
            "status": "scheduled",
            "duration_hours": 3.0,
            "is_upcoming": true
        }
    ],
    "total_count": 2
}
```

---

### 7. 📅 **Cursos Próximos**
**GET** `/courses/upcoming/`

#### Response (200 OK):
```json
{
    "courses": [
        {
            "id": 5,
            "name": "Programación Avanzada",
            "room_name": "Sala A",
            "monitor_name": "Carlos Rodriguez",
            "start_datetime": "2025-10-15T08:00:00Z",
            "end_datetime": "2025-10-15T10:00:00Z",
            "days_until_start": 5
        }
    ],
    "total_count": 1,
    "date_range": "Próximos 7 días"
}
```

---

### 8. ⏰ **Cursos Actuales**
**GET** `/courses/current/`

#### Response (200 OK):
```json
{
    "courses": [
        {
            "id": 4,
            "name": "Bases de Datos",
            "room_name": "Sala B",
            "monitor_name": "Ana Martinez",
            "start_datetime": "2025-10-10T14:00:00Z",
            "end_datetime": "2025-10-10T16:00:00Z",
            "status": "in_progress",
            "time_remaining_minutes": 45
        }
    ],
    "total_count": 1,
    "timestamp": "2025-10-10T15:15:00Z"
}
```

---

### 9. 📋 **Historial de Curso**
**GET** `/courses/{id}/history/`

#### Response (200 OK):
```json
{
    "course_id": 5,
    "course_name": "Programación Avanzada",
    "history": [
        {
            "id": 12,
            "action": "updated",
            "field_changes": {
                "name": {
                    "old_value": "Programación Avanzada",
                    "new_value": "Programación Avanzada - Modificado"
                },
                "notes": {
                    "old_value": "Llevar laptops y material de apoyo",
                    "new_value": "Nuevas instrucciones para el curso"
                }
            },
            "changed_by": {
                "id": 1,
                "username": "admin",
                "full_name": "Administrador Sistema"
            },
            "timestamp": "2025-10-10T15:45:00Z"
        },
        {
            "id": 11,
            "action": "created",
            "field_changes": {},
            "changed_by": {
                "id": 1,
                "username": "admin",
                "full_name": "Administrador Sistema"
            },
            "timestamp": "2025-10-10T14:30:00Z"
        }
    ],
    "total_changes": 2
}
```

---

### 10. 📊 **Vista de Calendario**
**GET** `/courses/calendar_view/`

#### Query Parameters:
```
?start_date=2025-10-15&end_date=2025-10-22
```

#### Response (200 OK):
```json
{
    "calendar_events": [
        {
            "id": "schedule_2",
            "type": "schedule",
            "title": "Turno - Carlos Rodriguez",
            "start": "2025-10-15T08:00:00Z",
            "end": "2025-10-15T12:00:00Z",
            "room": "Sala A",
            "monitor": "Carlos Rodriguez",
            "status": "active"
        },
        {
            "id": "course_5", 
            "type": "course",
            "title": "Programación Avanzada",
            "start": "2025-10-15T08:00:00Z",
            "end": "2025-10-15T10:00:00Z",
            "room": "Sala A",
            "monitor": "Carlos Rodriguez",
            "status": "scheduled"
        }
    ],
    "summary": {
        "total_schedules": 3,
        "total_courses": 2,
        "date_range": {
            "start": "2025-10-15",
            "end": "2025-10-22"
        }
    }
}
```

---

### 11. 📈 **Resumen de Cursos para Administradores**
**GET** `/admin/courses/overview/`

#### Response (200 OK):
```json
{
    "summary": {
        "total_courses": 15,
        "scheduled_courses": 8,
        "in_progress_courses": 2,
        "completed_courses": 4,
        "cancelled_courses": 1
    },
    "recent_activity": [
        {
            "course_name": "Programación Avanzada",
            "action": "created",
            "timestamp": "2025-10-10T14:30:00Z",
            "user": "admin"
        }
    ],
    "upcoming_courses": [
        {
            "id": 5,
            "name": "Programación Avanzada", 
            "start_datetime": "2025-10-15T08:00:00Z",
            "room_name": "Sala A"
        }
    ]
}
```

---

## 🔐 Autenticación y Permisos

### Obtener Token de Autenticación
**POST** `/auth/login/`

```json
{
    "username": "admin",
    "password": "admin123"
}
```

#### Response:
```json
{
    "token": "a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0",
    "user": {
        "id": 1,
        "username": "admin",
        "role": "admin",
        "is_verified": true
    }
}
```

### Roles y Permisos

| Endpoint | Administrador | Monitor | Comentarios |
|----------|:-------------:|:-------:|-------------|
| `GET /courses/` | ✅ (todos) | ✅ (solo suyos) | Lista filtrada por rol |
| `POST /courses/` | ✅ | ❌ | Solo admin puede crear |
| `PUT/PATCH /courses/{id}/` | ✅ | ❌ | Solo admin puede editar |
| `DELETE /courses/{id}/` | ✅ | ❌ | Solo admin puede eliminar |
| `GET /courses/my_courses/` | ❌ | ✅ | Endpoint específico para monitores |
| `GET /courses/upcoming/` | ✅ | ✅ | Ambos pueden ver próximos |
| `GET /courses/current/` | ✅ | ✅ | Ambos pueden ver actuales |
| `GET /courses/{id}/history/` | ✅ | ✅ | Historial visible para ambos |
| `GET /admin/courses/overview/` | ✅ | ❌ | Solo administradores |

---

## 🚨 Códigos de Error Comunes

| Código | Descripción | Ejemplo |
|--------|-------------|---------|
| 400 | Datos inválidos | Campos requeridos faltantes |
| 401 | No autenticado | Token inválido o faltante |
| 403 | Sin permisos | Monitor intentando crear curso |
| 404 | No encontrado | Curso con ID inexistente |
| 409 | Conflicto | Horario ocupado |
| 500 | Error servidor | Error interno |

---

## 📝 Notas de Implementación

- **Fechas**: Usar formato ISO 8601 (`2025-10-15T08:00:00Z`)
- **Paginación**: Respuestas grandes están paginadas (20 items por página)
- **Filtros**: Soporta búsqueda, filtrado y ordenamiento
- **Validación**: Validación automática de conflictos de horario
- **Historial**: Todos los cambios quedan registrados automáticamente
- **Permisos**: Sistema de roles robusto (admin/monitor)

---

## 🔧 Variables de Entorno para Testing

```bash
# .env
DEBUG=True
DJANGO_SETTINGS_MODULE=ds2_back.settings
SECRET_KEY=your-secret-key
DATABASE_URL=sqlite:///db.sqlite3
```