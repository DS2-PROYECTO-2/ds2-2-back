# 📊 MODELO ENTIDAD-RELACIÓN - SISTEMA DS2

## 🎯 RESUMEN GENERAL
Este documento describe el modelo de datos completo del Sistema DS2 (Django + PostgreSQL) para gestión de salas, monitores y turnos.

---

## 🏗️ ENTIDADES Y ATRIBUTOS

### 1. **User** (users_user)
**Descripción:** Usuarios del sistema (administradores y monitores)

#### Atributos:
- **id** (PK) - AutoField - Clave primaria
- **username** - CharField(150) - ÚNICO - Nombre de usuario
- **email** - EmailField(254) - Correo electrónico  
- **first_name** - CharField(150) - Nombre(s)
- **last_name** - CharField(150) - Apellido(s)
- **password** - CharField(128) - Contraseña hasheada
- **identification** - CharField(20) - ÚNICO - Número de identificación
- **phone** - CharField(15) - OPCIONAL - Teléfono
- **role** - CharField(10) - Valores: 'admin', 'monitor' - DEFAULT: 'monitor'
- **is_verified** - BooleanField - DEFAULT: False - Si está verificado
- **verified_by** (FK) - ForeignKey(User) - NULL PERMITIDO - Admin que verificó
- **verification_date** - DateTimeField - NULL PERMITIDO - Fecha de verificación
- **is_active** - BooleanField - DEFAULT: True - Usuario activo
- **date_joined** - DateTimeField - Fecha de registro
- **created_at** - DateTimeField - Auto add
- **updated_at** - DateTimeField - Auto update

#### Restricciones:
- username ÚNICO
- email ÚNICO  
- identification ÚNICO

---

### 2. **ApprovalLink** (users_approval_link)
**Descripción:** Enlaces de aprobación/rechazo de usuarios con expiración

#### Atributos:
- **id** (PK) - AutoField - Clave primaria
- **user** (FK) - ForeignKey(User) - Usuario a aprobar/rechazar
- **action** - CharField(10) - Valores: 'approve', 'reject'
- **token_hash** - CharField(64) - ÚNICO - Hash del token
- **used_at** - DateTimeField - NULL PERMITIDO - Cuándo se usó
- **expires_at** - DateTimeField - Fecha de expiración
- **created_at** - DateTimeField - Auto add

#### Restricciones:
- token_hash ÚNICO

---

### 3. **PasswordReset** (users_password_reset)
**Descripción:** Tokens para restablecimiento de contraseñas

#### Atributos:
- **id** (PK) - AutoField - Clave primaria
- **user** (FK) - ForeignKey(User) - Usuario que solicita reset
- **token_hash** - CharField(64) - ÚNICO - Hash del token
- **used_at** - DateTimeField - NULL PERMITIDO - Cuándo se usó
- **expires_at** - DateTimeField - Fecha de expiración
- **created_at** - DateTimeField - Auto add

#### Restricciones:
- token_hash ÚNICO

---

### 4. **Room** (rooms_room)
**Descripción:** Salas físicas del sistema

#### Atributos:
- **id** (PK) - AutoField - Clave primaria
- **name** - CharField(100) - Nombre descriptivo
- **code** - CharField(10) - ÚNICO - Código identificador
- **capacity** - IntegerField - Capacidad máxima
- **description** - TextField - OPCIONAL - Descripción adicional
- **is_active** - BooleanField - DEFAULT: True - Sala activa
- **created_at** - DateTimeField - Auto add
- **updated_at** - DateTimeField - Auto update

#### Restricciones:
- code ÚNICO

---

### 5. **RoomEntry** (rooms_roomentry)
**Descripción:** Registros de entrada y salida de monitores en salas

#### Atributos:
- **id** (PK) - AutoField - Clave primaria
- **user** (FK) - ForeignKey(User) - Monitor que ingresa
- **room** (FK) - ForeignKey(Room) - Sala de entrada
- **entry_time** - DateTimeField - DEFAULT: now - Tiempo de entrada
- **exit_time** - DateTimeField - NULL PERMITIDO - Tiempo de salida
- **notes** - TextField - OPCIONAL - Notas adicionales
- **active** - BooleanField - DEFAULT: True - Registro activo
- **created_at** - DateTimeField - Auto add
- **updated_at** - DateTimeField - Auto update

