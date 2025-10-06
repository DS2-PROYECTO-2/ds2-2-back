from django.urls import path
from . import views, views_admin

urlpatterns = [
    # Gestión de salas (Sprint 1)
    path('', views.room_list_view, name='room_list'),
    path('<int:room_id>/', views.room_detail_view, name='room_detail'),
    path('<int:room_id>/occupants/', views.room_current_occupants_view, name='room_occupants'),
    
    # Registro de entrada/salida (Sprint 2) - Tarea 2 con validaciones
    path('entry/', views.room_entry_create_view, name='room_entry_create'),
    path('entry/<int:entry_id>/exit/', views.room_entry_exit_view, name='room_entry_exit'),
    
    # Historial del usuario con información de duración y validaciones
    path('my-entries/', views.user_room_entries_view, name='user_room_entries'),
    path('my-active-entry/', views.user_active_entry_view, name='user_active_entry'),
    path('my-active-entry/exit/', views.user_active_entry_exit_view, name='user_active_entry_exit'),
    path('my-daily-summary/', views.user_daily_summary_view, name='user_daily_summary'),
    
    # Endpoints para administradores (nombres esperados por tests)
    path('admin/rooms/', views_admin.admin_rooms_list, name='admin_rooms_list'),
    path('admin/rooms/create/', views_admin.admin_room_create, name='admin_room_create'),
    path('admin/rooms/<int:room_id>/', views_admin.admin_room_detail, name='admin_room_detail'),
    path('admin/rooms/<int:room_id>/update/', views_admin.admin_room_update, name='admin_room_update'),
    path('admin/rooms/<int:room_id>/delete/', views_admin.admin_room_delete, name='admin_room_delete'),

    # Endpoints admin adicionales
    path('entries/', views_admin.admin_entries_list, name='admin_entries_list'),
    path('entries/stats/', views_admin.admin_entries_stats, name='admin_entries_stats'),
]