from django.utils import timezone
from django.db.models import Count, Sum
from datetime import timedelta
from users.models import User
from rooms.models import Room, RoomEntry
from notifications.models import Notification
from notifications.services import ExcessiveHoursChecker
import logging

logger = logging.getLogger(__name__)


class DashboardService:
    """
    Servicio para generar datos del dashboard
    """
    
    @staticmethod
    def get_admin_dashboard_data(user):
        """
        Generar datos del dashboard para administradores
        """
        try:
            # Estadísticas básicas
            total_users = User.objects.count()
            total_monitors = User.objects.filter(role='monitor').count()
            verified_monitors = User.objects.filter(role='monitor', is_verified=True).count()
            pending_verifications = User.objects.filter(role='monitor', is_verified=False).count()
            
            # Estadísticas de salas
            total_rooms = Room.objects.filter(is_active=True).count()
            active_entries = RoomEntry.objects.filter(exit_time__isnull=True).count()
            occupied_rooms = RoomEntry.objects.filter(exit_time__isnull=True).values('room').distinct().count()
            available_rooms = total_rooms - occupied_rooms
            
            # Estadísticas de notificaciones
            unread_notifications = Notification.objects.filter(user=user, read=False).count()
            
            # Estadísticas de tiempo (hoy)
            today = timezone.now().date()
            today_entries = RoomEntry.objects.filter(
                entry_time__date=today,
                exit_time__isnull=False
            )
            
            total_hours_today = 0
            if today_entries.exists():
                for entry in today_entries:
                    duration = entry.exit_time - entry.entry_time
                    total_hours_today += duration.total_seconds() / 3600
            
            # Duración promedio de sesiones
            completed_entries = RoomEntry.objects.filter(exit_time__isnull=False)
            if completed_entries.exists():
                total_duration = 0
                for entry in completed_entries:
                    duration = entry.exit_time - entry.entry_time
                    total_duration += duration.total_seconds() / 3600
                average_session_duration = total_duration / completed_entries.count()
            else:
                average_session_duration = 0
            
            # Alertas
            excessive_hours_alerts = Notification.objects.filter(
                notification_type='excessive_hours',
                created_at__gte=timezone.now() - timedelta(days=7)
            ).count()
            
            critical_alerts = Notification.objects.filter(
                notification_type='excessive_hours',
                created_at__gte=timezone.now() - timedelta(hours=24)
            ).count()
            
            # Mini cards
            mini_cards = [
                {
                    'title': 'Total Usuarios',
                    'value': str(total_users),
                    'icon': '👥',
                    'color': 'blue',
                    'trend': 'up' if total_users > 0 else 'stable',
                    'trend_value': f'+{total_users}'
                },
                {
                    'title': 'Monitores Activos',
                    'value': str(active_entries),
                    'icon': '🏢',
                    'color': 'green',
                    'trend': 'up' if active_entries > 0 else 'stable',
                    'trend_value': f'{active_entries} en salas'
                },
                {
                    'title': 'Pendientes Verificación',
                    'value': str(pending_verifications),
                    'icon': '⏳',
                    'color': 'orange',
                    'trend': 'down' if pending_verifications == 0 else 'up',
                    'trend_value': f'{pending_verifications} usuarios'
                },
                {
                    'title': 'Horas Hoy',
                    'value': f'{total_hours_today:.1f}h',
                    'icon': '⏰',
                    'color': 'purple',
                    'trend': 'up' if total_hours_today > 0 else 'stable',
                    'trend_value': f'{total_hours_today:.1f} horas'
                }
            ]
            
            # Actividades recientes
            recent_activities = DashboardService._get_recent_activities()
            
            # Alertas
            alerts = DashboardService._get_alerts()
            
            # Datos para gráficos
            charts_data = DashboardService._get_charts_data()
            
            return {
                'user_info': {
                    'id': user.id,
                    'username': user.username,
                    'full_name': user.get_full_name(),
                    'role': user.role,
                    'is_verified': user.is_verified
                },
                'stats': {
                    'total_users': total_users,
                    'total_rooms': total_rooms,
                    'active_entries': active_entries,
                    'unread_notifications': unread_notifications,
                    'total_monitors': total_monitors,
                    'verified_monitors': verified_monitors,
                    'pending_verifications': pending_verifications,
                    'occupied_rooms': occupied_rooms,
                    'available_rooms': available_rooms,
                    'total_hours_today': total_hours_today,
                    'average_session_duration': average_session_duration,
                    'excessive_hours_alerts': excessive_hours_alerts,
                    'critical_alerts': critical_alerts
                },
                'mini_cards': mini_cards,
                'recent_activities': recent_activities,
                'alerts': alerts,
                'charts_data': charts_data
            }
            
        except Exception as e:
            logger.error(f"Error generando dashboard de admin: {e}")
            return DashboardService._get_error_dashboard()
    
    @staticmethod
    def get_monitor_dashboard_data(user):
        """
        Generar datos del dashboard para monitores
        """
        try:
            # Entrada activa
            active_entry = RoomEntry.objects.filter(user=user, exit_time__isnull=True).first()
            
            # Estadísticas del usuario
            RoomEntry.objects.filter(user=user).count()
            completed_entries = RoomEntry.objects.filter(user=user, exit_time__isnull=False).count()
            
            # Horas totales (últimos 30 días)
            thirty_days_ago = timezone.now() - timedelta(days=30)
            recent_entries = RoomEntry.objects.filter(
                user=user,
                entry_time__gte=thirty_days_ago,
                exit_time__isnull=False
            )
            
            total_hours_30_days = 0
            for entry in recent_entries:
                duration = entry.exit_time - entry.entry_time
                total_hours_30_days += duration.total_seconds() / 3600
            
            # Notificaciones no leídas
            unread_notifications = Notification.objects.filter(user=user, read=False).count()
            
            # Mini cards para monitores
            mini_cards = [
                {
                    'title': 'Estado Actual',
                    'value': 'En sala' if active_entry else 'Disponible',
                    'icon': '🏢' if active_entry else '✅',
                    'color': 'green' if active_entry else 'blue'
                },
                {
                    'title': 'Sesiones Completadas',
                    'value': str(completed_entries),
                    'icon': '📊',
                    'color': 'purple',
                    'trend': 'up' if completed_entries > 0 else 'stable',
                    'trend_value': f'{completed_entries} sesiones'
                },
                {
                    'title': 'Horas (30 días)',
                    'value': f'{total_hours_30_days:.1f}h',
                    'icon': '⏰',
                    'color': 'orange',
                    'trend': 'up' if total_hours_30_days > 0 else 'stable',
                    'trend_value': f'{total_hours_30_days:.1f} horas'
                },
                {
                    'title': 'Notificaciones',
                    'value': str(unread_notifications),
                    'icon': '🔔',
                    'color': 'red' if unread_notifications > 0 else 'green',
                    'trend': 'up' if unread_notifications > 0 else 'stable',
                    'trend_value': f'{unread_notifications} no leídas'
                }
            ]
            
            # Actividades recientes del usuario
            recent_activities = DashboardService._get_user_recent_activities(user)
            
            # Alertas del usuario
            alerts = DashboardService._get_user_alerts(user)
            
            return {
                'user_info': {
                    'id': user.id,
                    'username': user.username,
                    'full_name': user.get_full_name(),
                    'role': user.role,
                    'is_verified': user.is_verified
                },
                'stats': {
                    'total_users': 1,  # Solo el usuario actual
                    'total_rooms': Room.objects.filter(is_active=True).count(),
                    'active_entries': 1 if active_entry else 0,
                    'unread_notifications': unread_notifications,
                    'total_monitors': 1,
                    'verified_monitors': 1 if user.is_verified else 0,
                    'pending_verifications': 0 if user.is_verified else 1,
                    'occupied_rooms': 1 if active_entry else 0,
                    'available_rooms': Room.objects.filter(is_active=True).count() - (1 if active_entry else 0),
                    'total_hours_today': total_hours_30_days,
                    'average_session_duration': total_hours_30_days / max(completed_entries, 1),
                    'excessive_hours_alerts': 0,
                    'critical_alerts': 0
                },
                'mini_cards': mini_cards,
                'recent_activities': recent_activities,
                'alerts': alerts,
                'charts_data': DashboardService._get_user_charts_data(user)
            }
            
        except Exception as e:
            logger.error(f"Error generando dashboard de monitor: {e}")
            return DashboardService._get_error_dashboard()
    
    @staticmethod
    def _get_recent_activities():
        """
        Obtener actividades recientes del sistema
        """
        try:
            # Últimas entradas y salidas
            recent_entries = RoomEntry.objects.select_related('user', 'room').order_by('-entry_time')[:10]
            
            activities = []
            for entry in recent_entries:
                activity_type = 'exit' if entry.exit_time else 'entry'
                activities.append({
                    'id': entry.id,
                    'type': activity_type,
                    'user': entry.user.get_full_name(),
                    'room': entry.room.name,
                    'timestamp': entry.entry_time if activity_type == 'entry' else entry.exit_time,
                    'description': f"{entry.user.get_full_name()} {'salió de' if activity_type == 'exit' else 'entró a'} {entry.room.name}"
                })
            
            return activities
            
        except Exception as e:
            logger.error(f"Error obteniendo actividades recientes: {e}")
            return []
    
    @staticmethod
    def _get_user_recent_activities(user):
        """
        Obtener actividades recientes del usuario
        """
        try:
            recent_entries = RoomEntry.objects.filter(user=user).select_related('room').order_by('-entry_time')[:5]
            
            activities = []
            for entry in recent_entries:
                activity_type = 'exit' if entry.exit_time else 'entry'
                activities.append({
                    'id': entry.id,
                    'type': activity_type,
                    'room': entry.room.name,
                    'timestamp': entry.entry_time if activity_type == 'entry' else entry.exit_time,
                    'description': f"{'Saliste de' if activity_type == 'exit' else 'Entraste a'} {entry.room.name}"
                })
            
            return activities
            
        except Exception as e:
            logger.error(f"Error obteniendo actividades del usuario: {e}")
            return []
    
    @staticmethod
    def _get_alerts():
        """
        Obtener alertas del sistema
        """
        try:
            alerts = []
            
            # Monitores con exceso de horas
            excessive_monitors = ExcessiveHoursChecker.get_monitors_with_excessive_hours()
            for monitor in excessive_monitors:
                alerts.append({
                    'type': 'excessive_hours',
                    'severity': 'critical' if monitor['is_critical'] else 'warning',
                    'title': f'Exceso de horas - {monitor["user"].get_full_name()}',
                    'message': f'{monitor["user"].get_full_name()} lleva {monitor["total_hours"]:.1f} horas en {monitor["room"].name}',
                    'timestamp': timezone.now()
                })
            
            return alerts
            
        except Exception as e:
            logger.error(f"Error obteniendo alertas: {e}")
            return []
    
    @staticmethod
    def _get_user_alerts(user):
        """
        Obtener alertas del usuario
        """
        try:
            alerts = []
            
            # Verificar si el usuario tiene exceso de horas
            active_entry = RoomEntry.objects.filter(user=user, exit_time__isnull=True).first()
            if active_entry:
                from rooms.services import RoomEntryBusinessLogic
                duration_info = RoomEntryBusinessLogic.calculate_session_duration(active_entry)
                total_hours = duration_info.get('current_duration_hours', 0)
                
                if total_hours > 8:
                    alerts.append({
                        'type': 'excessive_hours',
                        'severity': 'critical' if total_hours > 12 else 'warning',
                        'title': 'Exceso de horas',
                        'message': f'Has excedido las 8 horas permitidas. Duración actual: {total_hours:.1f} horas',
                        'timestamp': timezone.now()
                    })
                elif total_hours > 7:
                    alerts.append({
                        'type': 'warning_hours',
                        'severity': 'warning',
                        'title': 'Aproximándose al límite',
                        'message': f'Llevas {total_hours:.1f} horas. Te acercas al límite de 8 horas',
                        'timestamp': timezone.now()
                    })
            
            return alerts
            
        except Exception as e:
            logger.error(f"Error obteniendo alertas del usuario: {e}")
            return []
    
    @staticmethod
    def _get_charts_data():
        """
        Obtener datos para gráficos
        """
        try:
            # Datos de uso por día (últimos 7 días)
            timezone.now() - timedelta(days=7)
            daily_usage = []
            
            for i in range(7):
                date = (timezone.now() - timedelta(days=i)).date()
                entries = RoomEntry.objects.filter(
                    entry_time__date=date,
                    exit_time__isnull=False
                )
                
                total_hours = 0
                for entry in entries:
                    duration = entry.exit_time - entry.entry_time
                    total_hours += duration.total_seconds() / 3600
                
                daily_usage.append({
                    'date': date.isoformat(),
                    'hours': round(total_hours, 1),
                    'sessions': entries.count()
                })
            
            return {
                'daily_usage': daily_usage,
                'room_occupancy': DashboardService._get_room_occupancy_data()
            }
            
        except Exception as e:
            logger.error(f"Error obteniendo datos de gráficos: {e}")
            return {'daily_usage': [], 'room_occupancy': []}
    
    @staticmethod
    def _get_user_charts_data(user):
        """
        Obtener datos de gráficos para el usuario
        """
        try:
            # Datos de uso del usuario por día (últimos 7 días)
            timezone.now() - timedelta(days=7)
            daily_usage = []
            
            for i in range(7):
                date = (timezone.now() - timedelta(days=i)).date()
                entries = RoomEntry.objects.filter(
                    user=user,
                    entry_time__date=date,
                    exit_time__isnull=False
                )
                
                total_hours = 0
                for entry in entries:
                    duration = entry.exit_time - entry.entry_time
                    total_hours += duration.total_seconds() / 3600
                
                daily_usage.append({
                    'date': date.isoformat(),
                    'hours': round(total_hours, 1),
                    'sessions': entries.count()
                })
            
            return {
                'daily_usage': daily_usage,
                'room_usage': DashboardService._get_user_room_usage_data(user)
            }
            
        except Exception as e:
            logger.error(f"Error obteniendo datos de gráficos del usuario: {e}")
            return {'daily_usage': [], 'room_usage': []}
    
    @staticmethod
    def _get_room_occupancy_data():
        """
        Obtener datos de ocupación de salas
        """
        try:
            rooms = Room.objects.filter(is_active=True)
            occupancy_data = []
            
            for room in rooms:
                active_count = RoomEntry.objects.filter(room=room, exit_time__isnull=True).count()
                occupancy_data.append({
                    'room_name': room.name,
                    'active_users': active_count,
                    'capacity': room.capacity,
                    'occupancy_rate': round((active_count / room.capacity) * 100, 1) if room.capacity > 0 else 0
                })
            
            return occupancy_data
            
        except Exception as e:
            logger.error(f"Error obteniendo datos de ocupación: {e}")
            return []
    
    @staticmethod
    def _get_user_room_usage_data(user):
        """
        Obtener datos de uso de salas del usuario
        """
        try:
            # Entradas del usuario por sala (últimos 30 días)
            thirty_days_ago = timezone.now() - timedelta(days=30)
            room_usage = []
            
            entries_by_room = RoomEntry.objects.filter(
                user=user,
                entry_time__gte=thirty_days_ago
            ).values('room__name').annotate(
                total_sessions=Count('id'),
                total_hours=Sum('exit_time' - 'entry_time')
            )
            
            for room_data in entries_by_room:
                room_usage.append({
                    'room_name': room_data['room__name'],
                    'sessions': room_data['total_sessions'],
                    'hours': round(room_data['total_hours'].total_seconds() / 3600, 1) if room_data['total_hours'] else 0
                })
            
            return room_usage
            
        except Exception as e:
            logger.error(f"Error obteniendo datos de uso de salas: {e}")
            return []
    
    @staticmethod
    def _get_error_dashboard():
        """
        Dashboard de error por defecto
        """
        return {
            'user_info': {},
            'stats': {
                'total_users': 0,
                'total_rooms': 0,
                'active_entries': 0,
                'unread_notifications': 0,
                'total_monitors': 0,
                'verified_monitors': 0,
                'pending_verifications': 0,
                'occupied_rooms': 0,
                'available_rooms': 0,
                'total_hours_today': 0,
                'average_session_duration': 0,
                'excessive_hours_alerts': 0,
                'critical_alerts': 0
            },
            'mini_cards': [],
            'recent_activities': [],
            'alerts': [],
            'charts_data': {'daily_usage': [], 'room_occupancy': []}
        }
