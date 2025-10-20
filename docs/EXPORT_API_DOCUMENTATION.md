# API de Exportación de Datos de Monitores

## Descripción General

Sistema completo de exportación de datos de monitores en formatos PDF y Excel, con soporte para filtros por fechas y monitores específicos.

## Endpoints Disponibles

### 1. Exportar Datos de Monitores

**POST** `/api/export/monitors/export/`

Inicia un proceso de exportación de datos de monitores.

#### Parámetros del Body:
```json
{
    "export_type": "monitors_data",
    "format": "pdf",  // o "excel"
    "title": "Reporte de Monitores - Enero 2024",
    "monitor_ids": [1, 2, 3],  // opcional: IDs específicos
    "start_date": "2024-01-01",  // opcional: formato YYYY-MM-DD
    "end_date": "2024-01-31"     // opcional: formato YYYY-MM-DD
}
```

#### Respuesta:
```json
{
    "message": "Exportación iniciada",
    "export_job_id": 123,
    "status": "processing"
}
```

### 2. Obtener Datos de Monitores (JSON)

**GET** `/api/export/monitors/data/`

Obtiene los datos de monitores en formato JSON.

#### Parámetros de Query:
- `monitor_ids[]`: IDs específicos de monitores
- `start_date`: Fecha inicial (YYYY-MM-DD)
- `end_date`: Fecha final (YYYY-MM-DD)

#### Ejemplo:
```
GET /api/export/monitors/data/?monitor_ids[]=1&monitor_ids[]=2&start_date=2024-01-01&end_date=2024-01-31
```

#### Respuesta:
```json
{
    "monitors": [
        {
            "id": 1,
            "username": "monitor1",
            "email": "monitor1@example.com",
            "full_name": "Juan Pérez",
            "identification": "12345678",
            "phone": "3001234567",
            "role": "monitor",
            "is_verified": true,
            "total_hours_worked": 45.5,
            "total_room_entries": 12,
            "total_schedules": 8,
            "total_incapacities": 0
        }
    ],
    "total_count": 1,
    "filters_applied": {
        "monitor_ids": ["1", "2"],
        "start_date": "2024-01-01",
        "end_date": "2024-01-31"
    }
}
```

### 3. Obtener Datos de Entradas a Salas

**GET** `/api/export/room-entries/data/`

Obtiene los datos de entradas a salas.

#### Parámetros de Query:
- `monitor_ids[]`: IDs de monitores
- `room_ids[]`: IDs de salas
- `start_date`: Fecha inicial
- `end_date`: Fecha final

#### Respuesta:
```json
{
    "room_entries": [
        {
            "id": 1,
            "user_name": "Juan Pérez",
            "user_identification": "12345678",
            "room_name": "Sala A",
            "room_code": "SA001",
            "entry_time": "2024-01-15T08:00:00Z",
            "exit_time": "2024-01-15T16:00:00Z",
            "duration_hours": 8.0,
            "is_active_display": "No",
            "notes": "Turno matutino"
        }
    ],
    "total_count": 1
}
```

### 4. Obtener Datos de Turnos

**GET** `/api/export/schedules/data/`

Obtiene los datos de turnos asignados.

#### Parámetros de Query:
- `monitor_ids[]`: IDs de monitores
- `room_ids[]`: IDs de salas
- `status`: Estado del turno (active, completed, cancelled)
- `start_date`: Fecha inicial
- `end_date`: Fecha final

#### Respuesta:
```json
{
    "schedules": [
        {
            "id": 1,
            "user_name": "Juan Pérez",
            "room_name": "Sala A",
            "start_datetime": "2024-01-15T08:00:00Z",
            "end_datetime": "2024-01-15T16:00:00Z",
            "duration_hours": 8.0,
            "status": "completed",
            "recurring": false,
            "notes": "Turno regular"
        }
    ],
    "total_count": 1
}
```

### 5. Verificar Estado de Exportación

**GET** `/api/export/jobs/{export_job_id}/status/`

Verifica el estado de un trabajo de exportación.

#### Respuesta:
```json
{
    "id": 123,
    "title": "Reporte de Monitores - Enero 2024",
    "export_type": "monitors_data",
    "format": "pdf",
    "status": "completed",
    "file_url": "https://example.com/media/exports/monitors_export_20240115_143022.pdf",
    "file_size_mb": 2.5,
    "created_at": "2024-01-15T14:30:00Z",
    "completed_at": "2024-01-15T14:32:00Z"
}
```

### 6. Descargar Archivo de Exportación

