from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'notifications', views.NotificationViewSet, basename='notification')  # CRUD completo de notificaciones

urlpatterns = [
    path('', include(router.urls)),  # GET/POST/PUT/PATCH/DELETE - CRUD de notificaciones
    # Rutas generadas automáticamente:
    # GET /notifications/ - Listar notificaciones
    # POST /notifications/ - Crear notificación  
    # GET /notifications/{id}/ - Detalle de notificación
    # PUT/PATCH /notifications/{id}/ - Actualizar notificación
    # DELETE /notifications/{id}/ - Eliminar notificación
]