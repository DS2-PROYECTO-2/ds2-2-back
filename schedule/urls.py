from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'schedules', views.ScheduleViewSet, basename='schedule')

urlpatterns = [
    path('', include(router.urls)),
]