**GET** `/api/export/jobs/{export_job_id}/download/`

Descarga el archivo generado.

#### Respuesta:
Archivo binario (PDF o Excel) con headers de descarga.

### 7. Listar Trabajos de Exportación

**GET** `/api/export/jobs/`

Lista todos los trabajos de exportación del usuario.

#### Respuesta:
```json
{
    "results": [
        {
            "id": 123,
            "title": "Reporte de Monitores - Enero 2024",
            "export_type": "monitors_data",
            "format": "pdf",
            "status": "completed",
            "file_url": "https://example.com/media/exports/monitors_export_20240115_143022.pdf",
            "created_at": "2024-01-15T14:30:00Z"
        }
    ],
    "count": 1
}
```

## Formatos de Exportación

### PDF
- **Contenido**: Información completa de monitores con estadísticas
- **Estructura**: 
  - Página de resumen con información general
  - Una página por monitor con:
    - Datos básicos
    - Estadísticas (horas trabajadas, entradas, turnos, incapacidades)
    - Historial de entradas a salas (últimas 10)
- **Tamaño**: Optimizado para impresión A4

### Excel
- **Contenido**: Datos estructurados en múltiples hojas
- **Estructura**:
  - **Hoja 1**: Resumen de monitores
  - **Hoja 2**: Detalle de entradas a salas
  - **Hoja 3**: Detalle de turnos
- **Formato**: Tablas con encabezados estilizados y colores

## Filtros Disponibles

### Por Monitores
- **Todos**: No especificar `monitor_ids`
- **Específicos**: Lista de IDs en `monitor_ids`

### Por Fechas
- **Sin límite**: No especificar fechas
- **Rango**: `start_date` y `end_date` en formato YYYY-MM-DD
- **Desde**: Solo `start_date`
- **Hasta**: Solo `end_date`

### Por Salas (en entradas y turnos)
- **Todas**: No especificar `room_ids`
- **Específicas**: Lista de IDs en `room_ids`

## Estados de Exportación

- **pending**: Trabajo creado, esperando procesamiento
- **processing**: Exportación en curso
- **completed**: Exportación completada exitosamente
- **failed**: Exportación falló (ver `error_message`)

## Autenticación

Todos los endpoints requieren autenticación:
```http
Authorization: Token tu_token_aqui
```

## Ejemplos de Uso

### 1. Exportar todos los monitores en PDF
```bash
curl -X POST "https://api.example.com/api/export/monitors/export/" \
  -H "Authorization: Token tu_token" \
  -H "Content-Type: application/json" \
  -d '{
    "format": "pdf",
    "title": "Reporte General de Monitores"
  }'
```

### 2. Exportar monitores específicos en Excel
```bash
curl -X POST "https://api.example.com/api/export/monitors/export/" \
  -H "Authorization: Token tu_token" \
  -H "Content-Type: application/json" \
  -d '{
    "format": "excel",
    "title": "Monitores Seleccionados",
    "monitor_ids": [1, 2, 3],
    "start_date": "2024-01-01",
    "end_date": "2024-01-31"
  }'
```

### 3. Verificar estado y descargar
```bash
# Verificar estado
curl -X GET "https://api.example.com/api/export/jobs/123/status/" \
  -H "Authorization: Token tu_token"

# Descargar archivo
curl -X GET "https://api.example.com/api/export/jobs/123/download/" \
  -H "Authorization: Token tu_token" \
  -o "reporte_monitores.pdf"
```

## Consideraciones Técnicas

### Rendimiento
- Las exportaciones se procesan en hilos separados
- Para grandes volúmenes de datos, el proceso puede tomar varios minutos
- Los archivos se almacenan temporalmente en el servidor

### Límites
- **PDF**: Máximo 1000 monitores por exportación
- **Excel**: Máximo 5000 registros por hoja
- **Tiempo**: Timeout de 30 minutos por exportación

### Almacenamiento
- Los archivos se almacenan en `media/exports/`
- Se recomienda limpiar archivos antiguos periódicamente
- Los archivos incluyen timestamp en el nombre para evitar conflictos

## Troubleshooting

### Error: "Formato no válido"
- Verificar que `format` sea "pdf" o "excel"

### Error: "Formato de fecha inválido"
- Usar formato YYYY-MM-DD para fechas
- Verificar que start_date <= end_date

### Error: "El archivo no está disponible"
- Verificar que la exportación esté completada
- Revisar el estado con `/status/`

### Error: "Error al iniciar exportación"
- Verificar permisos de escritura en media/exports/
- Revisar logs del servidor para detalles específicos

