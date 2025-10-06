# 🔐 ENDPOINTS DE AUTENTICACIÓN Y MANEJO DE ERRORES

## 📝 **1. REGISTRO DE USUARIOS**

### **Endpoint:**
```
POST /api/auth/register/
```

### **Datos de Entrada:**
```json
{
  "username": "usuario123",
  "email": "usuario@email.com",
  "password": "password123",
  "password_confirm": "password123",
  "first_name": "Juan",
  "last_name": "Pérez",
  "identification": "12345678",
  "phone": "3001234567",
  "role": "monitor"
}
```

### **Respuesta Exitosa (201):**
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

### **Errores Posibles (400):**

#### **1. Contraseñas no coinciden:**
```json
{
  "password_confirm": ["Las contraseñas no coinciden"]
}
```

#### **2. Identificación ya existe:**
```json
{
  "identification": ["Ya existe un usuario con esta identificación"]
}
```

#### **3. Username ya existe:**
```json
{
  "username": ["Ya existe un usuario con este nombre de usuario"]
}
```

#### **4. Email ya existe:**
```json
{
  "email": ["Ya existe un usuario con este email"]
}
```

#### **5. Campos requeridos faltantes:**
```json
{
  "first_name": ["Este campo es requerido"],
  "last_name": ["Este campo es requerido"],
  "identification": ["Este campo es requerido"],
  "email": ["Este campo es requerido"]
}
```

#### **6. Contraseña muy corta:**
```json
{
  "password": ["Asegúrese de que este valor tenga al menos 8 caracteres (tiene 6)."]
}
```

#### **7. Email inválido:**
```json
{
  "email": ["Ingrese una dirección de correo electrónico válida."]
}
```

---

## 🔑 **2. RESTABLECER CONTRASEÑA**

### **A. Solicitar Restablecimiento**

#### **Endpoint:**
```
POST /api/auth/password/reset-request/
```

#### **Datos de Entrada:**
```json
{
  "email": "usuario@email.com"
}
```

#### **Respuesta Exitosa (200):**
```json
{
  "message": "Si el email existe, recibirás un enlace de restablecimiento"
}
```

#### **Errores Posibles (400):**
```json
{
  "email": ["Ingrese una dirección de correo electrónico válida."]
}
```

### **B. Validar Token (GET)**

#### **Endpoint:**
```
GET /api/auth/password/reset-confirm/?token=abc123...
```

#### **Respuesta Exitosa (200):**
```json
{
  "valid": true,
  "user": {
    "id": 1,
    "username": "usuario123",
    "email": "usuario@email.com",
    "full_name": "Juan Pérez"
  }
}
```

#### **Errores Posibles (400):**

##### **Token no proporcionado:**
```json
{
  "error": "Token no proporcionado"
}
```

##### **Token expirado:**
```json
{
  "error": "Token expirado o ya usado"
}
```

##### **Token inválido:**
```json
{
  "error": "Token inválido"
}
```

### **C. Confirmar Nueva Contraseña (POST)**

#### **Endpoint:**
```
POST /api/auth/password/reset-confirm/
```

#### **Datos de Entrada:**
```json
{
  "token": "abc123...",
  "new_password": "nuevapassword123",
  "new_password_confirm": "nuevapassword123"
}
```

#### **Respuesta Exitosa (200):**
```json
{
  "message": "Contraseña actualizada correctamente"
}
```

#### **Errores Posibles (400):**

##### **Contraseñas no coinciden:**
```json
{
  "new_password_confirm": ["Las contraseñas no coinciden"]
}
```

##### **Token inválido:**
```json
{
  "token": ["Token inválido"]
}
```

##### **Token expirado:**
```json
{
  "token": ["Token expirado"]
}
```

##### **Token ya usado:**
```json
{
  "token": ["Token ya fue usado"]
}
```

##### **Contraseña igual a la actual:**
```json
{
  "new_password": ["La nueva contraseña debe ser diferente a la actual"]
}
```

##### **Contraseña muy corta:**
```json
{
  "new_password": ["Asegúrese de que este valor tenga al menos 8 caracteres."]
}
```

---

## 🔍 **3. MANEJO DE ERRORES GENERALES**

### **Códigos de Estado HTTP:**

#### **200 OK:**
- Operación exitosa
- Datos devueltos correctamente

