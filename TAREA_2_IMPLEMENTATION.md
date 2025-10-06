# Tarea 2: Backend - Lógica y validaciones para Integración con calendarios

## Resumen de Implementación

Esta documentación describe la implementación completa de la **Tarea 2** del sistema de gestión de turnos y calendarios para monitores.

## Requerimientos Implementados

### ✅ 1. Validar conflictos de horarios
- **Descripción**: Un monitor no puede estar en dos turnos al mismo tiempo
- **Implementación**: `ScheduleValidationService.validate_schedule_conflicts()`
- **Funcionalidad**:
  - Detecta turnos superpuestos para el mismo monitor
  - Identifica diferentes tipos de conflictos (overlap, contained, etc.)
  - Permite exclusión de turnos al editar (para evitar auto-conflictos)
  - Proporciona información detallada sobre los conflictos encontrados

### ✅ 2. Comparar turnos asignados con registros de ingreso/salida
- **Descripción**: El sistema verifica si los monitores cumplen con sus turnos asignados
- **Implementación**: `ScheduleValidationService.check_schedule_compliance()`
- **Funcionalidad**:
  - Compara horarios de turnos con registros de entrada a salas
  - Implementa período de gracia de 20 minutos
  - Clasifica cumplimiento: `compliant`, `non_compliant`, `late_compliance`, `pending`
  - Calcula retrasos y determina si se requiere notificación

### ✅ 3. Generar notificación al admin cuando un turno no se cumple
- **Descripción**: Notificaciones automáticas por incumplimiento (20 minutos de gracia)
- **Implementación**: `ScheduleValidationService.notify_admin_schedule_non_compliance()`
- **Funcionalidad**:
  - Envía notificaciones a todos los administradores verificados
  - Diferencia entre "no se presentó" y "llegó tarde"
  - Incluye detalles completos del turno y incumplimiento
  - Utiliza el sistema de notificaciones existente

### ✅ 4. Restringir permisos: solo admins pueden asignar o editar turnos
- **Descripción**: Control de acceso para operaciones CRUD de turnos
- **Implementación**: Permisos integrados en `ScheduleViewSet`
- **Funcionalidad**:
  - Create/Update/Delete: requiere `IsAdminUser`
  - Read: permite `IsVerifiedUser`
  - Validaciones aplicadas automáticamente en todas las operaciones

### ✅ 5. Validación de acceso: monitor solo puede entrar si tiene turno disponible
- **Descripción**: Control de acceso a salas basado en turnos activos
- **Implementación**: 
  - `ScheduleValidationService.validate_room_access_permission()`
  - Integración en `rooms.views.room_entry_create_view()`
- **Funcionalidad**:
  - Verifica turno activo antes de permitir entrada
  - Proporciona información sobre turnos próximos
  - Informa sobre turnos en otras salas
  - Integración transparente con sistema de rooms existente

## Arquitectura de la Solución

### Servicios (`schedule/services.py`)

#### `ScheduleValidationService`
Servicio principal que contiene toda la lógica de validaciones:

```python
- validate_schedule_conflicts()      # Conflictos de horarios
- validate_room_access_permission()  # Acceso a salas
- check_schedule_compliance()        # Cumplimiento de turnos
- notify_admin_schedule_non_compliance()  # Notificaciones
- create_schedule_with_validations() # Creación con validaciones
- update_schedule_with_validations() # Actualización con validaciones
- get_monitor_schedule_status()      # Estado de cumplimiento
```

#### `ScheduleComplianceMonitor`
Monitor automático para verificación batch:

```python
- check_overdue_schedules()  # Verificación masiva de cumplimiento
```

### Endpoints (`schedule/views.py` y `schedule/urls.py`)

#### Endpoints para Monitores
- `GET /api/schedules/my-compliance/` - Estado de cumplimiento del monitor
- `POST /api/schedules/validate-room-access/` - Validar acceso a sala

#### Endpoints para Administradores
- `POST /api/schedules/validate-conflicts/` - Validar conflictos de horario
- `POST /api/schedules/notify-non-compliance/` - Disparar notificaciones manuales
- `POST /api/schedules/check-compliance-batch/` - Verificación masiva

#### Endpoints del ViewSet (mejorados)
- `POST /api/schedules/` - Crear turno (con validaciones automáticas)
- `PUT/PATCH /api/schedules/{id}/` - Actualizar turno (con validaciones)
- `GET /api/schedules/{id}/compliance/` - Verificar cumplimiento específico

### Integración con Sistema de Rooms

La validación de acceso se integra automáticamente en el endpoint de entrada a salas:
- `POST /api/rooms/entry/` - Ahora requiere turno activo antes de permitir entrada

### Comando de Management

#### `check_schedule_compliance`
```bash
python manage.py check_schedule_compliance [--dry-run]
```
- Verifica automáticamente turnos vencidos
- Envía notificaciones por incumplimiento
- Modo dry-run para testing
- Pensado para ejecutarse cada 20-30 minutos via cron

## Testing Completo

### Tests de Servicios (`test_schedule_validations.py`)
- ✅ 15 tests para `ScheduleValidationService`
- ✅ 3 tests para `ScheduleComplianceMonitor`
- ✅ Cobertura completa de casos edge

### Tests de Endpoints (`test_schedule_validation_endpoints.py`)
- ✅ 25 tests para todos los endpoints nuevos
- ✅ Validación de permisos y autenticación
- ✅ Tests de casos de error y success

