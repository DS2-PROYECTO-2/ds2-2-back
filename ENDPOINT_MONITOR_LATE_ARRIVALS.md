# Endpoint para Monitores: Llegadas Tarde

## 📍 **Nuevo Endpoint Creado**

**`GET /api/rooms/monitor/late-arrivals/`**

### 🎯 **Propósito**
Permite que los monitores vean sus propias llegadas tarde de forma personalizada y segura.

## 🔐 **Permisos y Autenticación**

- **Autenticación:** Token Authentication requerida
- **Permisos:** Solo monitores (`@permission_classes([IsMonitorUser])`)
- **Seguridad:** Solo muestra datos del monitor actualmente logueado

## 📋 **Parámetros de Filtro**

| Parámetro | Tipo | Requerido | Descripción |
|-----------|------|-----------|-------------|
| `from_date` | string | No | Fecha de inicio (YYYY-MM-DD) |
| `to_date` | string | No | Fecha de fin (YYYY-MM-DD) |

## 📊 **Respuesta del Endpoint**

### **Estructura de Respuesta:**
```json
{
  "monitor_info": {
    "username": "monitor1",
    "full_name": "Juan Pérez",
    "email": "juan@ejemplo.com"
  },
  "late_arrivals_count": 2,
  "total_schedules": 10,
  "punctuality_percentage": 80.0,
  "late_details": [
    {
      "schedule_id": 123,
      "room_name": "Sala A",
      "scheduled_time": "08:00",
      "actual_time": "08:07",
      "delay_minutes": 7.0,
      "date": "2024-01-15",
      "notes": "Tráfico pesado"
    }
  ],
  "filters_applied": {
    "from_date": "2024-01-15",
    "to_date": "2024-01-15"
  }
}
```

### **Campos de Respuesta:**

#### **Información del Monitor:**
- `monitor_info`: Datos del monitor logueado
  - `username`: Nombre de usuario
  - `full_name`: Nombre completo
  - `email`: Correo electrónico

#### **Estadísticas:**
- `late_arrivals_count`: Número de llegadas tarde
- `total_schedules`: Total de turnos asignados
- `punctuality_percentage`: Porcentaje de puntualidad

#### **Detalles de Llegadas Tarde:**
- `late_details`: Array con detalles de cada llegada tarde
  - `schedule_id`: ID del turno
  - `room_name`: Nombre de la sala
  - `scheduled_time`: Hora programada (HH:MM)
  - `actual_time`: Hora real de llegada (HH:MM)
  - `delay_minutes`: Minutos de retraso
  - `date`: Fecha del turno (YYYY-MM-DD)
  - `notes`: Notas de la entrada

## 🔧 **Funcionalidades**

### **Cálculo de Llegadas Tarde:**
- Considera llegadas con más de **5 minutos de retraso**
- Usa zona horaria de **Bogotá** para cálculos precisos
- Busca entradas desde **10 minutos antes** del turno hasta final del día

### **Filtros de Fecha:**
- Soporte para rangos de fecha (`from_date` y `to_date`)
- Soporte para fecha única (`from_date` o `to_date`)
- Validación de formato de fecha (YYYY-MM-DD)

### **Estadísticas Adicionales:**
- **Porcentaje de puntualidad:** `((total_schedules - late_count) / total_schedules * 100)`
- **Total de turnos:** Número de turnos en el período filtrado

## 📝 **Ejemplos de Uso**

### **1. Obtener todas las llegadas tarde del monitor:**
```bash
GET /api/rooms/monitor/late-arrivals/
Authorization: Token YOUR_TOKEN
```

### **2. Filtrar por rango de fechas:**
```bash
GET /api/rooms/monitor/late-arrivals/?from_date=2024-01-15&to_date=2024-01-20
Authorization: Token YOUR_TOKEN
```

### **3. Filtrar desde una fecha específica:**
```bash
GET /api/rooms/monitor/late-arrivals/?from_date=2024-01-15
Authorization: Token YOUR_TOKEN
```

## ⚠️ **Manejo de Errores**

### **Error de Formato de Fecha:**
```json
{
  "error": "Formato de fecha inválido. Use YYYY-MM-DD"
}
```

### **Error del Servidor:**
```json
{
  "error": "Error al obtener llegadas tarde del monitor",
  "details": "Descripción del error"
}
```

## 🔒 **Seguridad**

- **Aislamiento de datos:** Solo muestra datos del monitor logueado
- **Validación de permisos:** Solo monitores pueden acceder
- **Autenticación requerida:** Token válido necesario

## 🎯 **Casos de Uso**

1. **Dashboard Personal:** Monitor ve su propio rendimiento
2. **Autoevaluación:** Revisar historial de puntualidad
3. **Mejora Personal:** Identificar patrones de llegadas tarde
4. **Reportes Personales:** Generar reportes individuales

## 📊 **Diferencias con Endpoints de Admin**

| Aspecto | Endpoint Monitor | Endpoint Admin |
|---------|------------------|----------------|
| **Datos** | Solo del monitor logueado | Todos los monitores |
| **Permisos** | `IsMonitorUser` | `IsAdminUser` |
| **Detalles** | Incluye información personal | Datos agregados |
| **Seguridad** | Aislamiento por usuario | Acceso completo |

## ✅ **Estado de Implementación**

- ✅ Endpoint creado: `get_monitor_late_arrivals()`
- ✅ URL configurada: `/api/rooms/monitor/late-arrivals/`
- ✅ Permisos configurados: Solo monitores
- ✅ Zona horaria corregida: Bogotá
- ✅ Filtros de fecha implementados
- ✅ Manejo de errores incluido
- ✅ Documentación completa
