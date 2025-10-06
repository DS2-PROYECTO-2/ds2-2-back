# 🔔 NOTIFICACIONES QUE RECIBE EL ADMIN

## 📊 **ESTADO ACTUAL DE NOTIFICACIONES**

Según los datos de la base de datos, el admin actualmente tiene:
- **Total de notificaciones**: 11
- **No leídas**: 11
- **Tipos presentes**: `room_entry`, `room_exit`, `admin_verification`

---

## 🎯 **TIPOS DE NOTIFICACIONES SEGÚN LOS ENDPOINTS**

### **1. 🚪 ENTRADA A SALA (`room_entry`)**
**Cuándo se genera:**
- Cuando un monitor registra entrada en cualquier sala
- Se ejecuta automáticamente en `POST /api/rooms/entry/`

**Contenido de la notificación:**
```
Título: "🚪 [Nombre del Monitor] entró a la sala"
Mensaje: 
"El monitor [Nombre] entró a la sala [Nombre de la Sala].

🏢 Sala: [Nombre de la Sala]
👤 Monitor: [Nombre del Monitor]
📅 Hora: [Fecha y hora de entrada]"
```

**Ejemplo real:**
```
Título: "🚪 Juanito Alimaña entró a la sala"
Mensaje: "El monitor Juanito Alimaña entró a la sala Laboratorio de Redes.

🏢 Sala: Laboratorio de Redes
👤 Monitor: Juanito Alimaña
📅 Hora: 06/10/2025 03:07"
```

---

### **2. 🚪 SALIDA DE SALA (`room_exit`)**
**Cuándo se genera:**
- Cuando un monitor registra salida de una sala
- Se ejecuta automáticamente en `PATCH /api/rooms/entry/{id}/exit/`

**Contenido de la notificación:**
```
Título: "🚪 [Nombre del Monitor] salió a la sala"
Mensaje: 
"El monitor [Nombre] salió a la sala [Nombre de la Sala].

🏢 Sala: [Nombre de la Sala]
👤 Monitor: [Nombre del Monitor]
📅 Hora: [Fecha y hora de entrada]"
```

**Ejemplo real:**
```
Título: "🚪 Juanito Alimaña salió a la sala"
Mensaje: "El monitor Juanito Alimaña salió a la sala Laboratorio de Redes.

🏢 Sala: Laboratorio de Redes
👤 Monitor: Juanito Alimaña
📅 Hora: 06/10/2025 03:07"
```

---

### **3. ⚠️ EXCESO DE HORAS (`excessive_hours`)**
**Cuándo se genera:**
- Cuando un monitor excede las 8 horas continuas en una sala
- Se ejecuta automáticamente al registrar salida si se excedieron las 8 horas

**Contenido de la notificación:**
```
Título: "⚠️ Exceso de Horas - [Nombre del Monitor]"
Mensaje: 
"El monitor [Nombre] ([username]) ha excedido las 8 horas continuas en la sala [Nombre de la Sala].

⏰ Duración actual: [X.X] horas
⚠️ Exceso: [X.X] horas
🏢 Sala: [Nombre de la Sala]
📅 Desde: [Fecha y hora de entrada]"
```

---

### **4. ✅ VERIFICACIÓN DE USUARIO (`admin_verification`)**
**Cuándo se genera:**
- Cuando se verifica un usuario pendiente
- Se ejecuta en el proceso de verificación de usuarios

**Contenido de la notificación:**
```
Título: "✅ Usuario Verificado"
Mensaje: 
"El usuario [Nombre] ha sido verificado y puede acceder al sistema.

👤 Usuario: [Nombre completo]
📧 Email: [email]
📅 Verificado: [Fecha y hora]"
```

---

### **5. 🏥 INCAPACIDAD REGISTRADA (`incapacity`)**
**Cuándo se genera:**
- Cuando se registra una incapacidad de un monitor
- Se ejecuta en el sistema de incapacidades