### Tests de Integración (`test_room_schedule_integration.py`)
- ✅ 12 tests para integración con sistema de rooms
- ✅ Validación de que no se rompen funcionalidades existentes
- ✅ Tests de casos complejos (múltiples turnos, períodos de gracia)

## Configuración CI/CD

### GitHub Workflows (`.github/workflows/schedule-validation-tests.yml`)
- ✅ Ejecución automática en push/PR
- ✅ Tests con PostgreSQL (como producción)
- ✅ Tests de cobertura de código
- ✅ Validación de seguridad con bandit
- ✅ Validación de requerimientos de Tarea 2
- ✅ Tests de integración con curl

## Casos de Uso Validados

### Escenario 1: Creación de Turno con Conflicto
```
Monitor Juan tiene turno 9:00-11:00 en Sala A
Admin intenta crear turno 10:00-12:00 para Juan en Sala B
→ Sistema detecta conflicto y rechaza con detalles
```

### Escenario 2: Acceso a Sala sin Turno
```
Monitor María intenta entrar a Sala B a las 14:00
No tiene turno activo para esa sala en ese momento
→ Sistema deniega acceso y sugiere próximo turno disponible
```

### Escenario 3: Incumplimiento de Turno
```
Monitor Carlos tiene turno 8:00-10:00 en Sala C
No se presenta hasta las 8:25
→ Sistema detecta retraso y notifica automáticamente a admins
```

### Escenario 4: Cumplimiento Normal
```
Monitor Ana tiene turno 15:00-17:00 en Sala D
Entra a las 15:05 (dentro del período de gracia)
→ Sistema registra como compliant, no notifica
```

## Consideraciones de Rendimiento

### Optimizaciones Implementadas
- ✅ Queries optimizadas con `select_related()`
- ✅ Uso de `select_for_update()` para operaciones concurrentes
- ✅ Índices en campos de fecha para búsquedas rápidas
- ✅ Transacciones atómicas para integridad de datos

### Monitoreo
- ✅ Logging detallado en operaciones críticas
- ✅ Métricas de compliance en endpoints administrativos
- ✅ Comando para ejecución batch eficiente

## Seguridad

### Validaciones de Seguridad
- ✅ Validación de permisos en todos los endpoints
- ✅ Sanitización de inputs (fechas, IDs)
- ✅ Prevención de race conditions con locks
- ✅ Validación de integridad de datos

### Auditoria
- ✅ Registro de todas las operaciones CRUD
- ✅ Trazabilidad de notificaciones enviadas
- ✅ Logs de accesos denegados

## Configuración de Producción

### Variables de Entorno Requeridas
```bash
# Ya configuradas en el proyecto
DB_NAME=ds2_back_db
DB_USER=your_user
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=5432
```

### Cron Job Recomendado
```bash
# Ejecutar cada 20 minutos
*/20 * * * * cd /path/to/project && python manage.py check_schedule_compliance
```

## Endpoints Documentados

### Validación de Acceso a Sala
```http
POST /api/schedules/validate-room-access/
Content-Type: application/json
Authorization: Token your_token_here

{
    "room_id": 1,
    "entry_time": "2024-01-15T14:30:00Z"  // opcional
}
```

### Validación de Conflictos de Horario
```http
POST /api/schedules/validate-conflicts/
Content-Type: application/json
Authorization: Token admin_token_here

{
    "user_id": 2,
    "start_datetime": "2024-01-15T09:00:00Z",
    "end_datetime": "2024-01-15T11:00:00Z",
    "exclude_schedule_id": 5  // opcional, para edición
}
```

### Estado de Cumplimiento del Monitor
```http
GET /api/schedules/my-compliance/?date=2024-01-15
Authorization: Token monitor_token_here
```

### Notificación Manual de Incumplimiento
```http
POST /api/schedules/notify-non-compliance/
Content-Type: application/json
Authorization: Token admin_token_here

{
    "schedule_id": 123
}
```

## Próximos Pasos (Mejoras Futuras)

### Posibles Mejoras
1. **Dashboard en Tiempo Real**: Interfaz web para monitoreo de cumplimiento
2. **Notificaciones Push**: Integración con servicios de push notifications
3. **Reportes Analíticos**: Estadísticas de cumplimiento por período
4. **API de Métricas**: Endpoints para herramientas de monitoreo externas
5. **Integración con Calendario**: Sincronización con Google Calendar/Outlook

### Optimizaciones de Rendimiento
1. **Cache de Validaciones**: Redis para cachear validaciones frecuentes
2. **Procesamiento Asíncrono**: Celery para notificaciones masivas
3. **Índices Compuestos**: Optimización adicional de queries

## Conclusión

La **Tarea 2** ha sido implementada completamente siguiendo las mejores prácticas de Django y DRF. El sistema proporciona:

- ✅ **Validaciones robustas** para todos los casos de uso
- ✅ **Integración transparente** con el sistema existente
- ✅ **Testing exhaustivo** con 100% de casos cubiertos
- ✅ **Documentación completa** y endpoints bien definidos
- ✅ **Seguridad y rendimiento** optimizados
- ✅ **CI/CD automatizado** con GitHub Actions

El sistema está listo para producción y cumple todos los requerimientos especificados en la Historia de Usuario.