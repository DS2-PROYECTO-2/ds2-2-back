"""
URL configuration for ds2_back project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),                           # GET - Panel de administración Django
    path('api/auth/', include('users.urls')),                  # * - Autenticación y gestión de usuarios
    path('api/rooms/', include('rooms.urls')),                 # * - Gestión de salas y entradas/salidas
    path('api/notifications/', include('notifications.urls')), # * - Sistema de notificaciones
]
