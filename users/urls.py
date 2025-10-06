from django.urls import path
from . import views

urlpatterns = [
    # Autenticación
    path('register/', views.register_view, name='register'),                                        # POST - Registrar nuevo usuario
    path('login/', views.login_view, name='login'),                                                  # POST - Iniciar sesión
    path('logout/', views.logout_view, name='logout'),                                               # POST - Cerrar sesión
    
    # Perfil de usuario
    path('profile/', views.profile_view, name='profile'),                                            # GET - Ver perfil actual
    path('profile/update/', views.update_profile_view, name='update_profile'),                      # PUT/PATCH - Actualizar perfil
    path('change-password/', views.change_password_view, name='change_password'),                   # POST - Cambiar contraseña
    
    # Dashboard
    path('dashboard/', views.dashboard_view, name='dashboard'),                                      # GET - Panel principal del usuario
    
    # Administración de usuarios (solo admins)
    path('admin/users/', views.admin_users_list_view, name='admin_users_list'),                     # GET - Listar todos los usuarios
    path('admin/users/<int:user_id>/verify/', views.admin_verify_user_view, name='admin_verify_user'), # POST - Verificar usuario

    path('admin/users/<int:user_id>/', views.admin_delete_user_view, name='admin_delete_user'),     # DELETE - Eliminar usuario

    path('admin/users/activate/', views.admin_user_activate_via_token, name='admin_user_activate'), # POST - Activar usuario con token
    path('admin/users/delete/', views.admin_user_delete_via_token, name='admin_user_delete'),       # POST - Eliminar usuario con token

    path('password/reset-request/', views.password_reset_request_view, name='password_reset_request'), # POST - Solicitar reset de contraseña
    path('password/reset-confirm/', views.password_reset_confirm_view, name='password_reset_confirm'), # POST - Confirmar reset de contraseña


]