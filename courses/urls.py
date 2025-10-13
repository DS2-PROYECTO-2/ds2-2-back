from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CourseViewSet, admin_courses_overview_view

# Router para el ViewSet
router = DefaultRouter()
router.register(r'courses', CourseViewSet, basename='course')

urlpatterns = [
    # Incluir rutas del ViewSet
    path('', include(router.urls)),
    
    # Vista adicional para administradores
    path('admin/courses/overview/', admin_courses_overview_view, name='admin-courses-overview'),
]

# Rutas generadas automáticamente por el ViewSet:
# GET    /courses/                  - Listar cursos
# POST   /courses/                  - Crear curso (solo admin)
# GET    /courses/{id}/             - Detalle de curso
# PUT    /courses/{id}/             - Actualizar curso (solo admin)
# PATCH  /courses/{id}/             - Actualizar parcial (solo admin)
# DELETE /courses/{id}/             - Eliminar curso (solo admin)
# GET    /courses/my_courses/       - Cursos del monitor autenticado
# GET    /courses/upcoming/         - Cursos próximos (7 días)
# GET    /courses/current/          - Cursos actuales
# GET    /courses/{id}/history/     - Historial de cambios del curso