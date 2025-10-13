from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views, views_simple

router = DefaultRouter()
router.register(r'notifications', views.NotificationViewSet, basename='notification')

urlpatterns = [
    path('', include(router.urls)),                            # CRUD de notificaciones (solo admins)
    # URLs que el frontend espera
    path('list/', views_simple.notifications_list, name='notifications-list'),  # GET - Listar notificaciones del usuario autenticado
    path('unread/', views_simple.notifications_unread, name='notifications-unread'),   # GET - Listar notificaciones no leídas del usuario autenticado
    path('unread-count/', views_simple.notifications_unread_count, name='notifications-unread-count'), # GET - Contar notificaciones no leídas
    path('summary/', views_simple.notifications_summary, name='notifications-summary'), # GET - Resumen de notificaciones del usuario autenticado 
    path('mark-all-read/', views_simple.notifications_mark_all_read, name='notifications-mark-all-read'),  # POST - Marcar todas las notificaciones como leídas
    path('<int:notification_id>/mark-read/', views_simple.notifications_mark_read, name='notifications-mark-read'), # POST - Marcar una notificación específica como leída

    #notifications/ - CRUD de notificaciones (solo admins)
    path('notifications/', include(router.urls)),
    # Rutas del ViewSet generadas automáticamente:
    # GET /notifications/ - Listar notificaciones (solo admins)
    # POST /notifications/ - Crear notificación (solo admins)
    # GET /notifications/{id}/ - Detalle de notificación (solo admins)
    # PUT/PATCH /notifications/{id}/ - Actualizar notificación (solo admins)
    # DELETE /notifications/{id}/ - Eliminar notificación (solo admins)
]