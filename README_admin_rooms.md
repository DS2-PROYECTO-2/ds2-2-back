# 📝 Documentación de Endpoints CRUD de Salas para Administradores

## 🔐 Autenticación y Permisos

Todos los endpoints de administración requieren:
- **Token de autenticación**: `Authorization: Token <token>`
- **Rol de administrador**: `user.role == 'admin'`
- **Usuario verificado**: `user.is_verified == True`

---

## 📋 Endpoints Disponibles

### **Base URL**: `/api/rooms/admin/rooms/`

---

## 1. 📖 **Listar Salas** → `GET` - Obtener todas las salas
```
GET /api/rooms/admin/rooms/
```

**Descripción**: Lista todas las salas con información detallada y conteo de ocupantes actuales.

**Parámetros Query** (opcionales):
- `include_inactive` (boolean): Incluir salas inactivas. Default: `false`
- `search` (string): Buscar por nombre, código o descripción

**Headers**:
```
Authorization: Token <admin_token>
```

**Respuesta Exitosa** (200):
```json
{
  "count": 3,
  "include_inactive": false,
  "search": null,
  "rooms": [
    {
      "id": 1,
      "name": "Laboratorio de Redes",
      "code": "LR001", 
      "capacity": 30,
      "description": "Laboratorio equipado para redes",
      "is_active": true,
      "created_at": "2025-10-03T10:00:00Z",
      "updated_at": "2025-10-03T10:00:00Z",
      "occupants_count": 2
    }
  ]
}
```

**Ejemplo con filtros**:
```bash
GET /api/rooms/admin/rooms/?search=Laboratorio&include_inactive=true
```

---

## 2. ➕ **Crear Sala** → `POST` - Crear nueva sala
```
POST /api/rooms/admin/rooms/create/
```

**Descripción**: Crea una nueva sala. Solo administradores pueden realizar esta acción.

**Headers**:
```
Authorization: Token <admin_token>
Content-Type: application/json
```

**Body**:
```json
{
  "name": "Nueva Sala",
  "code": "NS001",
  "capacity": 25,
  "description": "Descripción de la nueva sala",
  "is_active": true
}
```

**Respuesta Exitosa** (201):
```json
{
  "message": "Sala creada exitosamente",
  "room": {
    "id": 4,
    "name": "Nueva Sala",
    "code": "NS001",
    "capacity": 25,
    "description": "Descripción de la nueva sala", 
    "is_active": true,
    "created_at": "2025-10-03T15:30:00Z",
    "updated_at": "2025-10-03T15:30:00Z",
    "occupants_count": 0
  }
}
```

**Errores**:
- `400`: Datos inválidos (código/nombre duplicado, capacidad inválida)
- `403`: Sin permisos de administrador

---

## 3. 🔍 **Ver Detalle de Sala** → `GET` - Detalle y estadísticas
```
GET /api/rooms/admin/rooms/{room_id}/
```

**Descripción**: Obtiene información detallada de una sala específica con estadísticas de uso.

**Headers**:
```
Authorization: Token <admin_token>
```

**Respuesta Exitosa** (200):
```json
{
  "room": {
    "id": 1,
    "name": "Laboratorio de Redes",
    "code": "LR001",
    "capacity": 30,
    "description": "Laboratorio equipado",
    "is_active": true,
    "created_at": "2025-10-03T10:00:00Z",
    "updated_at": "2025-10-03T10:00:00Z",
    "occupants_count": 2
  },
  "statistics": {
    "current_occupants": 2,
    "total_entries_historical": 150,
    "total_hours_usage": 1245.5,
    "active_entries": [
      {
        "id": 25,
        "user_username": "monitor123",
        "user_full_name": "Juan Pérez",
        "entry_time": "2025-10-03T14:00:00Z",
        "duration_minutes": 90.5
      }
    ]
  }
}
```

---

## 4. ✏️ **Actualizar Sala** → `PUT/PATCH` - Modificar sala existente
```
PUT /api/rooms/admin/rooms/{room_id}/update/
PATCH /api/rooms/admin/rooms/{room_id}/update/
```

**Descripción**: Actualiza una sala existente. `PUT` requiere todos los campos, `PATCH` permite actualización parcial.

**Headers**:
```
Authorization: Token <admin_token>
Content-Type: application/json
```

**Body** (PATCH ejemplo):
```json
{
  "name": "Laboratorio Actualizado",
  "capacity": 35
}
```

**Respuesta Exitosa** (200):
```json
{
  "message": "Sala actualizada exitosamente",
  "room": {
    "id": 1,
    "name": "Laboratorio Actualizado",
    "code": "LR001",
    "capacity": 35,
    "description": "Laboratorio equipado",
    "is_active": true,
    "created_at": "2025-10-03T10:00:00Z",
    "updated_at": "2025-10-03T15:45:00Z",
    "occupants_count": 2
  }
}
```

**Restricciones**:
- No se puede desactivar (`is_active: false`) una sala con ocupantes activos
- Validaciones de unicidad para nombre y código

