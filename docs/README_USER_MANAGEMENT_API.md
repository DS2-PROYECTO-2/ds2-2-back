# 📋 **API de Gestión de Usuarios - Casos de Prueba en Postman**

## 🎯 **Descripción**

Documentación completa del endpoint **CONSOLIDADO** para la gestión administrativa de usuarios, incluyendo casos de prueba detallados para Postman.

### ✨ **Funcionalidades Consolidadas en un Solo Endpoint**
- ✅ **Editar información personal** (nombre, email, teléfono, etc.)
- ✅ **Cambiar roles** (monitor ↔ admin) 
- ✅ **Verificar/Desverificar usuarios** (is_verified)
- ✅ **Consultar detalle de usuarios** específicos
- ✅ **Búsqueda avanzada** con múltiples filtros
- ✅ **Validaciones de seguridad** (admins no pueden editarse entre sí)
- ✅ **Paginación** en resultados de búsqueda

### 🔄 **Endpoints Deprecados (ahora consolidados)**
- ❌ `/admin/users/{id}/verify/` → Usar `/admin/users/{id}/edit/` con `is_verified`
- ❌ `/admin/users/{id}/promote/` → Usar `/admin/users/{id}/edit/` con `role`

---

## 🔐 **Autenticación Requerida**

Todos los endpoints requieren:
```http
Authorization: Token <admin_token>
Content-Type: application/json
```

### **Obtener Token de Admin**
```http
POST /api/users/login/
Content-Type: application/json

{
  "username": "admin_user",
  "password": "admin_password"
}
```

---

## 📋 **CASOS DE PRUEBA EN POSTMAN**

### **🗂️ Colección: User Management API**

---

## 1️⃣ **ENDPOINT: Editar Usuario**

### **📁 Carpeta: Admin - Edit Users**

#### **🟢 1.1 Editar Información Personal - Éxito**
```http
PATCH {{base_url}}/api/users/admin/users/{{monitor_user_id}}/edit/
Authorization: Token {{admin_token}}
Content-Type: application/json

{
  "first_name": "Monitor Actualizado",
  "last_name": "Apellido Nuevo",
  "email": "monitor_actualizado@test.com",
  "phone": "9876543210",
  "identification": "87654321"
  "role": "monitor"
  "is_verified": "false"

}
```
**Expected Status:** `200 OK`  
**Expected Response:**
```json
{
  "message": "Usuario monitor_test actualizado exitosamente: first_name actualizado, last_name actualizado, email actualizado",
  "user": {
    "id": 3,
    "username": "monitor_test",
    "first_name": "Monitor Actualizado",
    "last_name": "Apellido Nuevo",
    "email": "monitor_actualizado@test.com",
    "phone": "9876543210",
    "identification": "87654321",
    "role": "monitor",
    "is_verified": true
  }
}
```

#### **🟢 1.2 Cambiar Rol (Monitor → Admin)**
```http
PATCH {{base_url}}/api/users/admin/users/{{monitor_user_id}}/edit/
Authorization: Token {{admin_token}}
Content-Type: application/json

{
  "role": "admin"
}
```
**Expected Status:** `200 OK`  
**Expected Response:**
```json
{
  "message": "Usuario monitor_test actualizado exitosamente: ascendido a admin",
  "user": {
    "id": 3,
    "username": "monitor_test",
    "role": "admin",
    "is_verified": true
  }
}
```

#### **🟢 1.3 Verificar Usuario**
```http
PATCH {{base_url}}/api/users/admin/users/{{unverified_user_id}}/edit/
Authorization: Token {{admin_token}}
Content-Type: application/json

{
  "is_verified": true
}
```
**Expected Status:** `200 OK`  
**Expected Response:**
```json
{
  "message": "Usuario unverified_user actualizado exitosamente: verificado",
  "user": {
    "id": 4,
    "username": "unverified_user",
    "role": "monitor",
    "is_verified": true
  }
}
```

