# Guía para el Modelo Entidad-Relación (ER)

Este documento proporciona una guía detallada para la creación y comprensión del modelo Entidad-Relación (ER) del proyecto "Registro Monitores UV".

## Entidades Principales

### 1. User (Usuario)
- **Descripción**: Representa a los usuarios del sistema (administradores y monitores).
- **Atributos clave**:
  - `id` (PK): Identificador único del usuario
  - `username`: Nombre de usuario para login
  - `password`: Contraseña (almacenada como hash)
  - `email`: Correo electrónico
  - `first_name`: Nombre
  - `last_name`: Apellido
  - `role`: Rol del usuario (admin/monitor)
  - `identification`: Número de identificación
  - `phone`: Número de teléfono
  - `is_verified`: Estado de verificación
  - `is_active`: Estado activo/inactivo
  - `date_joined`: Fecha de registro
  - `created_at`: Fecha de creación
  - `updated_at`: Fecha de actualización

### 2. Room (Sala)
- **Descripción**: Representa las salas donde trabajan los monitores.
- **Atributos clave**:
  - `id` (PK): Identificador único de la sala
  - `code`: Código único de la sala
  - `name`: Nombre descriptivo
  - `capacity`: Capacidad máxima de personas
  - `description`: Descripción adicional
  - `is_active`: Estado de la sala
  - `created_at`: Fecha de creación
  - `updated_at`: Fecha de actualización

### 3. RoomEntry (Entrada a Sala)
- **Descripción**: Registra las entradas y salidas de monitores a las salas.
- **Atributos clave**:
  - `id` (PK): Identificador único del registro
  - `user_id` (FK): Monitor que ingresa
  - `room_id` (FK): Sala a la que ingresa
  - `entry_time`: Fecha/hora de entrada
  - `exit_time`: Fecha/hora de salida
  - `notes`: Notas o comentarios sobre la entrada/salida
  - `created_at`: Fecha de creación
  - `updated_at`: Fecha de actualización
  - `duration_hours` (derivado): Duración de la permanencia en horas

### 4. Equipment (Equipo)
- **Descripción**: Equipos disponibles en las salas.
- **Atributos clave**:
  - `id` (PK): Identificador único del equipo
  - `serial_number`: Número de serie único
  - `name`: Nombre/modelo del equipo
  - `description`: Descripción detallada
  - `room_id` (FK): Sala donde se encuentra
  - `status`: Estado del equipo (operativo, mantenimiento, fuera de servicio)
  - `acquisition_date`: Fecha de adquisición
  - `created_at`: Fecha de creación
  - `updated_at`: Fecha de actualización

### 5. EquipmentReport (Reporte de Equipo)
- **Descripción**: Reportes de problemas con equipos.
- **Atributos clave**:
  - `id` (PK): Identificador único del reporte
  - `equipment_id` (FK): Equipo reportado
  - `reported_by` (FK): Usuario que reporta
  - `issue_description`: Descripción del problema
  - `reported_date`: Fecha/hora del reporte
  - `resolved`: Estado de resolución
  - `resolved_date`: Fecha/hora de resolución
  - `resolution_notes`: Notas sobre la resolución
  - `created_at`: Fecha de creación
  - `updated_at`: Fecha de actualización

### 6. Attendance (Asistencia)
- **Descripción**: Listados de asistencia subidos al sistema.
- **Atributos clave**:
  - `id` (PK): Identificador único del listado
  - `title`: Título descriptivo
  - `date`: Fecha del listado
  - `uploaded_by` (FK): Usuario que subió el listado
  - `file`: Archivo con el listado de asistencia
  - `description`: Descripción adicional
  - `reviewed`: Estado de revisión
  - `reviewed_by` (FK): Administrador que revisó el listado
  - `created_at`: Fecha de creación
  - `updated_at`: Fecha de actualización

