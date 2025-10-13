from django.urls import path
from . import views

urlpatterns = [
    # Dashboard principal
    path('', views.dashboard_view, name='dashboard'),
    
    # Componentes del dashboard
    path('mini-cards/', views.mini_cards_view, name='mini_cards'),
    path('stats/', views.stats_view, name='stats'),
    path('alerts/', views.alerts_view, name='alerts'),
    path('charts/', views.charts_data_view, name='charts_data'),
    
    # Vista administrativa
    path('admin/overview/', views.admin_overview_view, name='admin_overview'),
]


from django.urls import path
from . import views

urlpatterns = [
    # Dashboard principal
    path('', views.dashboard_view, name='dashboard'),
    
    # Componentes del dashboard
    path('mini-cards/', views.mini_cards_view, name='mini_cards'),
    path('stats/', views.stats_view, name='stats'),
    path('alerts/', views.alerts_view, name='alerts'),
    path('charts/', views.charts_data_view, name='charts_data'),
    
    # Vista administrativa
    path('admin/overview/', views.admin_overview_view, name='admin_overview'),
]


