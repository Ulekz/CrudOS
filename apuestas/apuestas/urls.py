from django.contrib import admin
from django.urls import path, include
from clientes import views as cliente_views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('clientes.urls')),
    path('accounts/login/', cliente_views.login_cliente, name='login_cliente'),
    path('accounts/logout/', cliente_views.logout_cliente, name='logout_cliente'),
    path('admin/logout/', cliente_views.logout_admin, name='logout_admin'),
    path('password_reset/', auth_views.PasswordResetView.as_view(template_name='registration/password_reset_form.html'), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(template_name='registration/password_reset_done.html'), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='registration/password_reset_confirm.html'), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(template_name='registration/password_reset_complete.html'), name='password_reset_complete'),
    path('admin_users_management/', cliente_views.admin_user_list, name='admin_user_list'),
    path('admin_users_management/create/', cliente_views.admin_user_create, name='admin_user_create'),
    path('admin_users_management/<int:id>/edit/', cliente_views.admin_user_update, name='admin_user_update'),
    path('admin_users_management/<int:id>/delete/', cliente_views.admin_user_delete, name='admin_user_delete'),
]
