from django.utils import timezone
from datetime import datetime, timedelta
import pytz

BOGOTA_TZ = pytz.timezone('America/Bogota')

def calcular_diferencia(hora_turno, hora_registro):
    """
    Calcula diferencia en minutos entre turno y registro
    Convierte ambas fechas a zona horaria de Bogotá para cálculo correcto
    
    Diferencia positiva: llegó después del turno (TARDE o SOBRE_LA_HORA)
    Diferencia negativa: llegó antes del turno (A_TIEMPO)
    
    SOLO usa hora y minutos, ignora segundos
    """
    # Convertir a zona horaria de Bogotá si no lo están
    if hora_turno.tzinfo is None:
        hora_turno = BOGOTA_TZ.localize(hora_turno)
    else:
        hora_turno = hora_turno.astimezone(BOGOTA_TZ)
    
    if hora_registro.tzinfo is None:
        hora_registro = BOGOTA_TZ.localize(hora_registro)
    else:
        hora_registro = hora_registro.astimezone(BOGOTA_TZ)
    
    # Calcular diferencia solo en minutos (ignorar segundos)
    turno_minutos = hora_turno.hour * 60 + hora_turno.minute
    registro_minutos = hora_registro.hour * 60 + hora_registro.minute
    
    diferencia_minutos = registro_minutos - turno_minutos
    
    return diferencia_minutos

def clasificar_estado(diferencia_minutos):
    """
    Clasifica el estado según la diferencia
    Período de gracia: 5 minutos
    
    Lógica corregida:
    - A_TIEMPO: Llegó antes del turno o exactamente a tiempo (diferencia <= 0)
    - SOBRE_LA_HORA: Llegó tarde pero dentro del período de gracia (0 < diferencia <= 5)
    - TARDE: Llegó muy tarde, fuera del período de gracia (diferencia > 5)
    """
    if diferencia_minutos > 5:
        return 'TARDE'  # Llegó más de 5 minutos tarde
    elif diferencia_minutos > 0:
        return 'SOBRE_LA_HORA'  # Llegó tarde pero dentro del período de gracia
    else:
        return 'A_TIEMPO'  # Llegó antes del turno o exactamente a tiempo (diferencia <= 0)

def formatear_diferencia(diferencia_minutos):
    """
    Formatea la diferencia en minutos para mostrar correctamente
    - Diferencia 0: Sin símbolo negativo, texto normal
    - Diferencia positiva: Con símbolo +, texto normal
    - Diferencia negativa: Con símbolo -, texto normal
    """
    if diferencia_minutos == 0:
        return "0"  # Sin símbolo negativo
    elif diferencia_minutos > 0:
        return f"+{diferencia_minutos}"  # Con símbolo positivo
    else:
        return str(diferencia_minutos)  # Con símbolo negativo