#### **🟢 1.4 Desverificar Usuario**
```http
PATCH {{base_url}}/api/users/admin/users/{{verified_user_id}}/edit/
Authorization: Token {{admin_token}}
Content-Type: application/json

{
  "is_verified": false
}
```
**Expected Status:** `200 OK`  
**Expected Response:**
```json
{
  "message": "Usuario verified_user actualizado exitosamente: desverificado",
  "user": {
    "id": 5,
    "username": "verified_user",
    "role": "monitor",
    "is_verified": false
  }
}
```

#### **🟢 1.5 Editar Múltiples Campos a la Vez**
```http
PATCH {{base_url}}/api/users/admin/users/{{monitor_user_id}}/edit/
Authorization: Token {{admin_token}}
Content-Type: application/json

{
  "first_name": "Nuevo Nombre",
  "email": "nuevo@email.com",
  "role": "admin",
  "is_verified": true
}
```
**Expected Status:** `200 OK`  
**Expected Response:**
```json
{
  "message": "Usuario monitor_test actualizado exitosamente: first_name actualizado, email actualizado, ascendido a admin, verificado",
  "user": {
    "id": 3,
    "username": "monitor_test",
    "first_name": "Nuevo Nombre",
    "email": "nuevo@email.com",
    "role": "admin",
    "is_verified": true
  }
}
```

#### **🔴 1.6 Editar Otro Admin - Prohibido**
```http
PATCH {{base_url}}/api/users/admin/users/{{another_admin_id}}/edit/
Authorization: Token {{admin_token}}
Content-Type: application/json

{
  "first_name": "Intento de Hack",
  "email": "hacked@test.com"
}
```
**Expected Status:** `403 Forbidden`  
**Expected Response:**
```json
{
  "error": "No se puede editar información de otros administradores"
}
```

#### **🔴 1.7 Editar con Campos Inválidos**
```http
PATCH {{base_url}}/api/users/admin/users/{{monitor_user_id}}/edit/
Authorization: Token {{admin_token}}
Content-Type: application/json

{
  "password": "newpassword",
  "username": "hacked_user",
  "invalid_field": "value"
}
```
**Expected Status:** `400 Bad Request`  
**Expected Response:**
```json
{
  "error": "No se proporcionaron campos válidos para actualizar"
}
```

#### **🔴 1.8 Rol Inválido**
```http
PATCH {{base_url}}/api/users/admin/users/{{monitor_user_id}}/edit/
Authorization: Token {{admin_token}}
Content-Type: application/json

{
  "role": "invalid_role"
}
```
**Expected Status:** `400 Bad Request`  
**Expected Response:**
```json
{
  "error": "Rol inválido. Solo se permite \"admin\" o \"monitor\""
}
```

#### **🔴 1.9 Valor de Verificación Inválido**
```http
PATCH {{base_url}}/api/users/admin/users/{{monitor_user_id}}/edit/
Authorization: Token {{admin_token}}
Content-Type: application/json

{
  "is_verified": "maybe"
}
```
**Expected Status:** `400 Bad Request`  
**Expected Response:**
```json
{
  "error": "is_verified debe ser true o false"
}
```

#### **🔴 1.10 Editar Usuario Inexistente**
```http
PATCH {{base_url}}/api/users/admin/users/99999/edit/
Authorization: Token {{admin_token}}
Content-Type: application/json

{
  "first_name": "Test"
}
```
**Expected Status:** `404 Not Found`  
**Expected Response:**
```json
{
  "error": "Usuario con ID 99999 no encontrado"
}
```

---

## 2️⃣ **ENDPOINT: Detalle de Usuario**

### **📁 Carpeta: Admin - User Details**

#### **🟢 2.1 Ver Detalle de Monitor**
```http
GET {{base_url}}/api/users/admin/users/{{monitor_user_id}}/detail/
Authorization: Token {{admin_token}}
```
**Expected Status:** `200 OK`  
**Expected Response:**
```json
{
  "user": {
    "id": 3,
    "username": "monitor_test",
    "first_name": "Monitor",
    "last_name": "Test",
    "email": "monitor@test.com",
    "phone": "1234567890",
    "identification": "87654321",
    "role": "monitor",
    "is_verified": true,
    "date_joined": "2025-10-08T10:30:00.000Z",
    "last_login": "2025-10-08T14:15:00.000Z",
    "is_active": true
  }
}
```

