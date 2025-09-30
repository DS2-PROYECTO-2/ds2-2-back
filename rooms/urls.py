from django.urls import path
from . import views

urlpatterns = [
    # Gestión de salas (Sprint 1)
    path('', views.room_list_view, name='room_list'),
    path('<int:room_id>/', views.room_detail_view, name='room_detail'),
]