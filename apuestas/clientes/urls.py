from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),  # Ruta para la página principal
    path('clientes/', views.clientes_list, name='clientes_list'),  # Lista de clientes
    path('cliente/<int:id>/', views.cliente_detail, name='cliente_detail'),  # Detalle de un cliente
    path('cliente/nuevo/', views.cliente_create, name='cliente_create'),  # Crear un nuevo cliente
    path('cliente/<int:id>/editar/', views.cliente_update, name='cliente_update'),  # Editar un cliente existente
    path('cliente/<int:id>/eliminar/', views.cliente_delete, name='cliente_delete'),  # Eliminar un cliente
    path('registro_cliente/', views.registro_cliente, name='registro_cliente'),  # Registro de nuevos clientes
    path('login_cliente/', views.login_cliente, name='login_cliente'),  # Login de clientes
    path('login_admin/', views.login_admin, name='login_admin'),  # Login de administradores
    path('logout_cliente/', views.logout_cliente, name='logout_cliente'),  # Logout de clientes
    path('logout_admin/', views.logout_admin, name='logout_admin'),  # Logout de administradores
    path('apuestas/', views.apuestas_list, name='apuestas_list'),  # Lista de apuestas
    path('apuesta/nueva/', views.apuesta_create, name='apuesta_create'),  # Crear una nueva apuesta
    path('perfil/', views.perfil_cliente, name='perfil_cliente'),  # Perfil del cliente
    path('historial/', views.historial_apuestas, name='historial_apuestas'),  # Historial de apuestas del cliente
    path('admin_dashboard/', views.admin_dashboard, name='admin_dashboard'),  # Panel de control del administrador
    path('reporte/csv/', views.generar_reporte_csv, name='generar_reporte_csv'),  # Generar reporte en formato CSV
    path('reporte/excel/', views.generar_reporte_excel, name='generar_reporte_excel'),  # Generar reporte en formato Excel
    path('graficas/', views.graficas, name='graficas'),  # Generar gráficas
    path('graficas_cliente/', views.graficas_cliente, name='graficas_cliente'), #Graficas Cliente
    path('mis_apuestas/', views.mis_apuestas, name='mis_apuestas'),  # Lista de apuestas del cliente
    path('admin/users_management/', views.admin_user_list, name='admin_user_list'),  # Lista de usuarios administradores
    path('admin/users_management/create/', views.admin_user_create, name='admin_user_create'),  # Crear un nuevo usuario administrador
    path('admin/users_management/<int:id>/edit/', views.admin_user_update, name='admin_user_update'),  # Editar un usuario administrador
    path('admin/users_management/<int:id>/delete/', views.admin_user_delete, name='admin_user_delete'),  # Eliminar un usuario administrador
    path('tarjeta/nueva/', views.agregar_tarjeta, name='agregar_tarjeta'),  # Agregar una nueva tarjeta
    path('tarjetas/', views.listar_tarjetas_cliente, name='listar_tarjetas_cliente'),  # Lista de tarjetas del cliente
    path('admin/tarjetas/', views.listar_tarjetas, name='listar_tarjetas'),  # Lista de tarjetas para administradores
    path('tarjeta/<int:id>/editar/', views.editar_tarjeta, name='editar_tarjeta'),  # Editar una tarjeta
    path('tarjeta/<int:id>/eliminar/', views.eliminar_tarjeta, name='eliminar_tarjeta'),  # Eliminar una tarjeta
    path('publicidad/', views.lista_publicidad, name='lista_publicidad'),  # Lista de publicidades
    path('publicidad/nueva/', views.agregar_publicidad, name='agregar_publicidad'),  # Agregar una nueva publicidad
    path('publicidad/<int:id>/editar/', views.editar_publicidad, name='editar_publicidad'),  # Editar una publicidad
    path('publicidad/<int:id>/eliminar/', views.eliminar_publicidad, name='eliminar_publicidad'),  # Eliminar una publicidad
    path('upload-image/', views.upload_image, name='upload_image'),  # Subir una imagen
    path('manage-images/', views.manage_images, name='manage_images'),  # Gestionar imágenes
    path('delete-image/<int:image_id>/', views.delete_image, name='delete_image'),  # Eliminar una imagen
    path('acerca_de/', views.acerca_de, name='acerca_de'),
    path('mision/', views.mision, name='mision'),
    path('vision/', views.vision, name='vision'),
    path('soporte_tecnico/', views.soporte_tecnico, name='soporte_tecnico'),
]