#### **🟢 2.2 Ver Detalle de Admin**
```http
GET {{base_url}}/api/users/admin/users/{{admin_user_id}}/detail/
Authorization: Token {{admin_token}}
```
**Expected Status:** `200 OK`

#### **🔴 2.3 Usuario Inexistente**
```http
GET {{base_url}}/api/users/admin/users/99999/detail/
Authorization: Token {{admin_token}}
```
**Expected Status:** `404 Not Found`  
**Expected Response:**
```json
{
  "error": "Usuario con ID 99999 no encontrado"
}
```

---

## 3️⃣ **ENDPOINT: Búsqueda Avanzada de Usuarios**

### **📁 Carpeta: Admin - User Search**

#### **🟢 3.1 Listar Todos los Usuarios**
```http
GET {{base_url}}/api/users/admin/users/search/
Authorization: Token {{admin_token}}
```
**Expected Status:** `200 OK`  
**Expected Response:**
```json
{
  "users": [
    {
      "id": 1,
      "username": "admin_user",
      "first_name": "Admin",
      "last_name": "User",
      "email": "admin@test.com",
      "role": "admin",
      "is_verified": true,
      "is_active": true,
      "date_joined": "2025-10-08T10:00:00.000Z"
    }
  ],
  "pagination": {
    "total_count": 3,
    "page": 1,
    "page_size": 20,
    "total_pages": 1
  },
  "filters_applied": {
    "role": null,
    "is_verified": null,
    "is_active": null,
    "search": null,
    "order_by": "date_joined"
  }
}
```

#### **🟢 3.2 Filtrar Solo Monitores**
```http
GET {{base_url}}/api/users/admin/users/search/?role=monitor
Authorization: Token {{admin_token}}
```
**Expected Status:** `200 OK`  
**Variables to Set:** Verificar que todos los usuarios tienen `"role": "monitor"`

#### **🟢 3.3 Filtrar Solo Administradores**
```http
GET {{base_url}}/api/users/admin/users/search/?role=admin
Authorization: Token {{admin_token}}
```
**Expected Status:** `200 OK`  
**Variables to Set:** Verificar que todos los usuarios tienen `"role": "admin"`

#### **🟢 3.4 Filtrar Usuarios No Verificados**
```http
GET {{base_url}}/api/users/admin/users/search/?is_verified=false
Authorization: Token {{admin_token}}
```
**Expected Status:** `200 OK`  
**Variables to Set:** Verificar que todos los usuarios tienen `"is_verified": false`

#### **🟢 3.5 Filtrar Usuarios Verificados**
```http
GET {{base_url}}/api/users/admin/users/search/?is_verified=true
Authorization: Token {{admin_token}}
```
**Expected Status:** `200 OK`  
**Variables to Set:** Verificar que todos los usuarios tienen `"is_verified": true`

#### **🟢 3.6 Filtrar Usuarios Activos**
```http
GET {{base_url}}/api/users/admin/users/search/?is_active=true
Authorization: Token {{admin_token}}
```
**Expected Status:** `200 OK`

#### **🟢 3.7 Filtrar Usuarios Inactivos**
```http
GET {{base_url}}/api/users/admin/users/search/?is_active=false
Authorization: Token {{admin_token}}
```
**Expected Status:** `200 OK`

#### **🟢 3.8 Búsqueda por Texto - Username**
```http
GET {{base_url}}/api/users/admin/users/search/?search=monitor_test
Authorization: Token {{admin_token}}
```
**Expected Status:** `200 OK`  
**Expected:** Al menos un usuario con username que contenga "monitor_test"

#### **🟢 3.9 Búsqueda por Texto - Email**
```http
GET {{base_url}}/api/users/admin/users/search/?search=@test.com
Authorization: Token {{admin_token}}
```
**Expected Status:** `200 OK`  
**Expected:** Usuarios con emails que contengan "@test.com"

