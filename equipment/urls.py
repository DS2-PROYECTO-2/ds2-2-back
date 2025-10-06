from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'equipment', views.EquipmentViewSet)         # CRUD de equipos
router.register(r'reports', views.EquipmentReportViewSet)     # CRUD de reportes de equipos

urlpatterns = [
    path('', include(router.urls)),  # GET/POST/PUT/PATCH/DELETE - CRUD de equipos y reportes
    # Rutas generadas automáticamente:
    # GET /equipment/ - Listar equipos
    # POST /equipment/ - Crear equipo
    # GET /equipment/{id}/ - Detalle de equipo
    # PUT/PATCH /equipment/{id}/ - Actualizar equipo
    # DELETE /equipment/{id}/ - Eliminar equipo
    # GET /reports/ - Listar reportes de equipos
    # POST /reports/ - Crear reporte de equipo
    # GET /reports/{id}/ - Detalle de reporte
    # PUT/PATCH /reports/{id}/ - Actualizar reporte
    # DELETE /reports/{id}/ - Eliminar reporte
]