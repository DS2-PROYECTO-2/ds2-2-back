# 📋 Resumen: Endpoints de Usuarios - Campos Devueltos

## ✅ **Confirmación: Los endpoints SÍ devuelven `identification` y `role`**

### 🔍 **Endpoints Verificados**

#### **1. Login (`POST /api/auth/login/`)**
**Serializer usado:** `UserProfileCompleteSerializer`

**Campos devueltos:**
```json
{
  "message": "Login exitoso",
  "token": "token_aqui",
  "user": {
    "id": 30,
    "username": "admin",
    "email": "admin@ejemplo.com",
    "first_name": "Admin",
    "last_name": "Sistema",
    "identification": "00000000",
    "phone": "",
    "role": "admin",
    "role_display": "Administrador",
    "is_verified": true,
    "verified_by_name": null,
    "verification_date": null,
    "date_joined": "2024-01-01T10:00:00Z",
    "created_at": "2024-01-01T10:00:00Z"
  }
}
```

**✅ Campos confirmados:**
- ✅ `identification` - Número de identificación
- ✅ `role` - Rol del usuario (admin/monitor)
- ✅ `role_display` - Nombre del rol en español

#### **2. Registro (`POST /api/auth/register/`)**
**Serializer usado:** `UserProfileCompleteSerializer`

**Campos devueltos:**
```json
{
  "message": "Usuario registrado exitosamente",
  "user": {
    "id": 31,
    "username": "nuevo_usuario",
    "email": "usuario@ejemplo.com",
    "first_name": "Usuario",
    "last_name": "Nuevo",
    "identification": "12345678",
    "phone": "3001234567",
    "role": "monitor",
    "role_display": "Monitor",
    "is_verified": false,
    "verified_by_name": null,
    "verification_date": null,
    "date_joined": "2024-01-01T10:00:00Z",
    "created_at": "2024-01-01T10:00:00Z"
  }
}
```

**✅ Campos confirmados:**
- ✅ `identification` - Número de identificación
- ✅ `role` - Rol del usuario (admin/monitor)
- ✅ `role_display` - Nombre del rol en español

#### **3. Perfil (`GET /api/auth/profile/`)**
**Serializer usado:** `UserProfileSerializer`

**Campos devueltos:**
```json
{
  "first_name": "Admin",
  "last_name": "Sistema",
  "username": "admin",
  "email": "admin@ejemplo.com",
  "phone": "",
  "identification": "00000000"
}
```

**⚠️ Nota:** El endpoint de perfil NO incluye `role` (solo campos editables)

## 📊 **Comparación de Serializers**

### **UserProfileCompleteSerializer** (Login/Registro)
```python
fields = [
    'id', 'username', 'email', 'first_name', 'last_name',
    'identification', 'phone', 'role', 'role_display',
    'is_verified', 'verified_by_name', 'verification_date',
    'date_joined', 'created_at'
]
```

### **UserProfileSerializer** (Perfil)
```python
fields = [
    'first_name', 'last_name', 'username', 'email', 'phone', 'identification'
]
```

## 🎯 **Respuesta a tu Pregunta**

### **¿El endpoint devuelve `identification` y `role`?**

**✅ SÍ, pero depende del endpoint:**

1. **Login (`/api/auth/login/`)** - ✅ SÍ devuelve ambos
2. **Registro (`/api/auth/register/`)** - ✅ SÍ devuelve ambos  
3. **Perfil (`/api/auth/profile/`)** - ⚠️ Solo devuelve `identification`, NO `role`

## 🔧 **Para Obtener Todos los Campos**

### **Opción 1: Usar Login**
```javascript
// Después del login, guardar todos los datos del usuario
const loginResponse = await fetch('/api/auth/login/', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ username, password })
});

const data = await loginResponse.json();
const userData = data.user; // Contiene identification, role, etc.
```

### **Opción 2: Usar Dashboard**
```javascript
// El dashboard devuelve información completa del usuario
const dashboardResponse = await fetch('/api/dashboard/', {
  headers: { 'Authorization': `Token ${token}` }
});

const data = await dashboardResponse.json();
const userInfo = data.user_info; // Contiene todos los campos
```

## 📋 **Campos Disponibles por Endpoint**

| Campo | Login | Registro | Perfil | Dashboard |
|-------|-------|----------|--------|-----------|
| `id` | ✅ | ✅ | ❌ | ✅ |
| `username` | ✅ | ✅ | ✅ | ✅ |
| `email` | ✅ | ✅ | ✅ | ✅ |
| `first_name` | ✅ | ✅ | ✅ | ✅ |
| `last_name` | ✅ | ✅ | ✅ | ✅ |
| `identification` | ✅ | ✅ | ✅ | ✅ |
| `phone` | ✅ | ✅ | ✅ | ✅ |
| `role` | ✅ | ✅ | ❌ | ✅ |
| `role_display` | ✅ | ✅ | ❌ | ✅ |
| `is_verified` | ✅ | ✅ | ❌ | ✅ |

## 🎉 **Conclusión**

**✅ SÍ, los endpoints de usuarios devuelven `identification` y `role`**

- **Login y Registro:** Devuelven TODOS los campos incluyendo `identification` y `role`
- **Perfil:** Solo devuelve campos editables (incluye `identification` pero NO `role`)
- **Dashboard:** Devuelve información completa del usuario

**Para obtener `role` en el frontend, usar el endpoint de login o dashboard.**
