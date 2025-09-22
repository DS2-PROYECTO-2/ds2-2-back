from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'attendances', views.AttendanceViewSet)
router.register(r'incapacities', views.IncapacityViewSet)

urlpatterns = [
    path('', include(router.urls)),
]