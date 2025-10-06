from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'schedules', views.ScheduleViewSet, basename='schedule')  # CRUD de horarios

urlpatterns = [
    path('', include(router.urls)),  # GET/POST/PUT/PATCH/DELETE - CRUD de horarios
    # Rutas generadas automáticamente:
    # GET /schedules/ - Listar horarios
    # POST /schedules/ - Crear horario
    # GET /schedules/{id}/ - Detalle de horario
    # PUT/PATCH /schedules/{id}/ - Actualizar horario
    # DELETE /schedules/{id}/ - Eliminar horario
]