### 7. Incapacity (Incapacidad)
- **Descripción**: Registros de incapacidades de monitores.
- **Atributos clave**:
  - `id` (PK): Identificador único de la incapacidad
  - `user_id` (FK): Monitor con incapacidad
  - `start_date`: Fecha de inicio
  - `end_date`: Fecha de finalización
  - `document`: Documento que certifica la incapacidad
  - `description`: Descripción o motivo
  - `approved`: Estado de aprobación
  - `approved_by` (FK): Administrador que aprobó la incapacidad
  - `created_at`: Fecha de creación
  - `updated_at`: Fecha de actualización
  - `duration_days` (derivado): Duración en días

### 8. Notification (Notificación)
- **Descripción**: Notificaciones en tiempo real.
- **Atributos clave**:
  - `id` (PK): Identificador único de la notificación
  - `user_id` (FK): Usuario que recibe la notificación
  - `notification_type`: Tipo de notificación
  - `title`: Título de la notificación
  - `message`: Mensaje detallado
  - `related_object_id`: ID del objeto relacionado
  - `read`: Estado de lectura
  - `read_timestamp`: Fecha/hora de lectura
  - `created_at`: Fecha de creación
  - `updated_at`: Fecha de actualización

### 9. Schedule (Turno)
- **Descripción**: Programación de turnos de monitores.
- **Atributos clave**:
  - `id` (PK): Identificador único del turno
  - `user_id` (FK): Monitor asignado
  - `room_id` (FK): Sala asignada
  - `start_datetime`: Inicio del turno
  - `end_datetime`: Fin del turno
  - `recurring`: Indica si es recurrente
  - `notes`: Notas adicionales
  - `created_by` (FK): Administrador que creó el turno
  - `created_at`: Fecha de creación
  - `updated_at`: Fecha de actualización
  - `duration_hours` (derivado): Duración en horas

### 10. Report (Reporte)
- **Descripción**: Reportes generados por el sistema.
- **Atributos clave**:
  - `id` (PK): Identificador único del reporte
  - `title`: Título descriptivo
  - `report_type`: Tipo de reporte (horas, asistencia, equipos, incapacidades)
  - `start_date`: Fecha inicial del período
  - `end_date`: Fecha final del período
  - `format`: Formato de exportación (PDF, Excel)
  - `file`: Archivo del reporte generado
  - `created_by` (FK): Usuario que generó el reporte
  - `user_filter` (FK): Filtro por usuario específico
  - `created_at`: Fecha de creación
  - `updated_at`: Fecha de actualización

## Relaciones entre Entidades

### 1. User - RoomEntry
- **Tipo**: Uno a Muchos (1:N)
- **Descripción**: Un usuario (monitor) puede tener múltiples registros de entrada, pero cada registro pertenece a un único usuario.
- **Cardinalidad**: Un usuario tiene 0 o muchos registros de entrada. Cada registro de entrada pertenece exactamente a 1 usuario.

### 2. Room - RoomEntry
- **Tipo**: Uno a Muchos (1:N)
- **Descripción**: Una sala puede tener múltiples registros de entrada, pero cada registro corresponde a una única sala.
- **Cardinalidad**: Una sala tiene 0 o muchos registros de entrada. Cada registro de entrada pertenece exactamente a 1 sala.

### 3. Room - Equipment
- **Tipo**: Uno a Muchos (1:N)
- **Descripción**: Una sala puede tener múltiples equipos, pero cada equipo está en una única sala.
- **Cardinalidad**: Una sala tiene 0 o muchos equipos. Cada equipo pertenece exactamente a 1 sala.

### 4. Equipment - EquipmentReport
- **Tipo**: Uno a Muchos (1:N)
- **Descripción**: Un equipo puede tener múltiples reportes de problemas, pero cada reporte corresponde a un único equipo.
- **Cardinalidad**: Un equipo tiene 0 o muchos reportes. Cada reporte pertenece exactamente a 1 equipo.

### 5. User - EquipmentReport
- **Tipo**: Uno a Muchos (1:N)
- **Descripción**: Un usuario puede crear múltiples reportes de equipos, pero cada reporte es creado por un único usuario.
- **Cardinalidad**: Un usuario tiene 0 o muchos reportes creados. Cada reporte es creado exactamente por 1 usuario.