def generar_comparacion_turnos_registros(date_from, date_to, user_id=None, room_id=None):
    """
    Genera comparación entre turnos asignados y registros reales
    """
    from .models import RoomEntry
    from schedule.models import Schedule
    
    # Convertir fechas
    try:
        from_date = datetime.fromisoformat(date_from.replace('Z', '+00:00'))
        to_date = datetime.fromisoformat(date_to.replace('Z', '+00:00'))
    except ValueError:
        return []
    
    # Obtener turnos en el rango de fechas
    turnos_queryset = Schedule.objects.filter(
        start_datetime__date__gte=from_date.date(),
        start_datetime__date__lte=to_date.date()
    ).select_related('user', 'room')
    
    if user_id:
        turnos_queryset = turnos_queryset.filter(user_id=user_id)
    if room_id:
        turnos_queryset = turnos_queryset.filter(room_id=room_id)
    
    turnos = list(turnos_queryset)
    
    # Obtener todos los registros en el rango de fechas
    registros_queryset = RoomEntry.objects.filter(
        entry_time__date__gte=from_date.date(),
        entry_time__date__lte=to_date.date()
    ).select_related('user', 'room')
    
    if user_id:
        registros_queryset = registros_queryset.filter(user_id=user_id)
    if room_id:
        registros_queryset = registros_queryset.filter(room_id=room_id)
    
    registros = list(registros_queryset)
    
    comparaciones = []
    
    for turno in turnos:
        # Buscar PRIMER registro correspondiente (el más temprano)
        # Incluir registros desde 10 minutos antes del turno hasta el final del día
        turno_start = turno.start_datetime
        turno_end = turno.start_datetime.replace(hour=23, minute=59, second=59, microsecond=999999)
        
        # Rango de búsqueda: 10 minutos antes del turno hasta el final del día
        rango_inicio = turno_start - timedelta(minutes=10)
        
        registros_del_dia = []
        for r in registros:
            if (r.user == turno.user and 
                r.room == turno.room and 
                r.entry_time.date() == turno.start_datetime.date() and
                rango_inicio <= r.entry_time <= turno_end):
                registros_del_dia.append(r)
        
        # Ordenar por hora de entrada (más temprano primero) y tomar el primero
        if registros_del_dia:
            registros_del_dia.sort(key=lambda x: x.entry_time)
            registro = registros_del_dia[0]  # PRIMER registro (más temprano)
        else:
            registro = None
        
        # Calcular diferencia y estado
        if registro:
            diferencia = calcular_diferencia(turno.start_datetime, registro.entry_time)
            estado = clasificar_estado(diferencia)
            diferencia_formateada = formatear_diferencia(diferencia)
            
            comparaciones.append({
                'usuario': turno.user.username,
                'turno': turno.start_datetime.strftime('%H:%M'),
                'registro': registro.entry_time.strftime('%H:%M'),
                'diferencia': int(diferencia),
                'diferencia_formateada': diferencia_formateada,
                'estado': estado,
                'notas': registro.notes or '',
                'sala': turno.room.name,
                'fecha': turno.start_datetime.strftime('%Y-%m-%d')
            })
        else:
            comparaciones.append({
                'usuario': turno.user.username,
                'turno': turno.start_datetime.strftime('%H:%M'),
                'registro': 'Sin registro',
                'diferencia': 0,
                'diferencia_formateada': '0',
                'estado': 'SIN_REGISTRO',
                'notas': '',
                'sala': turno.room.name,
                'fecha': turno.start_datetime.strftime('%Y-%m-%d')
            })
    
    return comparaciones

def validar_acceso_anticipado(user, room_id, access_time):
    """
    Valida si un usuario puede acceder anticipadamente a una sala
    """
    from schedule.models import Schedule
    
    # Buscar turnos del día actual
    turnos_del_dia = Schedule.objects.filter(
        user=user,
        room_id=room_id,
        status=Schedule.ACTIVE,
        start_datetime__date=access_time.date()
    )
    
    if not turnos_del_dia.exists():
        return False, f"El monitor {user.username} no tiene un turno asignado en la sala {room_id} para hoy."
    
    # Buscar turno activo en el momento exacto
    active_schedule = turnos_del_dia.filter(
        start_datetime__lte=access_time,
        end_datetime__gte=access_time
    ).first()
    
    # Si no hay turno activo, buscar turno futuro (para acceso anticipado)
    if not active_schedule:
        future_schedule = turnos_del_dia.filter(
            start_datetime__gt=access_time
        ).order_by('start_datetime').first()
        
        if future_schedule:
            # Verificar si el acceso anticipado está permitido (máximo 10 minutos antes)
            diferencia_minutos = (future_schedule.start_datetime - access_time).total_seconds() / 60
            
            if diferencia_minutos <= 10:
                return True, f"Acceso anticipado permitido. Turno inicia en {diferencia_minutos:.1f} minutos."
            else:
                return False, f"Acceso muy anticipado. El turno inicia en {diferencia_minutos:.1f} minutos. Máximo 10 minutos antes."
        else:
            return False, f"El monitor {user.username} no tiene un turno asignado en la sala {room_id} para el horario actual."
    
    return True, "Acceso permitido durante el turno activo."