from django.urls import path
from . import views

urlpatterns = [
    # Gestión de salas (Sprint 1)
    path('', views.room_list_view, name='room_list'),                                                      # GET - Listar salas disponibles
    path('<int:room_id>/', views.room_detail_view, name='room_detail'),                                    # GET - Detalle de sala específica
    path('<int:room_id>/occupants/', views.room_current_occupants_view, name='room_occupants'),           # GET - Ocupantes actuales de sala
    
    # CRUD de salas para administradores 
    path('admin/rooms/', views.admin_rooms_list_view, name='admin_rooms_list'),                           # GET - Listar salas (admin)
    path('admin/rooms/create/', views.admin_room_create_view, name='admin_room_create'),                  # POST - Crear nueva sala
    path('admin/rooms/<int:room_id>/', views.admin_room_detail_view, name='admin_room_detail'),           # GET - Detalle sala con estadísticas
    path('admin/rooms/<int:room_id>/update/', views.admin_room_update_view, name='admin_room_update'),    # PUT/PATCH - Actualizar sala
    path('admin/rooms/<int:room_id>/delete/', views.admin_room_delete_view, name='admin_room_delete'),    # DELETE - Eliminar sala
    
    # Registro de entrada/salida (Sprint 2) - Tarea 2 con validaciones
    path('entry/', views.room_entry_create_view, name='room_entry_create'),                               # POST - Registrar entrada a sala
    path('entry/<int:entry_id>/exit/', views.room_entry_exit_view, name='room_entry_exit'),              # POST - Registrar salida de sala
    
    # Historial del usuario con información de duración y validaciones
    path('my-entries/', views.user_room_entries_view, name='user_room_entries'),                          # GET - Historial de entradas del usuario
    path('my-active-entry/', views.user_active_entry_view, name='user_active_entry'),                    # GET - Entrada activa del usuario
    path('my-active-entry/exit/', views.user_active_entry_exit_view, name='user_active_entry_exit'),     # POST - Salir de entrada activa
    path('my-daily-summary/', views.user_daily_summary_view, name='user_daily_summary'),                 # GET - Resumen diario del usuario
]