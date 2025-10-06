from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views, views_simple

router = DefaultRouter()
router.register(r'notifications', views.NotificationViewSet, basename='notification')

urlpatterns = [
    path('', include(router.urls)),
    # URLs que el frontend espera
    path('list/', views_simple.notifications_list, name='notifications-list'),
    path('unread/', views_simple.notifications_unread, name='notifications-unread'),
    path('unread-count/', views_simple.notifications_unread_count, name='notifications-unread-count'),
    path('summary/', views_simple.notifications_summary, name='notifications-summary'),
    path('mark-all-read/', views_simple.notifications_mark_all_read, name='notifications-mark-all-read'),
    path('<int:notification_id>/mark-read/', views_simple.notifications_mark_read, name='notifications-mark-read'),
]