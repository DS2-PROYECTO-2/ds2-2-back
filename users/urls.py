from django.urls import path
from . import views

urlpatterns = [
    # Autenticación
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    
    # Perfil de usuario
    path('profile/', views.profile_view, name='profile'),
    path('profile/update/', views.update_profile_view, name='update_profile'),
    path('change-password/', views.change_password_view, name='change_password'),
    
    # Dashboard
    path('dashboard/', views.dashboard_view, name='dashboard'),
    
    # Administración de usuarios (solo admins)
    path('admin/users/', views.admin_users_list_view, name='admin_users_list'),
    path('admin/users/<int:user_id>/verify/', views.admin_verify_user_view, name='admin_verify_user'),

    path('admin/users/<int:user_id>/', views.admin_delete_user_view, name='admin_delete_user'),

    path('admin/users/activate/', views.admin_user_activate_via_token, name='admin_user_activate'),
    path('admin/users/delete/', views.admin_user_delete_via_token, name='admin_user_delete'),

    path('password/reset-request/', views.password_reset_request_view, name='password_reset_request'),
    path('password/reset-confirm/', views.password_reset_confirm_view, name='password_reset_confirm'),


]