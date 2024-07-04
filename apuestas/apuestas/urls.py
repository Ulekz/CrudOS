from django.contrib import admin
from django.urls import path, include
from clientes import views as cliente_views
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),  # Ruta para la administración de Django
    path('', cliente_views.index, name='index'),  # Ruta para la página de inicio
    path('clientes/', include('clientes.urls')),  # Incluir las rutas del app clientes
    path('accounts/login/', cliente_views.login_cliente, name='login_cliente'),  # Ruta para el login de clientes
    path('accounts/logout/', cliente_views.logout_cliente, name='logout_cliente'),  # Ruta para el logout de clientes
    path('admin/logout/', cliente_views.logout_admin, name='logout_admin'),  # Ruta para el logout de administradores

    # Rutas para el restablecimiento de contraseñas
    path('password_reset/', 
         auth_views.PasswordResetView.as_view(template_name='registration/password_reset_form.html'), 
         name='password_reset'),
    path('password_reset/done/', 
         auth_views.PasswordResetDoneView.as_view(template_name='registration/password_reset_done.html'), 
         name='password_reset_done'),
    path('reset/<uidb64>/<token>/', 
         auth_views.PasswordResetConfirmView.as_view(template_name='registration/password_reset_confirm.html'), 
         name='password_reset_confirm'),
    path('reset/done/', 
         auth_views.PasswordResetCompleteView.as_view(template_name='registration/password_reset_complete.html'), 
         name='password_reset_complete'),

    # Rutas para la gestión de usuarios administradores
    path('admin_users_management/', cliente_views.admin_user_list, name='admin_user_list'),  # Lista de usuarios administradores
    path('admin_users_management/create/', cliente_views.admin_user_create, name='admin_user_create'),  # Crear un nuevo usuario administrador
    path('admin_users_management/<int:id>/edit/', cliente_views.admin_user_update, name='admin_user_update'),  # Editar un usuario administrador
    path('admin_users_management/<int:id>/delete/', cliente_views.admin_user_delete, name='admin_user_delete'),  # Eliminar un usuario administrador
]

# Configuración para servir archivos de medios en desarrollo
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
