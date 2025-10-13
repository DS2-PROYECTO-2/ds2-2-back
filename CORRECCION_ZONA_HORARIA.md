# Corrección de Zona Horaria - Bogotá

## Problemas Identificados

### ❌ **Problemas Críticos Encontrados:**

1. **En `rooms/views_reports.py` y `rooms/views_admin.py`:**
   - Se está convirtiendo fechas a UTC en lugar de Bogotá
   - Se está removiendo la zona horaria después de convertir
   - Esto causa inconsistencias en el manejo de fechas

2. **Código Problemático:**
   ```python
   # ❌ INCORRECTO - Convierte a UTC
   if from_date_obj.tzinfo is None:
       from_date_obj = from_date_obj.replace(tzinfo=timezone.utc)
   
   # ❌ INCORRECTO - Remueve zona horaria
   if start_datetime.tzinfo is not None:
       start_datetime = start_datetime.replace(tzinfo=None)
   ```

### ✅ **Configuración Correcta:**
- `settings.py`: `TIME_ZONE = 'America/Bogota'` ✅
- `settings.py`: `USE_TZ = True` ✅
- `rooms/utils.py`: Manejo correcto de zona horaria ✅

## Soluciones Implementadas

### 1. **Nuevo Archivo: `rooms/timezone_utils.py`**
```python
import pytz
from datetime import datetime
from django.utils import timezone

BOGOTA_TZ = pytz.timezone('America/Bogota')

def parse_date_to_bogota(date_string):
    """Parsea una fecha string y la convierte a zona horaria de Bogotá"""
    # Maneja diferentes formatos y convierte a Bogotá
    
def create_date_range_bogota(from_date_str, to_date_str=None):
    """Crea un rango de fechas en zona horaria de Bogotá"""
    # Retorna (start_datetime, end_datetime) en zona horaria de Bogotá
```

### 2. **Correcciones Necesarias en Views:**

#### **Antes (❌ Incorrecto):**
```python
if from_date_obj.tzinfo is None:
    from_date_obj = from_date_obj.replace(tzinfo=timezone.utc)
if to_date_obj.tzinfo is None:
    to_date_obj = to_date_obj.replace(tzinfo=timezone.utc)

# Remover zona horaria (PROBLEMÁTICO)
if start_datetime.tzinfo is not None:
    start_datetime = start_datetime.replace(tzinfo=None)
```

#### **Después (✅ Correcto):**
```python
# Usar las utilidades de zona horaria
start_datetime, end_datetime = create_date_range_bogota(from_date, to_date)
entries_queryset = entries_queryset.filter(
    entry_time__gte=start_datetime,
    entry_time__lte=end_datetime
)
```

## Archivos que Necesitan Corrección

### 1. **`rooms/views_reports.py`**
- Líneas 50-118: Filtros de fecha problemáticos
- Líneas 247-314: Más filtros de fecha problemáticos
- Líneas 430-500: Filtros adicionales problemáticos

### 2. **`rooms/views_admin.py`**
- Líneas 370-450: Filtros de fecha problemáticos
- Múltiples funciones con el mismo patrón problemático

## Impacto de las Correcciones

### ✅ **Beneficios:**
1. **Consistencia:** Todas las fechas se manejan en zona horaria de Bogotá
2. **Precisión:** Los cálculos de tiempo son correctos
3. **Mantenibilidad:** Código más limpio y reutilizable
4. **Confiabilidad:** Evita errores de interpretación de fechas

### 🔧 **Implementación:**
1. Usar `create_date_range_bogota()` para filtros de fecha
2. Usar `convert_to_bogota()` para conversiones individuales
3. Usar `format_datetime_bogota()` para mostrar fechas
4. Eliminar código que remueve zona horaria

## Estado Actual

- ✅ Configuración de Django correcta
- ✅ Utilidades de zona horaria creadas
- ⚠️ Views necesitan corrección manual
- ⚠️ Tests necesitan verificación

## Próximos Pasos

1. **Corregir `rooms/views_reports.py`** - Reemplazar código problemático
2. **Corregir `rooms/views_admin.py`** - Reemplazar código problemático  
3. **Verificar tests** - Asegurar que funcionen con zona horaria correcta
4. **Documentar cambios** - Actualizar documentación de API

## Comandos de Verificación

```bash
# Verificar configuración de zona horaria
python manage.py shell -c "from django.conf import settings; print(f'TIME_ZONE: {settings.TIME_ZONE}'); print(f'USE_TZ: {settings.USE_TZ}')"

# Verificar zona horaria actual
python manage.py shell -c "from django.utils import timezone; print(f'Now: {timezone.now()}')"
```