### 6. User - Incapacity
- **Tipo**: Uno a Muchos (1:N)
- **Descripción**: Un usuario (monitor) puede tener múltiples incapacidades, pero cada incapacidad pertenece a un único usuario.
- **Cardinalidad**: Un usuario tiene 0 o muchas incapacidades. Cada incapacidad pertenece exactamente a 1 usuario.

### 7. User - Notification
- **Tipo**: Uno a Muchos (1:N)
- **Descripción**: Un usuario puede recibir múltiples notificaciones, pero cada notificación está dirigida a un único usuario.
- **Cardinalidad**: Un usuario tiene 0 o muchas notificaciones. Cada notificación pertenece exactamente a 1 usuario.

### 8. User - Schedule
- **Tipo**: Uno a Muchos (1:N)
- **Descripción**: Un usuario (monitor) puede tener múltiples turnos programados, pero cada turno es asignado a un único usuario.
- **Cardinalidad**: Un usuario tiene 0 o muchos turnos. Cada turno es asignado exactamente a 1 usuario.

### 10. User - Attendance
- **Tipo**: Uno a Muchos (1:N)
- **Descripción**: Un usuario puede subir múltiples listados de asistencia, pero cada listado es subido por un único usuario.
- **Cardinalidad**: Un usuario tiene 0 o muchos listados subidos. Cada listado es subido por exactamente 1 usuario.

### 11. User - Report
- **Tipo**: Uno a Muchos (1:N)
- **Descripción**: Un usuario puede generar múltiples reportes, pero cada reporte es generado por un único usuario.
- **Cardinalidad**: Un usuario tiene 0 o muchos reportes generados. Cada reporte es generado por exactamente 1 usuario.

## Consideraciones para el Diagrama ER

### Llaves

- **Llaves Primarias (PK)**: Cada entidad tiene un identificador único `id` que sirve como llave primaria.
- **Llaves Foráneas (FK)**: Establecen las relaciones entre entidades (por ejemplo, `user_id` en RoomEntry).

### Atributos

- **Atributos Simples**: Valores únicos como `name`, `code`, etc.
- **Atributos Derivados**: Valores calculados como `duration_hours` en RoomEntry.
- **Atributos Multivaluados**: No se utilizan en este modelo.

### Restricciones

- **Integridad Referencial**: Las llaves foráneas deben corresponder a valores existentes en la tabla referenciada.
- **Restricciones de Dominio**: Valores permitidos para campos como `role` en User.
- **Restricciones de Negocio**: Por ejemplo, un monitor no puede estar en dos salas al mismo tiempo.

## Herramientas Recomendadas para Crear el Diagrama ER

1. **Draw.io**: Herramienta gratuita basada en web.
2. **Lucidchart**: Ofrece plantillas específicas para diagramas ER.
3. **ERDPlus**: Especializada en diagramas ER con generación de SQL.
4. **MySQL Workbench**: Para diseño directo en bases de datos MySQL.
5. **DBeaver**: Editor de bases de datos universal con herramientas de diseño.

## Pasos para Crear el Diagrama ER

1. **Identificar Entidades**: Usar los modelos definidos en Django.
2. **Definir Atributos**: Incluir todos los campos relevantes.
3. **Establecer Relaciones**: Definir cómo se conectan las entidades.
4. **Asignar Cardinalidades**: Especificar la cantidad de instancias en cada relación.
5. **Revisar Integridad**: Verificar que todas las relaciones sean coherentes.
6. **Normalizar**: Aplicar formas normales para optimizar el diseño.

## Ejemplo de Notación (Chen)

```
[User] ---- 1 ---- < tiene > ---- N ---- [RoomEntry]
[Room] ---- 1 ---- < contiene > ---- N ---- [Equipment]
```

Este documento debe servir como guía para crear un modelo ER completo y coherente que represente adecuadamente la estructura de datos del proyecto "Registro Monitores UV".