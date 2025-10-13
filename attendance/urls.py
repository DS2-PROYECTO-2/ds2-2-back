from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'attendances', views.AttendanceViewSet)   # CRUD de registros de asistencia
router.register(r'incapacities', views.IncapacityViewSet)  # CRUD de incapacidades

urlpatterns = [
    path('', include(router.urls)),  # GET/POST/PUT/PATCH/DELETE - CRUD de asistencia e incapacidades
    # Rutas generadas automáticamente:
    # GET /attendances/ - Listar asistencias
    # POST /attendances/ - Crear asistencia
    # GET /attendances/{id}/ - Detalle de asistencia
    # PUT/PATCH /attendances/{id}/ - Actualizar asistencia
    # DELETE /attendances/{id}/ - Eliminar asistencia
    # GET /incapacities/ - Listar incapacidades
    # POST /incapacities/ - Crear incapacidad
    # GET /incapacities/{id}/ - Detalle de incapacidad
    # PUT/PATCH /incapacities/{id}/ - Actualizar incapacidad
    # DELETE /incapacities/{id}/ - Eliminar incapacidad
]