---

### 6. **Schedule** (schedule_schedule)
**Descripción:** Turnos asignados a monitores en salas

#### Atributos:
- **id** (PK) - AutoField - Clave primaria
- **user** (FK) - ForeignKey(User) - Monitor asignado (role='monitor', is_verified=True)
- **room** (FK) - ForeignKey(Room) - Sala asignada
- **start_datetime** - DateTimeField - Inicio del turno
- **end_datetime** - DateTimeField - Fin del turno
- **status** - CharField(10) - Valores: 'active', 'completed', 'cancelled' - DEFAULT: 'active'
- **recurring** - BooleanField - DEFAULT: False - Si se repite semanalmente
- **notes** - TextField - OPCIONAL - Notas del turno
- **created_by** (FK) - ForeignKey(User) - NULL PERMITIDO - Admin creador (role='admin')
- **created_at** - DateTimeField - Auto add
- **updated_at** - DateTimeField - Auto update

#### Restricciones:
- CHECK: end_datetime > start_datetime

---

### 7. **Equipment** (equipment_equipment)
**Descripción:** Equipos físicos en las salas

#### Atributos:
- **id** (PK) - AutoField - Clave primaria
- **serial_number** - CharField(50) - ÚNICO - Número de serie
- **name** - CharField(100) - Nombre/modelo del equipo
- **description** - TextField - OPCIONAL - Descripción detallada
- **room** (FK) - ForeignKey(Room) - Sala donde está ubicado
- **status** - CharField(20) - Valores: 'operational', 'maintenance', 'out_of_service' - DEFAULT: 'operational'
- **acquisition_date** - DateField - Fecha de adquisición
- **created_at** - DateTimeField - Auto add
- **updated_at** - DateTimeField - Auto update

#### Restricciones:
- serial_number ÚNICO

---

### 8. **EquipmentReport** (equipment_equipmentreport)
**Descripción:** Reportes de problemas en equipos

#### Atributos:
- **id** (PK) - AutoField - Clave primaria
- **equipment** (FK) - ForeignKey(Equipment) - Equipo con problema
- **reported_by** (FK) - ForeignKey(User) - Usuario que reporta
- **issue_description** - TextField - Descripción del problema
- **issue_type** - CharField(100) - OPCIONAL - Tipo de falla
- **reported_date** - DateTimeField - Auto add - Fecha del reporte
- **resolved** - BooleanField - DEFAULT: False - Si está resuelto
- **resolved_date** - DateTimeField - NULL PERMITIDO - Fecha de resolución
- **resolution_notes** - TextField - OPCIONAL - Notas de resolución
- **created_at** - DateTimeField - Auto add
- **updated_at** - DateTimeField - Auto update

---

### 9. **Attendance** (attendance_attendance)
**Descripción:** Listados de asistencia subidos por monitores

#### Atributos:
- **id** (PK) - AutoField - Clave primaria
- **title** - CharField(200) - Título descriptivo
- **date** - DateField - Fecha del listado
- **uploaded_by** (FK) - ForeignKey(User) - Monitor que sube el archivo
- **file** - FileField - Archivo PDF/Excel subido (upload_to='attendances/')
- **description** - TextField - OPCIONAL - Descripción adicional
- **reviewed** - BooleanField - DEFAULT: False - Si fue revisado
- **reviewed_by** (FK) - ForeignKey(User) - NULL PERMITIDO - Admin que revisó
- **created_at** - DateTimeField - Auto add
- **updated_at** - DateTimeField - Auto update

---

### 10. **Incapacity** (attendance_incapacity)
**Descripción:** Incapacidades médicas de monitores

#### Atributos:
- **id** (PK) - AutoField - Clave primaria
- **user** (FK) - ForeignKey(User) - Monitor con incapacidad
- **start_date** - DateField - Fecha de inicio
- **end_date** - DateField - Fecha de fin
- **document** - FileField - Documento médico (upload_to='incapacities/')
- **description** - TextField - OPCIONAL - Descripción/motivo
- **approved** - BooleanField - DEFAULT: False - Si está aprobada
- **approved_by** (FK) - ForeignKey(User) - NULL PERMITIDO - Admin que aprobó
- **created_at** - DateTimeField - Auto add
- **updated_at** - DateTimeField - Auto update

---

### 11. **Course** (courses_course)
**Descripción:** Cursos programados en salas con monitores asignados

