"""
Utilidades para manejo correcto de zona horaria de Bogotá
"""
import pytz
from datetime import datetime
from django.utils import timezone

BOGOTA_TZ = pytz.timezone('America/Bogota')

def parse_date_to_bogota(date_string):
    """
    Parsea una fecha string y la convierte a zona horaria de Bogotá
    
    Args:
        date_string: String de fecha en formato ISO o YYYY-MM-DD
        
    Returns:
        datetime object en zona horaria de Bogotá
    """
    try:
        # Manejar diferentes formatos de fecha
        if 'T' in date_string:
            date_obj = datetime.fromisoformat(date_string.replace('Z', '+00:00'))
        else:
            date_obj = datetime.fromisoformat(date_string)
        
        # Convertir a zona horaria de Bogotá
        if date_obj.tzinfo is None:
            date_obj = BOGOTA_TZ.localize(date_obj)
        else:
            date_obj = date_obj.astimezone(BOGOTA_TZ)
        
        return date_obj
    except (ValueError, AttributeError) as e:
        raise ValueError(f"Error parsing date '{date_string}': {e}")

def get_bogota_now():
    """
    Obtiene la fecha y hora actual en zona horaria de Bogotá
    
    Returns:
        datetime object en zona horaria de Bogotá
    """
    return timezone.now().astimezone(BOGOTA_TZ)

def convert_to_bogota(dt):
    """
    Convierte un datetime a zona horaria de Bogotá
    
    Args:
        dt: datetime object (con o sin zona horaria)
        
    Returns:
        datetime object en zona horaria de Bogotá
    """
    if dt is None:
        return None
    
    if dt.tzinfo is None:
        return BOGOTA_TZ.localize(dt)
    else:
        return dt.astimezone(BOGOTA_TZ)

def create_date_range_bogota(from_date_str, to_date_str=None):
    """
    Crea un rango de fechas en zona horaria de Bogotá
    
    Args:
        from_date_str: String de fecha de inicio
        to_date_str: String de fecha de fin (opcional)
        
    Returns:
        tuple: (start_datetime, end_datetime) en zona horaria de Bogotá
    """
    from_date = parse_date_to_bogota(from_date_str)
    start_datetime = from_date.replace(hour=0, minute=0, second=0, microsecond=0)
    
    if to_date_str:
        to_date = parse_date_to_bogota(to_date_str)
        end_datetime = to_date.replace(hour=23, minute=59, second=59, microsecond=999999)
    else:
        end_datetime = from_date.replace(hour=23, minute=59, second=59, microsecond=999999)
    
    return start_datetime, end_datetime

def fix_date_parsing_in_views():
    """
    Función para corregir el parsing de fechas en las views
    Reemplaza el código problemático con manejo correcto de zona horaria
    """
    # Esta función se puede usar para reemplazar bloques de código problemático
    pass

def format_datetime_bogota(dt, format_str='%d/%m/%Y %H:%M'):
    """
    Formatea un datetime en zona horaria de Bogotá
    
    Args:
        dt: datetime object
        format_str: Formato de salida
        
    Returns:
        String formateado
    """
    if dt is None:
        return None
    
    bogota_dt = convert_to_bogota(dt)
    return bogota_dt.strftime(format_str)
