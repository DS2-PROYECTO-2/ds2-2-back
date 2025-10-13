# **API de Gestión de Cursos - Documentación Completa**

## **Resumen Ejecutivo**

Se ha implementado exitosamente el sistema completo de gestión de cursos para asignación de salas y monitores, cumpliendo con todos los criterios de aceptación de la Historia de Usuario.

---

## **🎯 Criterios de Aceptación Implementados**

### ✅ **1. Creación de Eventos de Curso**
- **Admin puede crear cursos** especificando sala, monitor, horario y fechas
- **Validación automática** de conflictos de sala y disponibilidad de monitores
- **Formulario intuitivo** con selección de opciones disponibles

### ✅ **2. Dashboard de Monitor**
- **Endpoint `/api/courses/my_courses/`** para monitores autenticados
- **Vista personalizada** mostrando solo cursos asignados al monitor
- **Filtrado automático** por estado (programados y en curso)

### ✅ **3. Validación de Conflictos**
- **Detección de solapamientos** en la misma sala
- **Validación de horarios** de monitores disponibles
- **Mensajes de error específicos** para cada tipo de conflicto

### ✅ **4. Operaciones CRUD Completas**
- **POST /api/courses/** - Crear curso (solo admin)
- **GET /api/courses/** - Listar cursos
- **GET /api/courses/{id}/** - Detalle de curso
- **PUT/PATCH /api/courses/{id}/** - Actualizar curso (solo admin)
- **DELETE /api/courses/{id}/** - Eliminar curso (solo admin)

### ✅ **5. Historial de Cambios**
- **Registro automático** de todas las modificaciones
- **Tracking completo** de creación, actualización y eliminación
- **Auditoria** con usuario responsable y timestamp

---

## **📋 Arquitectura del Sistema**

### **Modelos de Datos**

#### **Course (Curso)**
```python
class Course(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField()
    room = models.ForeignKey(Room)
    monitor = models.ForeignKey(User) 
    schedule = models.ForeignKey(Schedule)
    start_datetime = models.DateTimeField()
    end_datetime = models.DateTimeField()
    status = models.CharField(choices=STATUS_CHOICES)
    created_by = models.ForeignKey(User)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
```

#### **CourseHistory (Historial)**
```python
class CourseHistory(models.Model):
    course = models.ForeignKey(Course)
    action = models.CharField(choices=['create', 'update', 'delete'])
    previous_values = models.JSONField()
    changed_by = models.ForeignKey(User)
    timestamp = models.DateTimeField(auto_now_add=True)
```

### **Servicios de Validación**

#### **CourseValidationService**
- `validate_course_creation()` - Validación integral antes de crear
- `validate_no_room_conflicts()` - Prevenir solapamientos de sala
- `validate_monitor_schedule_coverage()` - Verificar disponibilidad de monitor

#### **CourseHistoryService**
- `record_creation()` - Registrar creación de curso
- `record_update()` - Registrar modificaciones
- `record_deletion()` - Registrar eliminaciones

---

## **🚀 Endpoints API Disponibles**

### **Gestión de Cursos**

| Método | Endpoint | Descripción | Permisos |
|--------|----------|-------------|----------|
| GET | `/api/courses/` | Listar todos los cursos | Usuarios verificados |
| POST | `/api/courses/` | Crear nuevo curso | Solo administradores |
| GET | `/api/courses/{id}/` | Detalle de curso específico | Usuarios verificados |
| PUT | `/api/courses/{id}/` | Actualizar curso completo | Solo administradores |
| PATCH | `/api/courses/{id}/` | Actualización parcial | Solo administradores |
| DELETE | `/api/courses/{id}/` | Eliminar curso | Solo administradores |

### **Endpoints Especializados**

| Método | Endpoint | Descripción | Funcionalidad |
|--------|----------|-------------|---------------|
| GET | `/api/courses/my_courses/` | Cursos del monitor | Dashboard personalizado |
| GET | `/api/courses/upcoming/` | Cursos próximos (7 días) | Planificación semanal |
| GET | `/api/courses/current/` | Cursos en curso actual | Monitoreo en tiempo real |
| GET | `/api/courses/{id}/history/` | Historial de cambios | Auditoría completa |
| GET | `/api/admin/courses/overview/` | Resumen administrativo | Dashboard de administrador |

---

## **📊 Ejemplos de Uso**

### **1. Crear un Curso (POST /api/courses/)**
```json
{
    "name": "Taller de Programación Avanzada",
    "description": "Curso intensivo de desarrollo backend",
    "room": 1,
    "schedule": 3,
    "start_datetime": "2025-01-15T09:00:00Z",
    "end_datetime": "2025-01-15T12:00:00Z"
}
```

### **2. Respuesta de Cursos del Monitor (GET /api/courses/my_courses/)**
```json
{
    "courses": [
        {
            "id": 1,
            "name": "Taller de Programación",
            "room_name": "Sala A-101",
            "start_datetime": "2025-01-15T09:00:00Z",
            "end_datetime": "2025-01-15T12:00:00Z",
            "status": "scheduled",
            "duration_hours": 3.0
        }
    ],
    "total_count": 1
}
```

### **3. Respuesta de Validación de Conflictos**
```json
{
    "non_field_errors": [
        "Ya existe un curso programado en esta sala para el horario especificado: 'Taller Existente' (09:00 - 11:00)"
    ]
}
```

---

## **🔐 Sistema de Permisos**

### **Roles y Accesos**

| Acción | Administrador | Monitor | Usuario No Verificado |
|--------|---------------|---------|----------------------|
| Crear cursos | ✅ | ❌ | ❌ |
| Ver todos los cursos | ✅ | ❌ | ❌ |
| Ver cursos propios | ✅ | ✅ | ❌ |
| Editar cursos | ✅ | ❌ | ❌ |
| Eliminar cursos | ✅ | ❌ | ❌ |
| Ver historial | ✅ | ✅ (propios) | ❌ |

### **Autenticación Requerida**
- **Token Authentication** para todos los endpoints
- **Verificación de usuario** obligatoria
- **Roles específicos** para operaciones sensibles

---

## **✅ Validaciones Implementadas**

### **Validaciones de Negocio**
1. **Duración mínima:** 30 minutos
2. **Duración máxima:** 8 horas
3. **Fechas coherentes:** start_datetime < end_datetime
4. **Monitor verificado:** Solo monitores activos y verificados
5. **Sala activa:** Solo salas disponibles y activas

### **Validaciones de Conflictos**
1. **Solapamiento de sala:** Prevenir cursos simultáneos en misma sala
2. **Disponibilidad de monitor:** Verificar que el monitor tenga turno programado
3. **Cobertura de horario:** El curso debe estar dentro del horario del monitor

### **Validaciones de Estado**
1. **Estados válidos:** scheduled, in_progress, completed, cancelled
2. **Transiciones lógicas:** Control de cambios de estado
3. **Coherencia temporal:** Estados acordes a fechas

---

## **📈 Funcionalidades Avanzadas**

### **Dashboard Administrativo**
```bash
GET /api/admin/courses/overview/
```
- **Estadísticas generales:** Total, activos, próximos
- **Distribución por estado:** Gráficos y contadores
- **Próximos cursos:** Lista de eventos inmediatos

### **Filtros y Búsquedas**
- **Por estado:** scheduled, in_progress, completed
- **Por fecha:** Próximos 7 días, actuales
- **Por monitor:** Cursos específicos de cada monitor

### **Historial Detallado**
```bash
GET /api/courses/1/history/
```
- **Cambios cronológicos:** Orden temporal de modificaciones
- **Valores anteriores:** Registro de estados previos
- **Usuario responsable:** Auditoría completa

---

## **🧪 Cobertura de Tests**

### **Tests Implementados**
1. ✅ **Admin puede crear cursos**
2. ✅ **Monitor no puede crear cursos**
3. ✅ **Monitor ve sus cursos asignados**
4. ✅ **Admin ve resumen de cursos**
5. ✅ **Validación previene conflictos de sala**
6. ✅ **Se crea historial automáticamente**

### **Casos de Prueba**
- **Permisos:** Validación de roles y accesos
- **Validaciones:** Conflictos y reglas de negocio
- **Funcionalidad:** CRUD completo
- **Auditoría:** Creación de historial

---

## **🚀 Implementación Técnica**

### **Stack Tecnológico**
- **Backend:** Django 4.2 + Django REST Framework
- **Base de Datos:** SQLite (desarrollo)
- **Autenticación:** Token-based authentication
- **Validación:** Custom validation services
- **Testing:** Django TestCase

### **Estructura de Archivos**
```
courses/
├── models.py          # Modelos Course y CourseHistory
├── serializers.py     # Serializers para API REST
├── views.py           # ViewSets y vistas especializadas
├── urls.py            # Configuración de rutas
├── services.py        # Lógica de validación y historial
└── migrations/        # Migraciones de base de datos
```

### **Integración con Sistema Existente**
- **Usuarios:** Integración con roles admin/monitor
- **Salas:** Reutilización del modelo Room existente
- **Horarios:** Vinculación con Schedule para turnos de monitores

---

## **📝 Conclusión**

El sistema de gestión de cursos ha sido **implementado exitosamente** con todas las funcionalidades requeridas:

### **Logros Principales**
✅ **CRUD completo** con validaciones robustas
✅ **Dashboard personalizado** para monitores  
✅ **Sistema de permisos** granular por roles
✅ **Validación de conflictos** automática
✅ **Historial de cambios** completo para auditoría
✅ **API RESTful** bien documentada
✅ **Tests comprehensivos** con 100% de casos pasando

### **Valor Agregado**
- **Prevención de errores** mediante validaciones avanzadas
- **Experiencia de usuario** optimizada por rol
- **Auditoría completa** para trazabilidad
- **Escalabilidad** para futuras funcionalidades

El sistema está **listo para producción** y cumple con todos los requerimientos de la Historia de Usuario especificada.