#### Atributos:
- **id** (PK) - AutoField - Clave primaria
- **name** - CharField(200) - Nombre del curso
- **description** - TextField - OPCIONAL - Descripción del curso
- **room** (FK) - ForeignKey(Room) - Sala donde se imparte
- **schedule** (FK) - ForeignKey(Schedule) - Turno asociado del monitor
- **start_datetime** - DateTimeField - Inicio del curso
- **end_datetime** - DateTimeField - Fin del curso
- **status** - CharField(15) - Valores: 'scheduled', 'in_progress', 'completed', 'cancelled' - DEFAULT: 'scheduled'
- **created_by** (FK) - ForeignKey(User) - NULL PERMITIDO - Admin creador (role='admin')
- **created_at** - DateTimeField - Auto add
- **updated_at** - DateTimeField - Auto update

---

### 12. **CourseHistory** (courses_coursehistory)
**Descripción:** Historial de cambios en cursos

#### Atributos:
- **id** (PK) - AutoField - Clave primaria
- **course** (FK) - ForeignKey(Course) - Curso modificado
- **action** - CharField(10) - Valores: 'create', 'update', 'delete'
- **changes** - JSONField - Detalles de cambios realizados
- **changed_by** (FK) - ForeignKey(User) - NULL PERMITIDO - Usuario que modificó
- **timestamp** - DateTimeField - Auto add - Momento del cambio

---

### 13. **Notification** (notifications_notification)
**Descripción:** Notificaciones del sistema para usuarios

#### Atributos:
- **id** (PK) - AutoField - Clave primaria
- **user** (FK) - ForeignKey(User) - Usuario destinatario
- **notification_type** - CharField(30) - Tipo de notificación
  - Valores: 'room_entry', 'room_exit', 'incapacity', 'equipment_report', 'attendance', 'admin_verification', 'excessive_hours', 'schedule_non_compliance', 'conversation_message'
- **title** - CharField(200) - Título de la notificación
- **message** - TextField - Mensaje detallado
- **related_object_id** - IntegerField - NULL PERMITIDO - ID del objeto relacionado
- **read** - BooleanField - DEFAULT: False - Si fue leída
- **read_timestamp** - DateTimeField - NULL PERMITIDO - Cuándo se leyó
- **created_at** - DateTimeField - Auto add
- **updated_at** - DateTimeField - Auto update

---

### 14. **Report** (reports_report)
**Descripción:** Reportes generados del sistema

#### Atributos:
- **id** (PK) - AutoField - Clave primaria
- **title** - CharField(200) - Título del reporte
- **report_type** - CharField(30) - Tipo de reporte
  - Valores: 'hours_summary', 'attendance', 'equipment_status', 'incapacity'
- **start_date** - DateField - Fecha inicial del período
- **end_date** - DateField - Fecha final del período
- **format** - CharField(10) - Valores: 'pdf', 'excel' - DEFAULT: 'pdf'
- **file** - FileField - NULL PERMITIDO - Archivo generado (upload_to='reports/')
- **created_by** (FK) - ForeignKey(User) - Usuario que generó
- **user_filter** (FK) - ForeignKey(User) - NULL PERMITIDO - Filtro por usuario específico
- **created_at** - DateTimeField - Auto add
- **updated_at** - DateTimeField - Auto update

---

### 15. **ExportJob** (export_exportjob)
**Descripción:** Trabajos de exportación de datos

#### Atributos:
- **id** (PK) - AutoField - Clave primaria
- **title** - CharField(200) - Título de la exportación
- **export_type** - CharField(30) - Tipo de exportación
  - Valores: 'monitors_data', 'attendance_data', 'schedule_data', 'room_entries_data'
- **format** - CharField(10) - Valores: 'pdf', 'excel'
- **status** - CharField(15) - Valores: 'pending', 'processing', 'completed', 'failed' - DEFAULT: 'pending'
- **start_date** - DateField - NULL PERMITIDO - Filtro fecha inicial
- **end_date** - DateField - NULL PERMITIDO - Filtro fecha final
- **monitor_ids** - JSONField - NULL PERMITIDO - Lista de IDs específicos
- **file** - FileField - NULL PERMITIDO - Archivo generado (upload_to='exports/')
- **requested_by** (FK) - ForeignKey(User) - Usuario que solicita
- **created_at** - DateTimeField - Auto add
- **updated_at** - DateTimeField - Auto update
- **completed_at** - DateTimeField - NULL PERMITIDO - Cuándo completó
- **error_message** - TextField - OPCIONAL - Mensaje si falló
- **file_size** - BigIntegerField - NULL PERMITIDO - Tamaño en bytes

