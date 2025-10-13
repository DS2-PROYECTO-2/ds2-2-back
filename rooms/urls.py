from django.urls import path
from . import views, views_admin, views_reports

urlpatterns = [
    # Gestión de salas (Sprint 1)
    path('', views.room_list_view, name='room_list'), # GET - Listar salas disponibles                                                        
    path('<int:room_id>/', views.room_detail_view, name='room_detail'), # GET - Detalle de sala
    path('<int:room_id>/occupants/', views.room_current_occupants_view, name='room_occupants'), # GET - Ocupantes actuales de la sala
    
    # Registro de entrada/salida (Sprint 2) - Tarea 2 con validaciones
    path('entry/', views.room_entry_create_view, name='room_entry_create'),  # POST - Crear nueva entrada (ingreso a sala)
    path('entry/<int:entry_id>/exit/', views.room_entry_exit_view, name='room_entry_exit'), # POST - Registrar salida de sala (cerrar entrada activa)
    
    # Historial del usuario con información de duración y validaciones
    path('my-entries/', views.user_room_entries_view, name='user_room_entries'), # GET - Historial de entradas del usuario autenticado con duración y validaciones
    path('my-active-entry/', views.user_active_entry_view, name='user_active_entry'),   # GET - Verificar si el usuario tiene una entrada activa
    path('my-active-entry/exit/', views.user_active_entry_exit_view, name='user_active_entry_exit'), # POST - Cerrar la entrada activa del usuario autenticado
    path('my-daily-summary/', views.user_daily_summary_view, name='user_daily_summary'), # GET - Resumen diario de entradas del usuario autenticado
    
    # Mantenimiento del sistema
    path('close-expired-sessions/', views.close_expired_sessions_view, name='close_expired_sessions'), # POST - Cerrar sesiones expiradas automáticamente
    
    # Endpoints para administradores (nombres esperados por tests)
    path('admin/rooms/', views_admin.admin_rooms_list, name='admin_rooms_list'), # GET - Listar todas las salas (admin)
    path('admin/rooms/create/', views_admin.admin_room_create, name='admin_room_create'), # POST - Crear nueva sala (admin) 
    path('admin/rooms/<int:room_id>/', views_admin.admin_room_detail, name='admin_room_detail'),    # GET - Detalle de sala (admin)
    path('admin/rooms/<int:room_id>/update/', views_admin.admin_room_update, name='admin_room_update'), # PUT/PATCH - Actualizar sala (admin)
    path('admin/rooms/<int:room_id>/delete/', views_admin.admin_room_delete, name='admin_room_delete'), # DELETE - Eliminar sala (admin)

    # Endpoints admin adicionales
    path('entries/', views_admin.admin_entries_unpaginated, name='admin_entries_unpaginated'),
    path('entries/stats/', views_admin.admin_entries_stats, name='admin_entries_stats'),
    path('admin/entries/', views_admin.admin_entries_list, name='admin_entries_list'),

    ### *🔧 PASO 2: Modificar rooms/urls.py*

    
    # Endpoints de reportes con cálculos de superposición
    path('reports/worked-hours/', views_reports.calculate_worked_hours, name='calculate_worked_hours'),
    path('reports/late-arrivals/', views_reports.calculate_late_arrivals, name='calculate_late_arrivals'),
    path('reports/stats/', views_reports.calculate_report_stats, name='calculate_report_stats'),
    
    # NUEVOS ENDPOINTS: Comparación turnos vs registros y validación de acceso anticipado
    path('reports/turn-comparison/', views_reports.get_turn_comparison, name='get_turn_comparison'),
    path('entry/validate/', views_reports.validate_entry_access, name='validate_entry_access'),
    
    # Endpoint para monitores: sus propias llegadas tarde
    path('monitor/late-arrivals/', views_reports.get_monitor_late_arrivals, name='get_monitor_late_arrivals'),
    
    # Sistema de reutilización de IDs
    path('admin/id-statistics/', views_reports.get_id_statistics, name='get_id_statistics'),
]
