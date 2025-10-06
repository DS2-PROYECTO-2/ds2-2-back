from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'reports', views.ReportViewSet, basename='report')  # CRUD de reportes generales

urlpatterns = [
    path('', include(router.urls)),                                     # GET/POST/PUT/PATCH/DELETE - CRUD de reportes
    path('generate/', views.generate_report, name='generate-report'),   # POST - Generar nuevo reporte
    # Rutas generadas automáticamente:
    # GET /reports/ - Listar reportes
    # POST /reports/ - Crear reporte
    # GET /reports/{id}/ - Detalle de reporte
    # PUT/PATCH /reports/{id}/ - Actualizar reporte
    # DELETE /reports/{id}/ - Eliminar reporte
]