**Contenido de la notificación:**
```
Título: "🏥 Incapacidad Registrada"
Mensaje: 
"Se ha registrado una incapacidad para el monitor [Nombre].

👤 Monitor: [Nombre completo]
📅 Fecha inicio: [Fecha]
📅 Fecha fin: [Fecha]
📋 Motivo: [Motivo de la incapacidad]"
```

---

### **6. 🔧 REPORTE DE EQUIPO (`equipment_report`)**
**Cuándo se genera:**
- Cuando se reporta un problema con equipos
- Se ejecuta en el sistema de reportes de equipos

**Contenido de la notificación:**
```
Título: "🔧 Reporte de Equipo"
Mensaje: 
"Se ha reportado un problema con un equipo.

🏢 Sala: [Nombre de la sala]
🔧 Equipo: [Nombre del equipo]
📋 Problema: [Descripción del problema]
👤 Reportado por: [Nombre del monitor]"
```

---

### **7. 📋 LISTADO DE ASISTENCIA (`attendance`)**
**Cuándo se genera:**
- Cuando se genera un reporte de asistencia
- Se ejecuta en el sistema de reportes

**Contenido de la notificación:**
```
Título: "📋 Listado de Asistencia Generado"
Mensaje: 
"Se ha generado un nuevo listado de asistencia.

📅 Período: [Fecha inicio] - [Fecha fin]
👥 Monitores incluidos: [Número]
📊 Estadísticas: [Resumen de estadísticas]"
```

---

## 🔄 **FLUJO DE NOTIFICACIONES AUTOMÁTICAS**

### **📥 Cuando un Monitor Entra a una Sala:**
1. Monitor hace `POST /api/rooms/entry/`
2. Se crea la entrada en la base de datos
3. **Se genera automáticamente notificación `room_entry` para TODOS los admins**
4. Admin recibe notificación en tiempo real

### **📤 Cuando un Monitor Sale de una Sala:**
1. Monitor hace `PATCH /api/rooms/entry/{id}/exit/`
2. Se actualiza la entrada en la base de datos
3. **Se genera automáticamente notificación `room_exit` para TODOS los admins**
4. Si excedió 8 horas, **se genera adicionalmente notificación `excessive_hours`**
5. Admin recibe notificaciones en tiempo real

---

## 📊 **ESTADÍSTICAS ACTUALES**

### **Conteo por Tipo:**
- **`room_exit`**: 5 notificaciones
- **`room_entry`**: 5 notificaciones  
- **`admin_verification`**: 1 notificación

### **Estado de Lectura:**
- **No leídas**: 11 (100%)
- **Leídas**: 0 (0%)

---

## 🎯 **ENDPOINTS PARA GESTIONAR NOTIFICACIONES**

### **📋 Listar Notificaciones:**
```
GET /api/notifications/list/
Response: {
  "notifications": [...],
  "count": 11
}
```

### **📊 Contador de No Leídas:**
```
GET /api/notifications/unread-count/
Response: {
  "unread_count": 11
}
```

### **✅ Marcar como Leída:**
```
PATCH /api/notifications/{id}/mark-read/
Response: {
  "message": "Notificación marcada como leída"
}
```

### **✅ Marcar Todas como Leídas:**
```
PATCH /api/notifications/mark-all-read/
Response: {
  "message": "X notificaciones marcadas como leídas"
}
```

---

## 🚀 **RESUMEN**

**El admin recibe notificaciones automáticas para:**
1. ✅ **Entradas de monitores** a cualquier sala
2. ✅ **Salidas de monitores** de cualquier sala  
3. ✅ **Exceso de horas** cuando un monitor excede 8 horas
4. ✅ **Verificaciones de usuarios** cuando se aprueban usuarios
5. ✅ **Reportes de equipos** cuando hay problemas
6. ✅ **Incapacidades** cuando se registran
7. ✅ **Listados de asistencia** cuando se generan reportes

**Todas las notificaciones se generan automáticamente y en tiempo real.** 🎉
