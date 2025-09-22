from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'equipment', views.EquipmentViewSet)
router.register(r'reports', views.EquipmentReportViewSet)

urlpatterns = [
    path('', include(router.urls)),
]