---

## 🔗 RELACIONES Y CARDINALIDADES

### **RELACIONES 1:N (Uno a Muchos)**

1. **User → ApprovalLink**
   - Un usuario puede tener múltiples enlaces de aprobación
   - `User.approval_links` ← `ApprovalLink.user`

2. **User → PasswordReset**
   - Un usuario puede tener múltiples tokens de reset
   - `User.password_resets` ← `PasswordReset.user`

3. **User → User** (Auto-referencia)
   - Un admin puede verificar múltiples usuarios
   - `User.verified_users` ← `User.verified_by`

4. **Room → RoomEntry**
   - Una sala puede tener múltiples entradas
   - `Room.entries` ← `RoomEntry.room`

5. **User → RoomEntry**
   - Un monitor puede tener múltiples entradas
   - `User.room_entries` ← `RoomEntry.user`

6. **Room → Schedule**
   - Una sala puede tener múltiples turnos
   - `Room.schedules` ← `Schedule.room`

7. **User → Schedule**
   - Un monitor puede tener múltiples turnos
   - `User.schedules` ← `Schedule.user`

8. **User → Schedule** (created_by)
   - Un admin puede crear múltiples turnos
   - `User.created_schedules` ← `Schedule.created_by`

9. **Room → Equipment**
   - Una sala puede tener múltiples equipos
   - `Room.equipment` ← `Equipment.room`

10. **Equipment → EquipmentReport**
    - Un equipo puede tener múltiples reportes
    - `Equipment.reports` ← `EquipmentReport.equipment`

11. **User → EquipmentReport**
    - Un usuario puede reportar múltiples equipos
    - `User.equipment_reports` ← `EquipmentReport.reported_by`

12. **User → Attendance**
    - Un monitor puede subir múltiples listados
    - `User.uploaded_attendances` ← `Attendance.uploaded_by`

13. **User → Attendance** (reviewed_by)
    - Un admin puede revisar múltiples listados
    - `User.reviewed_attendances` ← `Attendance.reviewed_by`

14. **User → Incapacity**
    - Un monitor puede tener múltiples incapacidades
    - `User.incapacities` ← `Incapacity.user`

15. **User → Incapacity** (approved_by)
    - Un admin puede aprobar múltiples incapacidades
    - `User.approved_incapacities` ← `Incapacity.approved_by`

16. **Room → Course**
    - Una sala puede tener múltiples cursos
    - `Room.courses` ← `Course.room`

17. **Schedule → Course**
    - Un turno puede tener múltiples cursos asignados
    - `Schedule.course_assignments` ← `Course.schedule`

18. **User → Course** (created_by)
    - Un admin puede crear múltiples cursos
    - `User.created_courses` ← `Course.created_by`

19. **Course → CourseHistory**
    - Un curso puede tener múltiples entradas de historial
    - `Course.history` ← `CourseHistory.course`

20. **User → CourseHistory**
    - Un usuario puede modificar múltiples cursos
    - `User.course_histories` ← `CourseHistory.changed_by`

21. **User → Notification**
    - Un usuario puede recibir múltiples notificaciones
    - `User.notifications_received` ← `Notification.user`

22. **User → Report**
    - Un usuario puede generar múltiples reportes
    - `User.reports` ← `Report.created_by`

23. **User → Report** (user_filter)
    - Un usuario puede ser filtro de múltiples reportes
    - `User.filtered_reports` ← `Report.user_filter`

24. **User → ExportJob**
    - Un usuario puede solicitar múltiples exportaciones
    - `User.export_jobs` ← `ExportJob.requested_by`

---

## 🔑 CLAVES E ÍNDICES

### **CLAVES PRIMARIAS (PK)**
Todas las entidades tienen **id (AutoField)** como clave primaria.