#### **🟢 3.10 Búsqueda por Texto - Nombre**
```http
GET {{base_url}}/api/users/admin/users/search/?search=Monitor
Authorization: Token {{admin_token}}
```
**Expected Status:** `200 OK`  
**Expected:** Usuarios con nombres que contengan "Monitor"

#### **🟢 3.11 Búsqueda por Texto - Identificación**
```http
GET {{base_url}}/api/users/admin/users/search/?search=87654321
Authorization: Token {{admin_token}}
```
**Expected Status:** `200 OK`  
**Expected:** Usuario con identification "87654321"

#### **🟢 3.12 Filtros Combinados**
```http
GET {{base_url}}/api/users/admin/users/search/?role=monitor&is_verified=true&search=test
Authorization: Token {{admin_token}}
```
**Expected Status:** `200 OK`  
**Expected:** Monitores verificados con "test" en algún campo

#### **🟢 3.13 Ordenamiento Ascendente por Username**
```http
GET {{base_url}}/api/users/admin/users/search/?order_by=username
Authorization: Token {{admin_token}}
```
**Expected Status:** `200 OK`  
**Expected:** Usuarios ordenados alfabéticamente por username

#### **🟢 3.14 Ordenamiento Descendente por Fecha**
```http
GET {{base_url}}/api/users/admin/users/search/?order_by=-date_joined
Authorization: Token {{admin_token}}
```
**Expected Status:** `200 OK`  
**Expected:** Usuarios ordenados por fecha de registro (más recientes primero)

#### **🟢 3.15 Paginación - Primera Página**
```http
GET {{base_url}}/api/users/admin/users/search/?page=1&page_size=2
Authorization: Token {{admin_token}}
```
**Expected Status:** `200 OK`  
**Expected Response Structure:**
```json
{
  "users": [/* máximo 2 usuarios */],
  "pagination": {
    "total_count": 3,
    "page": 1,
    "page_size": 2,
    "total_pages": 2
  }
}
```

#### **🟢 3.16 Paginación - Segunda Página**
```http
GET {{base_url}}/api/users/admin/users/search/?page=2&page_size=2
Authorization: Token {{admin_token}}
```
**Expected Status:** `200 OK`  
**Expected:** Diferentes usuarios que en la página 1

#### **🟢 3.17 Página Vacía**
```http
GET {{base_url}}/api/users/admin/users/search/?page=999&page_size=10
Authorization: Token {{admin_token}}
```
**Expected Status:** `200 OK`  
**Expected:** Array vacío de usuarios

---

## 4️⃣ **VALIDACIONES DE SEGURIDAD**

### **📁 Carpeta: Security - Access Control**

#### **🔴 4.1 Monitor Intenta Editar Usuario**
```http
PATCH {{base_url}}/api/users/admin/users/{{monitor_user_id}}/edit/
Authorization: Token {{monitor_token}}
Content-Type: application/json

{
  "first_name": "Hack Attempt"
}
```
**Expected Status:** `403 Forbidden`

#### **🔴 4.2 Monitor Intenta Ver Detalles**
```http
GET {{base_url}}/api/users/admin/users/{{admin_user_id}}/detail/
Authorization: Token {{monitor_token}}
```
**Expected Status:** `403 Forbidden`

#### **🔴 4.3 Monitor Intenta Buscar Usuarios**
```http
GET {{base_url}}/api/users/admin/users/search/
Authorization: Token {{monitor_token}}
```
**Expected Status:** `403 Forbidden`

#### **🔴 4.4 Sin Token de Autenticación**
```http
GET {{base_url}}/api/users/admin/users/search/
```
**Expected Status:** `401 Unauthorized`

#### **🔴 4.5 Token Inválido**
```http
GET {{base_url}}/api/users/admin/users/search/
Authorization: Token invalid_token_12345
```
**Expected Status:** `401 Unauthorized`

---

## 5️⃣ **ESCENARIOS DE PRUEBA COMPLETOS**

### **📋 Escenario 1: Gestión Completa de Monitor (TODO EN UN ENDPOINT)**

