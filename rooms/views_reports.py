from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.authentication import TokenAuthentication
from rest_framework.response import Response
from django.db.models import Q
from users.permissions import IsAdminUser
from .models import RoomEntry
from schedule.models import Schedule
from django.utils import timezone
from datetime import datetime, timedelta
import logging
from .serializers import RoomEntrySerializer, TurnComparisonSerializer, EntryValidationSerializer
from .timezone_utils import parse_date_to_bogota, create_date_range_bogota, convert_to_bogota
from .utils import generar_comparacion_turnos_registros, validar_acceso_anticipado
from users.permissions import IsMonitorUser


logger = logging.getLogger(__name__)

def get_time_overlap(entry_start, entry_end, schedule_start, schedule_end):
    """
    Calcula la superposición en horas entre dos intervalos de tiempo
    """
    overlap_start = max(entry_start, schedule_start)
    overlap_end = min(entry_end, schedule_end)
    
    if overlap_start >= overlap_end:
        return 0.0
    
    overlap_seconds = (overlap_end - overlap_start).total_seconds()
    return overlap_seconds / 3600.0

@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAdminUser])
def calculate_worked_hours(request):
    """
    Endpoint para calcular horas trabajadas con superposición temporal
    """
    try:
        # Obtener parámetros de filtro
        from_date = request.GET.get('from_date', '').strip()
        to_date = request.GET.get('to_date', '').strip()
        user_id = request.GET.get('user_id', '').strip()
        room_id = request.GET.get('room_id', '').strip()
        
        # Obtener todas las entradas
        entries_queryset = RoomEntry.objects.select_related('user', 'room').all()
        
        # Aplicar filtros de fecha
        if from_date and to_date:
            try:
                from datetime import datetime, timezone
                if 'T' in from_date:
                    from_date_obj = datetime.fromisoformat(from_date.replace('Z', '+00:00'))
                else:
                    from_date_obj = datetime.fromisoformat(from_date)
                
                if 'T' in to_date:
                    to_date_obj = datetime.fromisoformat(to_date.replace('Z', '+00:00'))
                else:
                    to_date_obj = datetime.fromisoformat(to_date)
                
                if from_date_obj.tzinfo is None:
                    from_date_obj = from_date_obj.replace(tzinfo=timezone.utc)
                if to_date_obj.tzinfo is None:
                    to_date_obj = to_date_obj.replace(tzinfo=timezone.utc)
                
                start_datetime = from_date_obj.replace(hour=0, minute=0, second=0, microsecond=0)
                end_datetime = to_date_obj.replace(hour=23, minute=59, second=59, microsecond=999999)
                
                if start_datetime.tzinfo is not None:
                    start_datetime = start_datetime.replace(tzinfo=None)
                if end_datetime.tzinfo is not None:
                    end_datetime = end_datetime.replace(tzinfo=None)
                
                entries_queryset = entries_queryset.filter(
                    entry_time__gte=start_datetime,
                    entry_time__lte=end_datetime
                )
            except ValueError as e:
                logger.warning(f"Error parsing date range: {e}")
                pass
        elif from_date:
            try:
                from datetime import datetime, timezone
                if 'T' in from_date:
                    from_date_obj = datetime.fromisoformat(from_date.replace('Z', '+00:00'))
                else:
                    from_date_obj = datetime.fromisoformat(from_date)
                
                if from_date_obj.tzinfo is None:
                    from_date_obj = from_date_obj.replace(tzinfo=timezone.utc)
                
                start_datetime = from_date_obj.replace(hour=0, minute=0, second=0, microsecond=0)
                if start_datetime.tzinfo is not None:
                    start_datetime = start_datetime.replace(tzinfo=None)
                entries_queryset = entries_queryset.filter(entry_time__gte=start_datetime)
            except ValueError as e:
                logger.warning(f"Error parsing from_date: {e}")
                pass
        elif to_date:
            try:
                from datetime import datetime, timezone
                if 'T' in to_date:
                    to_date_obj = datetime.fromisoformat(to_date.replace('Z', '+00:00'))
                else:
                    to_date_obj = datetime.fromisoformat(to_date)
                
                if to_date_obj.tzinfo is None:
                    to_date_obj = to_date_obj.replace(tzinfo=timezone.utc)
                
                end_datetime = to_date_obj.replace(hour=23, minute=59, second=59, microsecond=999999)
                if end_datetime.tzinfo is not None:
                    end_datetime = end_datetime.replace(tzinfo=None)
                entries_queryset = entries_queryset.filter(entry_time__lte=end_datetime)
            except ValueError as e:
                logger.warning(f"Error parsing to_date: {e}")
                pass
        
        # Aplicar filtros adicionales
        if user_id:
            try:
                user_id_int = int(user_id)
                entries_queryset = entries_queryset.filter(user_id=user_id_int)
            except ValueError:
                pass
        
        if room_id:
            try:
                room_id_int = int(room_id)
                entries_queryset = entries_queryset.filter(room_id=room_id_int)
            except ValueError:
                pass
        
        # Obtener todas las entradas filtradas
        entries = list(entries_queryset)
        
        # Obtener todos los turnos
        schedules = list(Schedule.objects.select_related('user', 'room').all())
        
        # Calcular horas trabajadas con superposición
        total_worked_hours = 0.0
        user_hours = {}
        schedule_hours = {}
        overlaps_found = []
        
        for entry in entries:
            # Solo procesar entradas completas (con salida registrada)
            if entry.exit_time is None:
                continue  # Saltar entradas sin salida
                
            entry_start = entry.entry_time
            entry_end = entry.exit_time
            entry_user = entry.user
            
            # Buscar turnos del mismo usuario
            user_schedules = [s for s in schedules if s.user == entry_user]
            
            entry_total_hours = 0
            
            for schedule in user_schedules:
                schedule_start = schedule.start_datetime
                schedule_end = schedule.end_datetime
                
                # Calcular superposición
                overlap = get_time_overlap(entry_start, entry_end, schedule_start, schedule_end)
                
                if overlap > 0:
                    entry_total_hours += overlap
                    total_worked_hours += overlap
                    
                    # Agrupar por usuario
                    user_key = f"{entry_user.username} (ID: {entry_user.id})"
                    if user_key not in user_hours:
                        user_hours[user_key] = 0
                    user_hours[user_key] += overlap
                    
                    # Agrupar por turno
                    if schedule.id not in schedule_hours:
                        schedule_hours[schedule.id] = 0
                    schedule_hours[schedule.id] += overlap
                    
                    overlaps_found.append({
                        'entry_id': entry.id,
                        'schedule_id': schedule.id,
                        'user': entry_user.username,
                        'overlap_hours': round(overlap, 4),
                        'entry_period': f"{entry_start.strftime('%H:%M')} - {entry_end.strftime('%H:%M')}",
                        'schedule_period': f"{schedule_start.strftime('%H:%M')} - {schedule_end.strftime('%H:%M')}"
                    })
        
        # Calcular horas asignadas totales
        total_assigned_hours = 0
        for schedule in schedules:
            start = schedule.start_datetime
            end = schedule.end_datetime
            duration = (end - start).total_seconds() / 3600
            total_assigned_hours += duration
        
        # Calcular porcentaje de cumplimiento
        compliance_percentage = 0
        if total_assigned_hours > 0:
            compliance_percentage = (total_worked_hours / total_assigned_hours) * 100
        
        return Response({
            'total_worked_hours': round(total_worked_hours, 4),
            'total_assigned_hours': round(total_assigned_hours, 4),
            'compliance_percentage': round(compliance_percentage, 2),
            'entries_processed': len(entries),
            'schedules_processed': len(schedules),
            'user_hours': user_hours,
            'schedule_hours': schedule_hours,
            'overlaps_found': overlaps_found,
            'filters_applied': {
                'from_date': from_date,
                'to_date': to_date,
                'user_id': user_id,
                'room_id': room_id
            }
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Error en calculate_worked_hours: {e}")
        return Response({
            'error': 'Error al calcular horas trabajadas',
            'details': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAdminUser])
def calculate_late_arrivals(request):
    """
    Endpoint para calcular llegadas tarde
    """
    try:
        # Obtener parámetros de filtro
        from_date = request.GET.get('from_date', '').strip()
        to_date = request.GET.get('to_date', '').strip()
        user_id = request.GET.get('user_id', '').strip()
        room_id = request.GET.get('room_id', '').strip()
        
        # Obtener todos los turnos
        schedules_queryset = Schedule.objects.select_related('user', 'room').all()
        
        # Aplicar filtros de fecha a turnos
        if from_date and to_date:
            try:
                from datetime import datetime, timezone
                if 'T' in from_date:
                    from_date_obj = datetime.fromisoformat(from_date.replace('Z', '+00:00'))
                else:
                    from_date_obj = datetime.fromisoformat(from_date)
                
                if 'T' in to_date:
                    to_date_obj = datetime.fromisoformat(to_date.replace('Z', '+00:00'))
                else:
                    to_date_obj = datetime.fromisoformat(to_date)
                
                if from_date_obj.tzinfo is None:
                    from_date_obj = from_date_obj.replace(tzinfo=timezone.utc)
                if to_date_obj.tzinfo is None:
                    to_date_obj = to_date_obj.replace(tzinfo=timezone.utc)
                
                start_datetime = from_date_obj.replace(hour=0, minute=0, second=0, microsecond=0)
                end_datetime = to_date_obj.replace(hour=23, minute=59, second=59, microsecond=999999)
                
                if start_datetime.tzinfo is not None:
                    start_datetime = start_datetime.replace(tzinfo=None)
                if end_datetime.tzinfo is not None:
                    end_datetime = end_datetime.replace(tzinfo=None)
                
                schedules_queryset = schedules_queryset.filter(
                    start_datetime__gte=start_datetime,
                    start_datetime__lte=end_datetime
                )
            except ValueError as e:
                logger.warning(f"Error parsing date range: {e}")
                pass
        elif from_date:
            try:
                from datetime import datetime, timezone
                if 'T' in from_date:
                    from_date_obj = datetime.fromisoformat(from_date.replace('Z', '+00:00'))
                else:
                    from_date_obj = datetime.fromisoformat(from_date)
                
                if from_date_obj.tzinfo is None:
                    from_date_obj = from_date_obj.replace(tzinfo=timezone.utc)
                
                start_datetime = from_date_obj.replace(hour=0, minute=0, second=0, microsecond=0)
                if start_datetime.tzinfo is not None:
                    start_datetime = start_datetime.replace(tzinfo=None)
                schedules_queryset = schedules_queryset.filter(start_datetime__gte=start_datetime)
            except ValueError as e:
                logger.warning(f"Error parsing from_date: {e}")
                pass
        elif to_date:
            try:
                from datetime import datetime, timezone
                if 'T' in to_date:
                    to_date_obj = datetime.fromisoformat(to_date.replace('Z', '+00:00'))
                else:
                    to_date_obj = datetime.fromisoformat(to_date)
                
                if to_date_obj.tzinfo is None:
                    to_date_obj = to_date_obj.replace(tzinfo=timezone.utc)
                
                end_datetime = to_date_obj.replace(hour=23, minute=59, second=59, microsecond=999999)
                if end_datetime.tzinfo is not None:
                    end_datetime = end_datetime.replace(tzinfo=None)
                schedules_queryset = schedules_queryset.filter(start_datetime__lte=end_datetime)
            except ValueError as e:
                logger.warning(f"Error parsing to_date: {e}")
                pass
        
        # Aplicar filtros adicionales
        if user_id:
            try:
                user_id_int = int(user_id)
                schedules_queryset = schedules_queryset.filter(user_id=user_id_int)
            except ValueError:
                pass
        
        if room_id:
            try:
                room_id_int = int(room_id)
                schedules_queryset = schedules_queryset.filter(room_id=room_id_int)
            except ValueError:
                pass
        
        schedules = list(schedules_queryset)
        
        # Calcular llegadas tarde
        late_count = 0
        processed_entries = set()
        late_details = []
        
        # Zona horaria de Bogotá
        import pytz
        bogota_tz = pytz.timezone('America/Bogota')
        
        for schedule in schedules:
            # Convertir turno a zona horaria de Bogotá
            schedule_start = schedule.start_datetime
            if schedule_start.tzinfo is None:
                schedule_start = bogota_tz.localize(schedule_start)
            else:
                schedule_start = schedule_start.astimezone(bogota_tz)
            
            # Buscar entradas desde 10 minutos antes del turno hasta final del día
            turno_end = schedule_start.replace(hour=23, minute=59, second=59, microsecond=999999)
            rango_inicio = schedule_start - timedelta(minutes=10)
            
            schedule_entries = RoomEntry.objects.filter(
                user=schedule.user,
                entry_time__gte=rango_inicio,
                entry_time__lte=turno_end
            ).order_by('entry_time')
            
            if schedule_entries.exists():
                first_entry = schedule_entries.first()
                entry_time = first_entry.entry_time
                
                # Convertir entrada a zona horaria de Bogotá
                if entry_time.tzinfo is None:
                    entry_time = bogota_tz.localize(entry_time)
                else:
                    entry_time = entry_time.astimezone(bogota_tz)
                
                if first_entry.id not in processed_entries:
                    # Verificar si es llegada tarde (más de 5 minutos)
                    time_diff = (entry_time - schedule_start).total_seconds() / 60
                    is_late = time_diff > 5
                    
                    if is_late:
                        late_count += 1
                        processed_entries.add(first_entry.id)
                        
                        late_details.append({
                            'schedule_id': schedule.id,
                            'entry_id': first_entry.id,
                            'user': schedule.user.username,
                            'room': schedule.room.name,
                            'schedule_start': schedule_start.isoformat(),
                            'entry_time': entry_time.isoformat(),
                            'delay_minutes': round(time_diff, 2)
                        })
                    else:
                        # También registrar entradas a tiempo para debug
                        processed_entries.add(first_entry.id)
        
        return Response({
            'late_arrivals_count': late_count,
            'total_schedules': len(schedules),
            'late_details': late_details,
            'filters_applied': {
                'from_date': from_date,
                'to_date': to_date,
                'user_id': user_id,
                'room_id': room_id
            }
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Error en calculate_late_arrivals: {e}")
        return Response({
            'error': 'Error al calcular llegadas tarde',
            'details': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAdminUser])
def calculate_report_stats(request):
    """
    Endpoint completo para calcular todas las estadísticas de reportes
    """
    try:
        # Obtener parámetros de filtro
        from_date = request.GET.get('from_date', '').strip()
        to_date = request.GET.get('to_date', '').strip()
        user_id = request.GET.get('user_id', '').strip()
        room_id = request.GET.get('room_id', '').strip()
        
        # Calcular horas trabajadas directamente
        entries_queryset = RoomEntry.objects.select_related('user', 'room').all()
        
        # Aplicar filtros de fecha a entradas
        if from_date and to_date:
            try:
                from datetime import datetime, timezone
                if 'T' in from_date:
                    from_date_obj = datetime.fromisoformat(from_date.replace('Z', '+00:00'))
                else:
                    from_date_obj = datetime.fromisoformat(from_date)
                
                if 'T' in to_date:
                    to_date_obj = datetime.fromisoformat(to_date.replace('Z', '+00:00'))
                else:
                    to_date_obj = datetime.fromisoformat(to_date)
                
                if from_date_obj.tzinfo is None:
                    from_date_obj = from_date_obj.replace(tzinfo=timezone.utc)
                if to_date_obj.tzinfo is None:
                    to_date_obj = to_date_obj.replace(tzinfo=timezone.utc)
                
                start_datetime = from_date_obj.replace(hour=0, minute=0, second=0, microsecond=0)
                end_datetime = to_date_obj.replace(hour=23, minute=59, second=59, microsecond=999999)
                
                if start_datetime.tzinfo is not None:
                    start_datetime = start_datetime.replace(tzinfo=None)
                if end_datetime.tzinfo is not None:
                    end_datetime = end_datetime.replace(tzinfo=None)
                
                entries_queryset = entries_queryset.filter(
                    entry_time__gte=start_datetime,
                    entry_time__lte=end_datetime
                )
            except ValueError as e:
                logger.warning(f"Error parsing date range: {e}")
                pass
        elif from_date:
            try:
                from datetime import datetime, timezone
                if 'T' in from_date:
                    from_date_obj = datetime.fromisoformat(from_date.replace('Z', '+00:00'))
                else:
                    from_date_obj = datetime.fromisoformat(from_date)
                
                if from_date_obj.tzinfo is None:
                    from_date_obj = from_date_obj.replace(tzinfo=timezone.utc)
                
                start_datetime = from_date_obj.replace(hour=0, minute=0, second=0, microsecond=0)
                if start_datetime.tzinfo is not None:
                    start_datetime = start_datetime.replace(tzinfo=None)
                entries_queryset = entries_queryset.filter(entry_time__gte=start_datetime)
            except ValueError as e:
                logger.warning(f"Error parsing from_date: {e}")
                pass
        elif to_date:
            try:
                from datetime import datetime, timezone
                if 'T' in to_date:
                    to_date_obj = datetime.fromisoformat(to_date.replace('Z', '+00:00'))
                else:
                    to_date_obj = datetime.fromisoformat(to_date)
                
                if to_date_obj.tzinfo is None:
                    to_date_obj = to_date_obj.replace(tzinfo=timezone.utc)
                
                end_datetime = to_date_obj.replace(hour=23, minute=59, second=59, microsecond=999999)
                if end_datetime.tzinfo is not None:
                    end_datetime = end_datetime.replace(tzinfo=None)
                entries_queryset = entries_queryset.filter(entry_time__lte=end_datetime)
            except ValueError as e:
                logger.warning(f"Error parsing to_date: {e}")
                pass
        
        # Aplicar filtros adicionales
        if user_id:
            try:
                user_id_int = int(user_id)
                entries_queryset = entries_queryset.filter(user_id=user_id_int)
            except ValueError:
                pass
        
        if room_id:
            try:
                room_id_int = int(room_id)
                entries_queryset = entries_queryset.filter(room_id=room_id_int)
            except ValueError:
                pass
        
        entries = list(entries_queryset)
        
        # Obtener turnos con filtros aplicados
        schedules_queryset = Schedule.objects.select_related('user', 'room').all()
        
        # Aplicar filtros de fecha a turnos
        if from_date and to_date:
            try:
                from datetime import datetime, timezone
                if 'T' in from_date:
                    from_date_obj = datetime.fromisoformat(from_date.replace('Z', '+00:00'))
                else:
                    from_date_obj = datetime.fromisoformat(from_date)
                
                if 'T' in to_date:
                    to_date_obj = datetime.fromisoformat(to_date.replace('Z', '+00:00'))
                else:
                    to_date_obj = datetime.fromisoformat(to_date)
                
                if from_date_obj.tzinfo is None:
                    from_date_obj = from_date_obj.replace(tzinfo=timezone.utc)
                if to_date_obj.tzinfo is None:
                    to_date_obj = to_date_obj.replace(tzinfo=timezone.utc)
                
                start_datetime = from_date_obj.replace(hour=0, minute=0, second=0, microsecond=0)
                end_datetime = to_date_obj.replace(hour=23, minute=59, second=59, microsecond=999999)
                
                if start_datetime.tzinfo is not None:
                    start_datetime = start_datetime.replace(tzinfo=None)
                if end_datetime.tzinfo is not None:
                    end_datetime = end_datetime.replace(tzinfo=None)
                
                schedules_queryset = schedules_queryset.filter(
                    start_datetime__gte=start_datetime,
                    start_datetime__lte=end_datetime
                )
            except ValueError as e:
                logger.warning(f"Error parsing date range: {e}")
                pass
        elif from_date:
            try:
                from datetime import datetime, timezone
                if 'T' in from_date:
                    from_date_obj = datetime.fromisoformat(from_date.replace('Z', '+00:00'))
                else:
                    from_date_obj = datetime.fromisoformat(from_date)
                
                if from_date_obj.tzinfo is None:
                    from_date_obj = from_date_obj.replace(tzinfo=timezone.utc)
                
                start_datetime = from_date_obj.replace(hour=0, minute=0, second=0, microsecond=0)
                if start_datetime.tzinfo is not None:
                    start_datetime = start_datetime.replace(tzinfo=None)
                schedules_queryset = schedules_queryset.filter(start_datetime__gte=start_datetime)
            except ValueError as e:
                logger.warning(f"Error parsing from_date: {e}")
                pass
        elif to_date:
            try:
                from datetime import datetime, timezone
                if 'T' in to_date:
                    to_date_obj = datetime.fromisoformat(to_date.replace('Z', '+00:00'))
                else:
                    to_date_obj = datetime.fromisoformat(to_date)
                
                if to_date_obj.tzinfo is None:
                    to_date_obj = to_date_obj.replace(tzinfo=timezone.utc)
                
                end_datetime = to_date_obj.replace(hour=23, minute=59, second=59, microsecond=999999)
                if end_datetime.tzinfo is not None:
                    end_datetime = end_datetime.replace(tzinfo=None)
                schedules_queryset = schedules_queryset.filter(start_datetime__lte=end_datetime)
            except ValueError as e:
                logger.warning(f"Error parsing to_date: {e}")
                pass
        
        # Aplicar filtros adicionales a turnos
        if user_id:
            try:
                user_id_int = int(user_id)
                schedules_queryset = schedules_queryset.filter(user_id=user_id_int)
            except ValueError:
                pass
        
        if room_id:
            try:
                room_id_int = int(room_id)
                schedules_queryset = schedules_queryset.filter(room_id=room_id_int)
            except ValueError:
                pass
        
        schedules = list(schedules_queryset)
        
        # Calcular horas trabajadas con superposición
        total_worked_hours = 0.0
        for entry in entries:
            # Solo procesar entradas completas (con salida registrada)
            if entry.exit_time is None:
                continue  # Saltar entradas sin salida
                
            entry_start = entry.entry_time
            entry_end = entry.exit_time
            entry_user = entry.user
            
            user_schedules = [s for s in schedules if s.user == entry_user]
            
            for schedule in user_schedules:
                schedule_start = schedule.start_datetime
                schedule_end = schedule.end_datetime
                
                overlap = get_time_overlap(entry_start, entry_end, schedule_start, schedule_end)
                if overlap > 0:
                    total_worked_hours += overlap
        
        # Calcular llegadas tarde
        late_count = 0
        
        # Zona horaria de Bogotá
        import pytz
        bogota_tz = pytz.timezone('America/Bogota')
        
        for schedule in schedules:
            # Convertir turno a zona horaria de Bogotá
            schedule_start = schedule.start_datetime
            if schedule_start.tzinfo is None:
                schedule_start = bogota_tz.localize(schedule_start)
            else:
                schedule_start = schedule_start.astimezone(bogota_tz)
            
            # Buscar entradas desde 10 minutos antes del turno hasta final del día
            turno_end = schedule_start.replace(hour=23, minute=59, second=59, microsecond=999999)
            rango_inicio = schedule_start - timedelta(minutes=10)
            
            schedule_entries = RoomEntry.objects.filter(
                user=schedule.user,
                entry_time__gte=rango_inicio,
                entry_time__lte=turno_end
            ).order_by('entry_time')
            
            if schedule_entries.exists():
                first_entry = schedule_entries.first()
                entry_time = first_entry.entry_time
                
                # Convertir entrada a zona horaria de Bogotá
                if entry_time.tzinfo is None:
                    entry_time = bogota_tz.localize(entry_time)
                else:
                    entry_time = entry_time.astimezone(bogota_tz)
                
                time_diff = (entry_time - schedule_start).total_seconds() / 60
                if time_diff > 5:
                    late_count += 1
        
        # Calcular horas asignadas
        total_assigned_hours = 0
        for schedule in schedules:
            start = schedule.start_datetime
            end = schedule.end_datetime
            duration = (end - start).total_seconds() / 3600
            total_assigned_hours += duration
        
        # Calcular horas restantes
        remaining_hours = total_assigned_hours - total_worked_hours
        
        return Response({
            'late_arrivals_count': late_count,
            'total_assigned_hours': round(total_assigned_hours, 4),
            'total_worked_hours': round(total_worked_hours, 4),
            'remaining_hours': round(remaining_hours, 4),
            'compliance_percentage': round((total_worked_hours / total_assigned_hours * 100) if total_assigned_hours > 0 else 0, 2),
            'entries_processed': len(entries),
            'schedules_processed': len(schedules),
            'filters_applied': {
                'from_date': from_date,
                'to_date': to_date,
                'user_id': user_id,
                'room_id': room_id
            }
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Error en calculate_report_stats: {e}")
        return Response({
            'error': 'Error al calcular estadísticas de reportes',
            'details': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAdminUser])
def get_turn_comparison(request):
    """
    Endpoint para obtener comparación entre turnos asignados y registros reales
    """
    try:
        # Obtener parámetros de filtro
        date_from = request.GET.get('date_from', '').strip()
        date_to = request.GET.get('date_to', '').strip()
        user_id = request.GET.get('user_id', '').strip()
        room_id = request.GET.get('room_id', '').strip()
        
        # Validar fechas requeridas
        if not date_from or not date_to:
            return Response({
                'error': 'Se requieren los parámetros date_from y date_to'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Convertir parámetros a enteros si se proporcionan
        user_id_int = None
        room_id_int = None
        
        if user_id:
            try:
                user_id_int = int(user_id)
            except ValueError:
                return Response({
                    'error': 'user_id debe ser un número entero válido'
                }, status=status.HTTP_400_BAD_REQUEST)
        
        if room_id:
            try:
                room_id_int = int(room_id)
            except ValueError:
                return Response({
                    'error': 'room_id debe ser un número entero válido'
                }, status=status.HTTP_400_BAD_REQUEST)
        
        # Generar comparación
        comparaciones = generar_comparacion_turnos_registros(
            date_from, date_to, user_id_int, room_id_int
        )
        
        # Serializar resultados
        serializer = TurnComparisonSerializer(comparaciones, many=True)
        
        return Response({
            'comparaciones': serializer.data,
            'total_registros': len(comparaciones),
            'filters_applied': {
                'date_from': date_from,
                'date_to': date_to,
                'user_id': user_id,
                'room_id': room_id
            }
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Error en get_turn_comparison: {e}")
        return Response({
            'error': 'Error al obtener comparación de turnos',
            'details': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsMonitorUser])
def validate_entry_access(request):
    """
    Endpoint para validar si un usuario puede registrarse anticipadamente
    """
    try:
        room_id = request.data.get('room_id')
        access_time_str = request.data.get('access_time')
        
        if not room_id:
            return Response({
                'error': 'Se requiere room_id'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Convertir access_time si se proporciona
        if access_time_str:
            try:
                access_time = datetime.fromisoformat(access_time_str.replace('Z', '+00:00'))
                if access_time.tzinfo is None:
                    access_time = timezone.make_aware(access_time)
            except ValueError:
                return Response({
                    'error': 'Formato de access_time inválido. Use ISO format'
                }, status=status.HTTP_400_BAD_REQUEST)
        else:
            access_time = timezone.now()
        
        # Validar acceso anticipado
        permitido, mensaje = validar_acceso_anticipado(request.user, room_id, access_time)
        
        # Calcular diferencia
        from schedule.models import Schedule
        turnos = Schedule.objects.filter(
            user=request.user,
            room_id=room_id,
            start_datetime__date=access_time.date()
        )
        
        diferencia = 0
        if turnos.exists():
            turno = turnos.first()
            diferencia = (access_time - turno.start_datetime).total_seconds() / 60
        
        # Serializar respuesta
        serializer = EntryValidationSerializer({
            'permitido': permitido,
            'diferencia': diferencia,
            'mensaje': mensaje
        })
        
        return Response(serializer.data, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Error en validate_entry_access: {e}")
        return Response({
            'error': 'Error al validar acceso',
            'details': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAdminUser])
def get_id_statistics(request):
    """
    Obtiene estadísticas sobre el uso de IDs en el sistema
    
    Endpoint para administradores que muestra:
    - Eficiencia de uso de IDs
    - IDs disponibles para reutilización
    - Estadísticas generales de la base de datos
    """
    try:
        from .id_reuse import RoomEntryIDManager
        from .models import RoomEntry
        
        # Obtener estadísticas generales
        stats = RoomEntryIDManager.get_room_entry_stats()
        
        # Agregar información adicional
        total_entries = RoomEntry.objects.count()
        active_entries = RoomEntry.objects.filter(exit_time__isnull=True).count()
        
        response_data = {
            'id_statistics': stats,
            'database_info': {
                'total_entries': total_entries,
                'active_entries': active_entries,
                'completed_entries': total_entries - active_entries
            },
            'optimization': {
                'reusable_ids_available': len(stats.get('reusable_ids', [])),
                'potential_space_saving': stats.get('gaps_count', 0),
                'efficiency_percentage': stats.get('efficiency', 100.0)
            },
            'timestamp': timezone.now().isoformat()
        }
        
        logger.info(f"Estadísticas de ID solicitadas por admin: {request.user.username}")
        
        return Response(response_data, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Error al obtener estadísticas de ID: {e}")
        return Response({
            'error': 'Error al obtener estadísticas',
            'details': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsMonitorUser])
def get_monitor_late_arrivals(request):
    """
    Endpoint para que los monitores vean sus propias llegadas tarde
    Solo muestra datos del monitor actualmente logueado
    """
    try:
        # Obtener parámetros de filtro
        from_date = request.GET.get('from_date', '').strip()
        to_date = request.GET.get('to_date', '').strip()
        
        # El usuario actual (monitor logueado)
        current_user = request.user
        
        # Obtener turnos del monitor actual
        schedules_queryset = Schedule.objects.filter(user=current_user).select_related('room')
        
        # Aplicar filtros de fecha a turnos
        if from_date and to_date:
            try:
                from .timezone_utils import create_date_range_bogota
                start_datetime, end_datetime = create_date_range_bogota(from_date, to_date)
                schedules_queryset = schedules_queryset.filter(
                    start_datetime__gte=start_datetime,
                    start_datetime__lte=end_datetime
                )
            except ValueError as e:
                logger.warning(f"Error parsing date range: {e}")
                return Response({
                    'error': 'Formato de fecha inválido. Use YYYY-MM-DD'
                }, status=status.HTTP_400_BAD_REQUEST)
        elif from_date:
            try:
                from .timezone_utils import create_date_range_bogota
                start_datetime, _ = create_date_range_bogota(from_date)
                schedules_queryset = schedules_queryset.filter(start_datetime__gte=start_datetime)
            except ValueError as e:
                logger.warning(f"Error parsing from_date: {e}")
                return Response({
                    'error': 'Formato de fecha inválido. Use YYYY-MM-DD'
                }, status=status.HTTP_400_BAD_REQUEST)
        elif to_date:
            try:
                from .timezone_utils import create_date_range_bogota
                _, end_datetime = create_date_range_bogota(to_date, to_date)
                schedules_queryset = schedules_queryset.filter(start_datetime__lte=end_datetime)
            except ValueError as e:
                logger.warning(f"Error parsing to_date: {e}")
                return Response({
                    'error': 'Formato de fecha inválido. Use YYYY-MM-DD'
                }, status=status.HTTP_400_BAD_REQUEST)
        
        schedules = list(schedules_queryset)
        
        # Calcular llegadas tarde del monitor
        late_count = 0
        late_details = []
        
        # Zona horaria de Bogotá
        import pytz
        bogota_tz = pytz.timezone('America/Bogota')
        
        for schedule in schedules:
            # Convertir turno a zona horaria de Bogotá
            schedule_start = schedule.start_datetime
            if schedule_start.tzinfo is None:
                schedule_start = bogota_tz.localize(schedule_start)
            else:
                schedule_start = schedule_start.astimezone(bogota_tz)
            
            # Buscar entradas desde 10 minutos antes del turno hasta final del día
            turno_end = schedule_start.replace(hour=23, minute=59, second=59, microsecond=999999)
            rango_inicio = schedule_start - timedelta(minutes=10)
            
            schedule_entries = RoomEntry.objects.filter(
                user=current_user,
                entry_time__gte=rango_inicio,
                entry_time__lte=turno_end
            ).order_by('entry_time')
            
            if schedule_entries.exists():
                first_entry = schedule_entries.first()
                entry_time = first_entry.entry_time
                
                # Convertir entrada a zona horaria de Bogotá
                if entry_time.tzinfo is None:
                    entry_time = bogota_tz.localize(entry_time)
                else:
                    entry_time = entry_time.astimezone(bogota_tz)
                
                time_diff = (entry_time - schedule_start).total_seconds() / 60
                if time_diff > 5:  # Más de 5 minutos tarde
                    late_count += 1
                    late_details.append({
                        'schedule_id': schedule.id,
                        'room_name': schedule.room.name,
                        'scheduled_time': schedule_start.strftime('%H:%M'),
                        'actual_time': entry_time.strftime('%H:%M'),
                        'delay_minutes': round(time_diff, 1),
                        'date': schedule_start.strftime('%Y-%m-%d'),
                        'notes': first_entry.notes or ''
                    })
        
        # Calcular estadísticas adicionales
        total_schedules = len(schedules)
        punctuality_percentage = round(((total_schedules - late_count) / total_schedules * 100) if total_schedules > 0 else 0, 2)
        
        return Response({
            'monitor_info': {
                'username': current_user.username,
                'full_name': current_user.get_full_name(),
                'email': current_user.email
            },
            'late_arrivals_count': late_count,
            'total_schedules': total_schedules,
            'punctuality_percentage': punctuality_percentage,
            'late_details': late_details,
            'filters_applied': {
                'from_date': from_date,
                'to_date': to_date
            }
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Error en get_monitor_late_arrivals: {e}")
        return Response({
            'error': 'Error al obtener llegadas tarde del monitor',
            'details': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)