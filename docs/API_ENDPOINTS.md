# 📚 API Endpoints - Sistema de Monitoreo de Salas

## 🔐 **Autenticación y Usuarios**

### **Registro y Login**
```
POST /api/auth/register/          # Registro de nuevos usuarios
POST /api/auth/login/             # Login de usuarios
POST /api/auth/logout/            # Logout de usuarios
```

### **Perfil de Usuario**
```
GET  /api/auth/profile/           # Obtener perfil del usuario
PUT  /api/auth/profile/update/    # Actualizar perfil
POST /api/auth/change-password/   # Cambiar contraseña
```

### **Dashboard**
```
GET  /api/auth/dashboard/         # Dashboard básico del usuario
```

### **Administración (Solo Admins)**
```
GET  /api/auth/admin/users/                    # Lista de usuarios
PATCH /api/auth/admin/users/{id}/verify/       # Verificar usuario
DELETE /api/auth/admin/users/{id}/             # Eliminar usuario
```

### **Reset de Contraseña**
```
POST /api/auth/password/reset-request/        # Solicitar reset
GET  /api/auth/password/reset-confirm/         # Validar token
POST /api/auth/password/reset-confirm/        # Confirmar nueva contraseña
```

---

## 🏢 **Salas y Entradas**

### **Gestión de Salas**
```
GET  /api/rooms/                   # Lista todas las salas
GET  /api/rooms/{id}/              # Detalles de una sala
GET  /api/rooms/{id}/occupants/    # Ocupantes actuales de una sala
```

### **Registro de Entrada/Salida**
```
POST /api/rooms/entry/             # Crear nueva entrada
PATCH /api/rooms/entry/{id}/exit/  # Salir de una entrada específica
PATCH /api/rooms/my-active-entry/exit/  # Salir de entrada activa (sin ID)
```

### **Historial del Usuario**
```
GET  /api/rooms/my-entries/        # Historial de entradas del usuario
GET  /api/rooms/my-active-entry/   # Entrada activa del usuario
GET  /api/rooms/my-daily-summary/ # Resumen diario del usuario
```

---

## 🔔 **Notificaciones**

### **Gestión de Notificaciones**
```
GET  /api/notifications/                    # Lista de notificaciones
GET  /api/notifications/unread/             # Notificaciones no leídas
GET  /api/notifications/unread-count/       # Contador de no leídas
PATCH /api/notifications/{id}/mark-read/     # Marcar como leída
PATCH /api/notifications/mark-all-read/      # Marcar todas como leídas
GET  /api/notifications/summary/            # Resumen de notificaciones
```

### **Notificaciones de Exceso de Horas (Solo Admins)**
```
GET  /api/notifications/excessive-hours/           # Notificaciones de exceso
GET  /api/notifications/excessive-hours-summary/   # Resumen estadístico
POST /api/notifications/hours-exceeded/            # Verificar exceso manual
```

---

## 📊 **Dashboard y Mini Cards**

### **Dashboard Principal**
```
GET  /api/dashboard/              # Dashboard completo
GET  /api/dashboard/mini-cards/   # Solo mini cards
GET  /api/dashboard/stats/        # Solo estadísticas
GET  /api/dashboard/alerts/       # Solo alertas
GET  /api/dashboard/charts/       # Datos para gráficos
```

### **Dashboard Administrativo**
```
GET  /api/dashboard/admin/overview/  # Resumen administrativo
```

---

## 🔧 **Comandos de Administración**

### **Verificación de Exceso de Horas**
```bash
# Verificar y notificar exceso de horas
python manage.py check_excessive_hours

# Modo dry-run (sin enviar notificaciones)
python manage.py check_excessive_hours --dry-run

# Modo verbose (información detallada)
python manage.py check_excessive_hours --verbose
```

---

## 📝 **Ejemplos de Uso**

### **1. Registro de Usuario**
```json
POST /api/auth/register/
{
    "username": "juan_perez",
    "email": "juan@ejemplo.com",
    "password": "mi_password123",
    "password_confirm": "mi_password123",
    "first_name": "Juan",
    "last_name": "Pérez",
    "identification": "12345678",
    "phone": "3001234567",
    "role": "monitor"
}
```

### **2. Login**
```json
POST /api/auth/login/
{
    "username": "juan_perez",
    "password": "mi_password123"
}
```

### **3. Entrar a una Sala**
```json
POST /api/rooms/entry/
{
    "room": 1,
    "notes": "Entrada para monitoreo"
}
```

### **4. Salir de una Sala**
```json
PATCH /api/rooms/my-active-entry/exit/
{
    "notes": "Salida por descanso"
}
```

### **5. Obtener Dashboard**
```json
GET /api/dashboard/
Authorization: Token tu_token_aqui
```

---

## 🚨 **Sistema de Notificaciones Automáticas**

### **Tipos de Notificaciones**
- `room_entry`: Entrada a sala
- `room_exit`: Salida de sala
- `excessive_hours`: Exceso de 8 horas
- `admin_verification`: Verificación de usuario

### **Validaciones Automáticas**
- ✅ **Una entrada activa por usuario**: No se puede entrar a otra sala sin salir primero
- ✅ **Notificación de exceso de horas**: Automática cuando se exceden 8 horas
- ✅ **Verificación de administradores**: Los monitores requieren verificación
- ✅ **Validación de sesiones**: Control de entrada/salida con timestamps

---

## 🔒 **Autenticación**

### **Headers Requeridos**
```
Authorization: Token tu_token_aqui
Content-Type: application/json
```

### **Roles de Usuario**
- **Admin**: Acceso completo al sistema
- **Monitor**: Acceso limitado a sus propias funciones

### **Permisos**
- **IsVerifiedUser**: Usuario verificado
- **IsAdminUser**: Solo administradores
- **IsAuthenticated**: Usuario autenticado

---

## 📊 **Mini Cards del Dashboard**

### **Para Administradores**
- 👥 Total Usuarios
- 🏢 Monitores Activos
- ⏳ Pendientes Verificación
- ⏰ Horas Hoy

### **Para Monitores**
- 🏢 Estado Actual (En sala/Disponible)
- 📊 Sesiones Completadas
- ⏰ Horas (30 días)
- 🔔 Notificaciones

---

## 🎯 **Características Principales**

### **Sistema de Validación de 8 Horas**
- ✅ Detección automática de exceso
- ✅ Notificaciones a administradores
- ✅ Comando de verificación manual
- ✅ Alertas en tiempo real

### **Dashboard Inteligente**
- ✅ Mini cards dinámicas
- ✅ Estadísticas en tiempo real
- ✅ Gráficos de uso
- ✅ Alertas contextuales

### **Sistema de Notificaciones**
- ✅ Notificaciones automáticas
- ✅ Diferentes tipos de alertas
- ✅ Contador de no leídas
- ✅ Historial de notificaciones

---

## 🚀 **Configuración de Producción**

### **Variables de Entorno**
```env
EMAIL_HOST_USER=tu_email@gmail.com
EMAIL_HOST_PASSWORD=tu_password_app
DEFAULT_FROM_EMAIL=tu_email@gmail.com
PUBLIC_BASE_URL=http://tu-dominio.com
FRONTEND_BASE_URL=http://tu-frontend.com
```

### **Cron Job para Verificación Automática**
```bash
# Ejecutar cada hora
0 * * * * cd /path/to/project && python manage.py check_excessive_hours
```

---

¡El sistema está completamente configurado y listo para usar! 🎉