1. **Buscar monitores no verificados** → `GET /search/?role=monitor&is_verified=false`
2. **Ver detalle del monitor** → `GET /users/{id}/detail/`
3. **Editar información completa** → `PATCH /users/{id}/edit/` con múltiples campos:
   ```json
   {
     "first_name": "Nombre Actualizado",
     "email": "nuevo@email.com",
     "is_verified": true,
     "role": "admin"
   }
   ```
4. **Confirmar cambios** → `GET /users/{id}/detail/`

### **📋 Escenario 2: Búsqueda y Filtrado Avanzado**

1. **Listar todos** → `GET /search/`
2. **Filtrar por rol** → `GET /search/?role=monitor`
3. **Filtrar por verificación** → `GET /search/?is_verified=false`
4. **Combinar filtros** → `GET /search/?role=monitor&is_verified=false`
5. **Buscar por texto** → `GET /search/?search=juan`
6. **Aplicar paginación** → `GET /search/?page=1&page_size=5`

### **📋 Escenario 3: Validaciones de Seguridad**

1. **Login como Admin** → Obtener admin_token
2. **Login como Monitor** → Obtener monitor_token
3. **Intentar acceso como Monitor** → Debe fallar (403)
4. **Intentar editar otro Admin** → Debe fallar (403)
5. **Intentar campos inválidos** → Debe fallar (400)

---

## 🔧 **VARIABLES DE ENTORNO PARA POSTMAN**

### **Variables Globales:**
```json
{
  "base_url": "http://127.0.0.1:8000",
  "admin_token": "",
  "monitor_token": "",
  "admin_user_id": "",
  "monitor_user_id": "",
  "another_admin_id": ""
}
```

### **Scripts de Pre-request (Postman):**

#### **Setup Initial Data:**
```javascript
// Ejecutar una vez para configurar IDs de usuarios
pm.sendRequest({
    url: pm.globals.get("base_url") + "/api/users/admin/users/",
    method: 'GET',
    header: {
        'Authorization': 'Token ' + pm.globals.get("admin_token")
    }
}, function (err, response) {
    if (!err && response.code === 200) {
        const users = response.json().users;
        const admin = users.find(u => u.role === 'admin');
        const monitor = users.find(u => u.role === 'monitor');
        
        if (admin) pm.globals.set("admin_user_id", admin.id);
        if (monitor) pm.globals.set("monitor_user_id", monitor.id);
    }
});
```

### **Tests Scripts (Postman):**

#### **Verify Response Structure:**
```javascript
// Test para verificar estructura de respuesta en búsquedas
pm.test("Response has correct structure", function () {
    const jsonData = pm.response.json();
    pm.expect(jsonData).to.have.property('users');
    pm.expect(jsonData).to.have.property('pagination');
    pm.expect(jsonData.pagination).to.have.property('total_count');
    pm.expect(jsonData.pagination).to.have.property('page');
    pm.expect(jsonData.pagination).to.have.property('page_size');
});
```

#### **Verify User Edit Success:**
```javascript
// Test para verificar edición exitosa
pm.test("User updated successfully", function () {
    const jsonData = pm.response.json();
    pm.expect(jsonData).to.have.property('message');
    pm.expect(jsonData.message).to.include('actualizado exitosamente');
    pm.expect(jsonData).to.have.property('user');
});
```

---

## 📊 **ESTRUCTURA DE RESPUESTAS**

### **Respuesta de Éxito - Editar Usuario:**
```json
{
  "message": "Usuario {username} actualizado exitosamente",
  "user": {
    "id": 123,
    "username": "username",
    "first_name": "Nombre",
    "last_name": "Apellido",
    "email": "email@test.com",
    "phone": "1234567890",
    "identification": "12345678",
    "role": "monitor",
    "is_verified": true
  }
}
```

### **Respuesta de Éxito - Detalle Usuario:**
```json
{
  "user": {
    "id": 123,
    "username": "username",
    "first_name": "Nombre",
    "last_name": "Apellido",
    "email": "email@test.com",
    "phone": "1234567890",
    "identification": "12345678",
    "role": "monitor",
    "is_verified": true,
    "date_joined": "2025-10-08T10:30:00.000Z",
    "last_login": "2025-10-08T14:15:00.000Z",
    "is_active": true
  }
}
```

