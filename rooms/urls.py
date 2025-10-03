from django.urls import path
from . import views

urlpatterns = [
    # Gestión de salas (Sprint 1)
    path('', views.room_list_view, name='room_list'),
    path('<int:room_id>/', views.room_detail_view, name='room_detail'),
    path('<int:room_id>/occupants/', views.room_current_occupants_view, name='room_occupants'),
    
    # Registro de entrada/salida (Sprint 2)
    path('entry/', views.room_entry_create_view, name='room_entry_create'),
    path('entry/<int:entry_id>/exit/', views.room_entry_exit_view, name='room_entry_exit'),
    
    # Historial del usuario
    path('my-entries/', views.user_room_entries_view, name='user_room_entries'),
    path('my-active-entry/', views.user_active_entry_view, name='user_active_entry'),
]