**Errores**:
- `400`: No se puede desactivar sala con ocupantes activos
- `400`: Datos inválidos (duplicados, etc.)

---

## 5. 🗑️ **Eliminar Sala**
```
DELETE /api/rooms/admin/rooms/{room_id}/delete/
```

**Descripción**: Elimina una sala. El comportamiento depende del historial:
- **Hard Delete**: Si no tiene registros históricos, se elimina completamente
- **Soft Delete**: Si tiene historial, se marca como inactiva

**Headers**:
```
Authorization: Token <admin_token>
```

**Respuesta - Hard Delete** (200):
```json
{
  "message": "Sala eliminada completamente",
  "details": "La sala no tenía registros históricos, por lo que se eliminó completamente.",
  "action": "hard_delete",
  "deleted_room": {
    "id": 4,
    "name": "Sala Sin Historial",
    "code": "SSH001"
  }
}
```

**Respuesta - Soft Delete** (200):
```json
{
  "message": "Sala marcada como eliminada exitosamente", 
  "details": "La sala tenía 45 registros históricos, por lo que se marcó como inactiva en lugar de eliminarla físicamente.",
  "action": "soft_delete",
  "room": {
    "id": 1,
    "name": "Laboratorio de Redes (ELIMINADA)",
    "is_active": false
  }
}
```

**Restricciones**:
- No se puede eliminar una sala con ocupantes activos

**Errores**:
- `400`: Sala tiene ocupantes activos
- `404`: Sala no encontrada

---

## 🚫 **Errores Comunes**

### **401 Unauthorized**
```json
{
  "detail": "Authentication credentials were not provided."
}
```

### **403 Forbidden**
```json
{
  "detail": "Solo los administradores verificados pueden realizar esta acción."
}
```

### **400 Bad Request** (Validación)
```json
{
  "error": "Datos inválidos para crear la sala",
  "details": {
    "code": ["Ya existe una sala con este código."],
    "capacity": ["La capacidad debe ser mayor a 0."]
  }
}
```

### **404 Not Found**
```json
{
  "detail": "Not found."
}
```

---

## 🧪 **Ejemplos de Uso**

### **Crear nueva sala**
```bash
curl -X POST http://localhost:8000/api/rooms/admin/rooms/create/ \
  -H "Authorization: Token abc123..." \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Sala de Conferencias",
    "code": "SC001", 
    "capacity": 50,
    "description": "Sala equipada para videoconferencias"
  }'
```

### **Buscar salas**
```bash
curl -X GET "http://localhost:8000/api/rooms/admin/rooms/?search=Laboratorio&include_inactive=true" \
  -H "Authorization: Token abc123..."
```

### **Actualizar capacidad**
```bash
curl -X PATCH http://localhost:8000/api/rooms/admin/rooms/1/update/ \
  -H "Authorization: Token abc123..." \
  -H "Content-Type: application/json" \
  -d '{"capacity": 40}'
```

### **Ver estadísticas detalladas**
```bash
curl -X GET http://localhost:8000/api/rooms/admin/rooms/1/ \
  -H "Authorization: Token abc123..."
```

---

## ⚡ **Características Especiales**

### **🔍 Búsqueda Inteligente**
El parámetro `search` busca en:
- Nombre de la sala
- Código de la sala  
- Descripción de la sala

### **📊 Conteo de Ocupantes en Tiempo Real**
Todos los endpoints de listado incluyen `occupants_count` que muestra el número actual de usuarios activos en cada sala.

### **🛡️ Eliminación Inteligente**
- **Sin historial** → Eliminación completa (hard delete)
- **Con historial** → Marcado como inactiva (soft delete)
- **Con ocupantes activos** → Bloqueado hasta que salgan

### **🔒 Seguridad Robusta**
- Solo administradores verificados pueden acceder
- Validaciones de negocio para prevenir inconsistencias
- Transacciones atómicas para integridad de datos

---

## 📈 **URLs Completas**

| Método | URL | Descripción |
|--------|-----|-------------|
| `GET` | `/api/rooms/admin/rooms/` | Listar salas |
| `POST` | `/api/rooms/admin/rooms/create/` | Crear sala |
| `GET` | `/api/rooms/admin/rooms/{id}/` | Ver detalle |
| `PUT/PATCH` | `/api/rooms/admin/rooms/{id}/update/` | Actualizar |
| `DELETE` | `/api/rooms/admin/rooms/{id}/delete/` | Eliminar |

---

## ✅ **Tests Incluidos**

Se han implementado **15 tests comprehensivos** que cubren:
- ✅ Creación exitosa y validaciones
- ✅ Actualización con restricciones de ocupantes  
- ✅ Eliminación inteligente (hard/soft delete)
- ✅ Búsqueda y filtrado
- ✅ Permisos y seguridad
- ✅ Casos edge y manejo de errores

**Ejecutar tests**: `python manage.py test rooms.tests.test_admin_room_crud`