### **Respuesta de Éxito - Búsqueda:**
```json
{
  "users": [
    {
      "id": 123,
      "username": "username",
      "first_name": "Nombre",
      "last_name": "Apellido",
      "email": "email@test.com",
      "role": "monitor",
      "is_verified": true,
      "is_active": true,
      "date_joined": "2025-10-08T10:30:00.000Z"
    }
  ],
  "pagination": {
    "total_count": 25,
    "page": 1,
    "page_size": 20,
    "total_pages": 2
  },
  "filters_applied": {
    "role": "monitor",
    "is_verified": "true",
    "is_active": null,
    "search": "juan",
    "order_by": "username"
  }
}
```

### **Respuestas de Error:**
```json
// 403 Forbidden
{
  "error": "No se puede editar información de otros administradores"
}

// 404 Not Found
{
  "error": "Usuario con ID 99999 no encontrado"
}

// 400 Bad Request
{
  "error": "No se proporcionaron campos válidos para actualizar"
}
```

---

## ⚡ **PARÁMETROS DE BÚSQUEDA DISPONIBLES**

| Parámetro | Valores | Descripción |
|-----------|---------|-------------|
| `role` | `admin`, `monitor` | Filtrar por rol de usuario |
| `is_verified` | `true`, `false` | Filtrar por estado de verificación |
| `is_active` | `true`, `false` | Filtrar por estado activo |
| `search` | `texto` | Buscar en username, email, nombres, identificación |
| `order_by` | `username`, `email`, `role`, `is_verified`, `date_joined` | Campo de ordenamiento |
| `order_by` | `-field` | Ordenamiento descendente (agregar `-` al inicio) |
| `page` | `1, 2, 3...` | Número de página |
| `page_size` | `1-100` | Cantidad de resultados por página |

---

## 🎯 **CAMPOS EDITABLES**

### **✅ Campos Permitidos en Edición (CONSOLIDADO):**

#### **📝 Información Personal:**
- `first_name` - Nombre
- `last_name` - Apellido  
- `email` - Correo electrónico
- `phone` - Teléfono
- `identification` - Número de identificación

#### **🔧 Campos Administrativos:**
- `role` - Rol (`"admin"` o `"monitor"`) ✨ **NUEVO**
- `is_verified` - Verificación (`true` o `false`) ✨ **NUEVO**

### **❌ Campos NO Editables:**
- `username` - Nombre de usuario (fijo)
- `password` - Contraseña (usar endpoint `/change-password/`)
- `is_active` - Estado activo (solo por admin en panel Django)
- `date_joined` - Fecha de registro (automático)
- `last_login` - Último acceso (automático)

---

## 🚀 **NOTAS IMPORTANTES**

1. **🔄 Endpoint Consolidado**: Toda la gestión de usuarios en `/edit/` - ya no necesitas endpoints separados
2. **🛡️ Seguridad**: Solo administradores pueden usar estos endpoints
3. **🔒 Protección entre Admins**: Un admin no puede editar a otro admin
4. **✅ Validación Inteligente**: Acepta cualquier combinación de campos válidos
5. **📊 Mensajes Descriptivos**: La respuesta indica exactamente qué cambios se realizaron
6. **🔄 Conversión Automática**: `is_verified` acepta `true`/`false` como string o boolean
7. **📋 Paginación**: Máximo 100 resultados por página en búsquedas
8. **🔍 Búsqueda**: Case-insensitive en todos los campos de texto
9. **📈 Ordenamiento**: Disponible para campos principales
10. **🎯 Filtros**: Se pueden combinar múltiples filtros

### **⚠️ Endpoints Deprecados:**
- ❌ `/admin/users/{id}/verify/` → Usar `/admin/users/{id}/edit/` con `{"is_verified": true}`
- ❌ `/admin/users/{id}/promote/` → Usar `/admin/users/{id}/edit/` con `{"role": "admin"}`

---

**🎯 APIs completamente funcionales con 158 tests exitosos y documentación completa para Postman.**