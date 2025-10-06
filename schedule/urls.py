from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'schedules', views.ScheduleViewSet, basename='schedule')  # CRUD de turnos (solo admins)

urlpatterns = [
    # CRUD de turnos para administradores
    path('', include(router.urls)),                                            # GET/POST/PUT/PATCH/DELETE - CRUD completo de turnos
    
    # Endpoints específicos para monitores
    path('my-schedules/', views.monitor_schedules_view, name='monitor_schedules'),              # GET - Turnos del monitor autenticado
    path('my-current-schedule/', views.monitor_current_schedule_view, name='monitor_current'),  # GET - Turno actual del monitor
    
    # Endpoints específicos para administradores
    path('admin/overview/', views.admin_schedules_overview_view, name='admin_schedules_overview'), # GET - Resumen general para admins
    
    # Rutas del ViewSet generadas automáticamente:
    # GET /schedules/ - Listar turnos
    # POST /schedules/ - Crear turno (solo admins)
    # GET /schedules/{id}/ - Detalle de turno
    # PUT/PATCH /schedules/{id}/ - Actualizar turno (solo admins)
    # DELETE /schedules/{id}/ - Eliminar turno (solo admins)
    # GET /schedules/upcoming/ - Turnos próximos (acción personalizada)
    # GET /schedules/current/ - Turnos actuales (acción personalizada)
]