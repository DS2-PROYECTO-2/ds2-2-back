# Registro Monitores UV - Backend

## Resumen del Commit

Este commit incluye la simplificación del proyecto y la creación de la estructura de modelos para el proyecto completo. Las principales acciones realizadas fueron:


### 2. Estructura de Modelos

Se han creado/modificado los siguientes modelos para cubrir la funcionalidad completa del proyecto:

#### Modelos Principales:

1. **User** (authentication/models.py)
   - Modelo personalizado de usuario con roles (admin/monitor)
   - Verificación de administradores

2. **Room** (rooms/models.py)
   - Información básica de salas (nombre, código, capacidad)

3. **RoomEntry** (rooms/models.py)
   - Registro de entrada/salida de monitores
   - Cálculo de horas trabajadas

4. **Equipment** (equipment/models.py)
   - Gestión de equipos en las salas
   - Estados de los equipos

5. **EquipmentReport** (equipment/models.py)
   - Reporte de problemas con equipos

6. **Attendance** (attendance/models.py)
   - Subida y gestión de listados de asistencia

7. **Incapacity** (attendance/models.py)
   - Gestión de incapacidades de monitores

8. **Notification** (notifications/models.py)
   - Sistema de notificaciones en tiempo real

9. **Schedule** (schedule/models.py)
   - Gestión de turnos y calendario

10. **Report** (reports/models.py)
    - Generación y exportación de reportes

### 3. Estructura Adicional

Para cada aplicación, se ha creado una estructura básica:

- **models.py**: Definición de modelos con relaciones
- **serializers.py**: Serializadores básicos para cada modelo
- **views.py**: Vistas API sin lógica implementada
- **urls.py**: Rutas de API básicas

Esta estructura proporciona una base sólida para:
- Crear diagramas ER y relacionales
- Visualizar la estructura completa del proyecto
- Implementar la lógica específica en fases posteriores

## Próximos Pasos

1. Implementar la lógica de negocio para el Sprint 1
2. Ejecutar migraciones para actualizar la base de datos
3. Configurar autenticación y permisos
4. Desarrollar el frontend básico
5. Implementar pruebas unitarias