#### **201 Created:**
- Recurso creado exitosamente
- Usuario registrado

#### **400 Bad Request:**
- Datos de entrada inválidos
- Errores de validación
- Token inválido/expirado

#### **401 Unauthorized:**
- Token de autenticación inválido
- Usuario no autenticado

#### **403 Forbidden:**
- Usuario autenticado pero sin permisos
- Acceso denegado

#### **404 Not Found:**
- Recurso no encontrado
- Endpoint no existe

#### **500 Internal Server Error:**
- Error interno del servidor
- Error de base de datos

### **Estructura de Errores:**

#### **Error de Validación:**
```json
{
  "field_name": ["Mensaje de error específico"]
}
```

#### **Error General:**
```json
{
  "error": "Descripción del error",
  "details": "Detalles adicionales (opcional)"
}
```

#### **Error con Múltiples Campos:**
```json
{
  "field1": ["Error en campo 1"],
  "field2": ["Error en campo 2"],
  "field3": ["Error en campo 3"]
}
```

---

## 🛡️ **4. VALIDACIONES DE SEGURIDAD**

### **Registro:**
- ✅ Contraseña mínimo 8 caracteres
- ✅ Contraseñas deben coincidir
- ✅ Email único en el sistema
- ✅ Username único en el sistema
- ✅ Identificación única en el sistema
- ✅ Email válido
- ✅ Campos requeridos

### **Restablecimiento de Contraseña:**
- ✅ Token válido y no expirado
- ✅ Token no usado previamente
- ✅ Nueva contraseña diferente a la actual
- ✅ Contraseña mínimo 8 caracteres
- ✅ Contraseñas deben coincidir
- ✅ Token expira en 2 horas

### **Seguridad:**
- ✅ No revela si un email existe (mismo mensaje para todos)
- ✅ Tokens hasheados en base de datos
- ✅ Tokens de un solo uso
- ✅ Expiración automática de tokens
- ✅ Limpieza automática de tokens expirados

---

## 📧 **5. FLUJO DE EMAIL**

### **Restablecimiento de Contraseña:**
1. Usuario solicita restablecimiento
2. Sistema genera token único
3. Token se hashea y guarda en BD
4. Email se envía con enlace
5. Usuario hace clic en enlace
6. Sistema valida token
7. Usuario ingresa nueva contraseña
8. Contraseña se actualiza
9. Token se marca como usado

### **Configuración de Email:**
- **Backend:** `django.core.mail.backends.console.EmailBackend` (desarrollo)
- **Host:** `smtp.gmail.com`
- **Puerto:** `587`
- **TLS:** `True`
- **Expiración:** 2 horas

---

## 🎯 **6. EJEMPLOS DE USO**

### **Registro Exitoso:**
```bash
curl -X POST http://localhost:8000/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "nuevousuario",
    "email": "nuevo@email.com",
    "password": "password123",
    "password_confirm": "password123",
    "first_name": "Juan",
    "last_name": "Pérez",
    "identification": "12345678",
    "phone": "3001234567",
    "role": "monitor"
  }'
```

### **Solicitar Restablecimiento:**
```bash
curl -X POST http://localhost:8000/api/auth/password/reset-request/ \
  -H "Content-Type: application/json" \
  -d '{"email": "usuario@email.com"}'
```

### **Confirmar Restablecimiento:**
```bash
curl -X POST http://localhost:8000/api/auth/password/reset-confirm/ \
  -H "Content-Type: application/json" \
  -d '{
    "token": "abc123...",
    "new_password": "nuevapassword123",
    "new_password_confirm": "nuevapassword123"
  }'
```

---

## ✅ **RESUMEN**

**Endpoints de Autenticación:**
- ✅ `POST /api/auth/register/` - Registro de usuarios
- ✅ `POST /api/auth/password/reset-request/` - Solicitar restablecimiento
- ✅ `GET /api/auth/password/reset-confirm/` - Validar token
- ✅ `POST /api/auth/password/reset-confirm/` - Confirmar nueva contraseña

**Manejo de Errores:**
- ✅ Validaciones detalladas por campo
- ✅ Mensajes de error específicos
- ✅ Códigos de estado HTTP apropiados
- ✅ Seguridad en manejo de tokens
- ✅ Limpieza automática de datos expirados