### **CLAVES FORÁNEAS (FK)**
- **ApprovalLink.user** → User.id
- **PasswordReset.user** → User.id  
- **User.verified_by** → User.id (auto-referencia)
- **RoomEntry.user** → User.id
- **RoomEntry.room** → Room.id
- **Schedule.user** → User.id
- **Schedule.room** → Room.id
- **Schedule.created_by** → User.id
- **Equipment.room** → Room.id
- **EquipmentReport.equipment** → Equipment.id
- **EquipmentReport.reported_by** → User.id
- **Attendance.uploaded_by** → User.id
- **Attendance.reviewed_by** → User.id
- **Incapacity.user** → User.id
- **Incapacity.approved_by** → User.id
- **Course.room** → Room.id
- **Course.schedule** → Schedule.id
- **Course.created_by** → User.id
- **CourseHistory.course** → Course.id
- **CourseHistory.changed_by** → User.id
- **Notification.user** → User.id
- **Report.created_by** → User.id
- **Report.user_filter** → User.id
- **ExportJob.requested_by** → User.id

### **RESTRICCIONES ÚNICAS**
- **User**: username, email, identification
- **ApprovalLink**: token_hash
- **PasswordReset**: token_hash
- **Room**: code
- **Equipment**: serial_number

### **ÍNDICES COMPUESTOS**
- **ApprovalLink**: [token_hash], [user, action], [expires_at]
- **PasswordReset**: [token_hash], [user], [expires_at]
- **Course**: [start_datetime, end_datetime], [room, start_datetime], [schedule, start_datetime]

---

## 📋 RESTRICCIONES DE INTEGRIDAD

### **CHECK CONSTRAINTS**
1. **Schedule**: `end_datetime > start_datetime`
2. **User.role**: Valores permitidos: 'admin', 'monitor'
3. **Schedule.status**: Valores permitidos: 'active', 'completed', 'cancelled'
4. **Equipment.status**: Valores permitidos: 'operational', 'maintenance', 'out_of_service'
5. **Course.status**: Valores permitidos: 'scheduled', 'in_progress', 'completed', 'cancelled'

### **VALIDACIONES DE NEGOCIO**
1. **Schedule.user** debe tener role='monitor' y is_verified=True
2. **Schedule.created_by** debe tener role='admin'
3. **Course.created_by** debe tener role='admin'
4. Duración de Schedule no puede exceder 12 horas
5. Duración de Course no puede exceder 8 horas

---

## 🎯 PATRONES DE ACCESO PRINCIPALES

### **Por Usuario**
- Obtener turnos de un monitor: `Schedule.objects.filter(user=monitor)`
- Obtener entradas de sala: `RoomEntry.objects.filter(user=monitor)`
- Obtener notificaciones: `Notification.objects.filter(user=user)`

### **Por Sala**
- Obtener ocupantes actuales: `RoomEntry.objects.filter(room=sala, exit_time__isnull=True)`
- Obtener equipos: `Equipment.objects.filter(room=sala)`
- Obtener turnos: `Schedule.objects.filter(room=sala)`

### **Por Fecha**
- Turnos del día: `Schedule.objects.filter(start_datetime__date=fecha)`
- Cursos del período: `Course.objects.filter(start_datetime__range=[inicio, fin])`
- Reportes de período: `Report.objects.filter(start_date__lte=fecha, end_date__gte=fecha)`

---

## 📊 RESUMEN DE CARDINALIDADES

```
User (1) ←→ (N) ApprovalLink
User (1) ←→ (N) PasswordReset  
User (1) ←→ (N) User (auto-referencia)
Room (1) ←→ (N) RoomEntry
User (1) ←→ (N) RoomEntry
Room (1) ←→ (N) Schedule
User (1) ←→ (N) Schedule
Room (1) ←→ (N) Equipment
Equipment (1) ←→ (N) EquipmentReport
User (1) ←→ (N) EquipmentReport
User (1) ←→ (N) Attendance
User (1) ←→ (N) Incapacity
Room (1) ←→ (N) Course
Schedule (1) ←→ (N) Course
Course (1) ←→ (N) CourseHistory
User (1) ←→ (N) Notification
User (1) ←→ (N) Report
User (1) ←→ (N) ExportJob
```

**Total de Entidades:** 15
**Total de Relaciones:** 24
**Relaciones 1:N:** 24
**Relaciones N:N:** 0 (se usan tablas intermedias si es necesario)

---

*Este documento debe ser usado como referencia exacta para crear el diagrama entidad-relación del Sistema DS2.*