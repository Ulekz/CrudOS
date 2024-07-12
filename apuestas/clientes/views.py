import json
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.views.decorators.http import require_POST
from django.db import IntegrityError
from django.http import HttpResponse
from django.contrib.auth.models import User
from .forms import ImageForm, RegistroClienteForm, ClienteForm, ApuestaForm, AdminUserForm, TarjetaForm, PublicidadForm
from django.contrib.auth.forms import AuthenticationForm
from .models import Cliente, Apuesta, Tarjeta, Publicidad, Image
import csv
import pandas as pd
import matplotlib.pyplot as plt
from io import BytesIO
import base64
from django.utils.timezone import localtime
from django.contrib import messages
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
import datetime
from django.core.mail import send_mail
from django.db.models import Sum

# Verifica si el usuario es administrador
def is_admin(user):
    return user.is_staff

# Vista principal que muestra las imágenes en la página principal
def index(request):
    images = Image.objects.all()
    images_left = Image.objects.filter(position='left')
    images_right = Image.objects.filter(position='right')
    return render(request, 'clientes/index.html', {'images': images, 'images_left': images_left, 'images_right': images_right})

# Vista del panel de administrador (requiere autenticación y ser administrador)
@login_required
@user_passes_test(is_admin)
def admin_dashboard(request):
    return render(request, 'clientes/admin_dashboard.html')

# Generar un reporte CSV con la información de los clientes (requiere autenticación y ser administrador)
@login_required
@user_passes_test(is_admin)
def generar_reporte_csv(request):
    clientes = Cliente.objects.all()
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="clientes_reporte.csv"'

    writer = csv.writer(response)
    writer.writerow(['ID', 'Nombre', 'Teléfono', 'Dirección', 'Email', 'Fecha de Registro'])

    for cliente in clientes:
        writer.writerow([cliente.id, cliente.nombre, cliente.telefono, cliente.direccion, cliente.email, localtime(cliente.fecha_registro).replace(tzinfo=None)])

    return response

# Generar un reporte Excel con la información de los clientes (requiere autenticación y ser administrador)
@login_required
@user_passes_test(is_admin)
def generar_reporte_excel(request):
    clientes = Cliente.objects.all()
    data = []
    for cliente in clientes:
        data.append({
            'ID': cliente.id,
            'Nombre': cliente.nombre,
            'Teléfono': cliente.telefono,
            'Dirección': cliente.direccion,
            'Email': cliente.email,
            'Fecha de Registro': localtime(cliente.fecha_registro).replace(tzinfo=None)
        })

    df = pd.DataFrame(data)
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename="clientes_reporte.xlsx"'

    with pd.ExcelWriter(response, engine='openpyxl') as writer:
        df.to_excel(writer, index=False)

    return response

@login_required
@user_passes_test(is_admin)
def generar_reporte_historico_apuestas(request):
    """
    Genera un reporte CSV con el historial de apuestas por cliente.

    El reporte incluye el ID del cliente, el nombre del cliente y el monto total de las apuestas
    realizadas por cada cliente.

    Args:
        request: Objeto HttpRequest que contiene información sobre la solicitud actual.

    Returns:
        HttpResponse: Respuesta HTTP que contiene el archivo CSV adjunto.
    """
    apuestas = Apuesta.objects.all()
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="historico_apuestas.csv"'

    writer = csv.writer(response)
    writer.writerow(['ID Cliente', 'Nombre Cliente', 'Monto Total de Apuestas'])

    clientes = Cliente.objects.all()
    for cliente in clientes:
        total_apuestas = apuestas.filter(cliente=cliente).aggregate(total=Sum('monto'))['total']
        if total_apuestas is None:
            total_apuestas = 0
        writer.writerow([cliente.id, cliente.get_full_name(), total_apuestas])

    return response

@login_required
@user_passes_test(is_admin)
def generar_reporte_historico_apuestas_excel(request):
    """
    Genera un reporte Excel con el historial de apuestas por cliente.

    El reporte incluye el ID del cliente, el nombre del cliente, cada una de sus apuestas con la fecha
    y el monto total de las apuestas realizadas por cada cliente.

    Args:
        request: Objeto HttpRequest que contiene información sobre la solicitud actual.

    Returns:
        HttpResponse: Respuesta HTTP que contiene el archivo Excel adjunto.
    """
    apuestas = Apuesta.objects.all()
    clientes = Cliente.objects.all()

    data = []
    for cliente in clientes:
        apuestas_cliente = apuestas.filter(cliente=cliente)
        total_apuestas = apuestas_cliente.aggregate(total=Sum('monto'))['total'] or 0
        for apuesta in apuestas_cliente:
            data.append({
                'ID Cliente': cliente.id,
                'Nombre Cliente': cliente.get_full_name(),
                'Monto de Apuesta': apuesta.monto,
                'Fecha de Apuesta': apuesta.fecha.replace(tzinfo=None),  # Eliminar la información de la zona horaria
            })
        data.append({
            'ID Cliente': '',
            'Nombre Cliente': 'Total:',
            'Monto de Apuesta': total_apuestas,
            'Fecha de Apuesta': '',
        })

    df = pd.DataFrame(data)
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename="historico_apuestas.xlsx"'

    with pd.ExcelWriter(response, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Histórico de Apuestas')

    return response

# Generar gráficas de registro de clientes (requiere autenticación y ser administrador)
def some_logic_to_check_if_recurrent(user):
    # Un cliente es recurrente si ha realizado más de una apuesta
    return Apuesta.objects.filter(cliente__user=user).count() > 1

@login_required
def graficas_cliente(request):
    cliente = Cliente.objects.get(user=request.user)
    apuestas = Apuesta.objects.filter(cliente=cliente)
    fechas_apuestas = [apuesta.fecha.date() for apuesta in apuestas]
    df = pd.DataFrame(fechas_apuestas, columns=['fecha_apuesta'])

    # Análisis de Actividad del Cliente
    df['fecha_apuesta'] = pd.to_datetime(df['fecha_apuesta'])
    df_activity = df.groupby(df['fecha_apuesta'].dt.to_period('M')).count().rename(columns={'fecha_apuesta': 'n_apuestas'})

    plt.figure(figsize=(10, 6))
    df_activity.plot(kind='line', legend=False)
    plt.title('Actividad del Cliente por Mes')
    plt.xlabel('Fecha')
    plt.ylabel('Número de Apuestas')
    plt.grid(True)
    buffer = BytesIO()
    plt.savefig(buffer, format='png')
    plt.close()
    image_activity_png = buffer.getvalue()
    buffer.close()
    graphic_activity = base64.b64encode(image_activity_png).decode('utf-8')

    return render(request, 'clientes/graficas_cliente.html', {
        'graphic_activity': graphic_activity
    })

@login_required
@user_passes_test(is_admin)
def graficas(request):
    clientes = Cliente.objects.all()
    fechas_registro = [cliente.fecha_registro.date() for cliente in clientes]
    df = pd.DataFrame(fechas_registro, columns=['fecha_registro'])

    # Análisis de Tendencias
    df['fecha_registro'] = pd.to_datetime(df['fecha_registro'])
    df_trends = df.groupby(df['fecha_registro'].dt.to_period('M')).count().rename(columns={'fecha_registro': 'registros'})

    plt.figure(figsize=(10, 6))
    df_trends.plot(kind='line', legend=False)
    plt.title('Número de Clientes Registrados por Mes')
    plt.xlabel('Fecha')
    plt.ylabel('Número de Clientes')
    plt.grid(True)
    buffer = BytesIO()
    plt.savefig(buffer, format='png')
    plt.close()
    image_trends_png = buffer.getvalue()
    buffer.close()
    graphic_trends = base64.b64encode(image_trends_png).decode('utf-8')

    # Análisis Demográfico
    df['edad'] = df.apply(lambda row: datetime.datetime.now().year - row.fecha_registro.year, axis=1)
    df_demographic = df.groupby(['sexo', 'edad']).count().unstack().fillna(0)

    plt.figure(figsize=(10, 6))
    df_demographic.plot(kind='bar', stacked=True)
    plt.title('Distribución de Clientes por Sexo y Edad')
    plt.xlabel('Edad')
    plt.ylabel('Número de Clientes')
    plt.legend(title='Sexo')
    plt.grid(True)
    buffer = BytesIO()
    plt.savefig(buffer, format='png')
    plt.close()
    image_demographic_png = buffer.getvalue()
    buffer.close()
    graphic_demographic = base64.b64encode(image_demographic_png).decode('utf-8')

    # Seguimiento del Crecimiento
    df_growth = df.groupby(df['fecha_registro'].dt.to_period('M')).count().rename(columns={'fecha_registro': 'registros'}).cumsum()
    plt.figure(figsize=(10, 6))
    df_growth.plot(kind='line', legend=False)
    plt.title('Crecimiento de la Base de Clientes por Mes')
    plt.xlabel('Fecha')
    plt.ylabel('Total de Clientes')
    plt.grid(True)
    buffer = BytesIO()
    plt.savefig(buffer, format='png')
    plt.close()
    image_growth_png = buffer.getvalue()
    buffer.close()
    graphic_growth = base64.b64encode(image_growth_png).decode('utf-8')

    # Detección de Caídas
    df_drops = df.groupby(df['fecha_registro'].dt.to_period('M')).count().rename(columns={'fecha_registro': 'registros'})
    df_drops['dif'] = df_drops['registros'].diff()
    plt.figure(figsize=(10, 6))
    df_drops['dif'].plot(kind='bar', legend=False)
    plt.title('Diferencia en Registros de Clientes por Mes')
    plt.xlabel('Fecha')
    plt.ylabel('Cambio en Número de Clientes')
    plt.grid(True)
    buffer = BytesIO()
    plt.savefig(buffer, format='png')
    plt.close()
    image_drops_png = buffer.getvalue()
    buffer.close()
    graphic_drops = base64.b64encode(image_drops_png).decode('utf-8')

    # Análisis de Retención
    df['user'] = df.index.map(lambda i: clientes[i].user.id)  # Obtener los IDs de usuario de los clientes
    df['es_recurrente'] = df['user'].apply(some_logic_to_check_if_recurrent)
    df_retention = df.groupby(['fecha_registro', 'es_recurrente']).count().unstack().fillna(0)
    plt.figure(figsize=(10, 6))
    df_retention.plot(kind='bar', stacked=True)
    plt.title('Retención de Clientes por Mes')
    plt.xlabel('Fecha')
    plt.ylabel('Número de Clientes')
    plt.legend(title='Es Recurrente')
    plt.grid(True)
    buffer = BytesIO()
    plt.savefig(buffer, format='png')
    plt.close()
    image_retention_png = buffer.getvalue()
    buffer.close()
    graphic_retention = base64.b64encode(image_retention_png).decode('utf-8')

    return render(request, 'clientes/graficas.html', {
        'graphic_trends': graphic_trends,
        'graphic_demographic': graphic_demographic,
        'graphic_growth': graphic_growth,
        'graphic_drops': graphic_drops,
        'graphic_retention': graphic_retention
    })

# Lista de clientes (requiere autenticación)
@login_required
def clientes_list(request):
    if request.user.is_staff:
        clientes = Cliente.objects.all()
    else:
        clientes = Cliente.objects.filter(user=request.user)
    
    paginator = Paginator(clientes, 25)  # Mostrar 25 clientes por página
    page = request.GET.get('page')
    try:
        clientes_paged = paginator.page(page)
    except PageNotAnInteger:
        clientes_paged = paginator.page(1)
    except EmptyPage:
        clientes_paged = paginator.page(paginator.num_pages)

    return render(request, 'clientes/clientes_list.html', {'clientes': clientes_paged})

# Detalle de un cliente (requiere autenticación)
@login_required
def cliente_detail(request, id):
    cliente = get_object_or_404(Cliente, id=id)
    if request.user.is_staff or cliente.user == request.user:
        return render(request, 'clientes/cliente_detail.html', {'cliente': cliente})
    else:
        return redirect('clientes_list')

# Crear un nuevo cliente (requiere autenticación y ser administrador)
@login_required
@user_passes_test(is_admin)
def cliente_create(request):
    if request.method == 'POST':
        form = ClienteForm(request.POST)
        try:
            if form.is_valid():
                form.save()
                messages.success(request, 'Cliente creado exitosamente.')
                return redirect('clientes_list')
            else:
                messages.error(request, 'Error en el formulario. Por favor, revisa los datos.')
        except IntegrityError:
            messages.error(request, 'Error de integridad. Por favor, revisa los datos ingresados.')
    else:
        form = ClienteForm()
    return render(request, 'clientes/cliente_form.html', {'form': form})

# Actualizar un cliente (requiere autenticación)
@login_required
def cliente_update(request, id):
    cliente = get_object_or_404(Cliente, id=id)
    if request.user.is_staff or cliente.user == request.user:
        if request.method == 'POST':
            form = ClienteForm(request.POST, instance=cliente)
            if form.is_valid():
                form.save()
                messages.success(request, 'Cliente actualizado exitosamente.')
                return redirect('clientes_list')
            else:
                messages.error(request, 'Error en el formulario. Por favor, revisa los datos.')
        else:
            form = ClienteForm(instance=cliente)
        return render(request, 'clientes/cliente_form.html', {'form': form})
    else:
        return redirect('clientes_list')

# Eliminar un cliente (requiere autenticación y ser administrador)
@login_required
@user_passes_test(is_admin)
def cliente_delete(request, id):
    cliente = get_object_or_404(Cliente, id=id)
    if request.method == 'POST':
        cliente.delete()
        messages.success(request, 'Cliente eliminado exitosamente.')
        return redirect('clientes_list')
    return render(request, 'clientes/cliente_confirm_delete.html', {'cliente': cliente})

# Lista de usuarios administradores (requiere autenticación y ser administrador)
@login_required
@user_passes_test(is_admin)
def admin_user_list(request):
    users = User.objects.all()
    return render(request, 'clientes/admin_user_list.html', {'users': users})

# Crear un nuevo usuario administrador (requiere autenticación y ser administrador)
@login_required
@user_passes_test(is_admin)
def admin_user_create(request):
    if request.method == 'POST':
        form = AdminUserForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Usuario administrador creado exitosamente.')
            return redirect('admin_user_list')
        else:
            print("Formulario inválido en creación:", form.errors)
            messages.error(request, 'Error en el formulario. Por favor, revisa los datos.')
    else:
        form = AdminUserForm()
    return render(request, 'clientes/admin_user_form.html', {'form': form})

# Actualizar un usuario administrador (requiere autenticación y ser administrador)
@login_required
@user_passes_test(is_admin)
def admin_user_update(request, id):
    user = get_object_or_404(User, id=id)
    if request.method == 'POST':
        form = AdminUserForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Usuario administrador actualizado exitosamente.')
            return redirect('admin_user_list')
        else:
            print("Formulario inválido en actualización:", form.errors)
            print("Datos recibidos en actualización:", request.POST)
            messages.error(request, 'Error en el formulario. Por favor, revisa los datos.')
    else:
        form = AdminUserForm(instance=user)
    return render(request, 'clientes/admin_user_form.html', {'form': form})

# Eliminar un usuario administrador (requiere autenticación y ser administrador)
@login_required
@user_passes_test(is_admin)
def admin_user_delete(request, id):
    user = get_object_or_404(User, id=id)
    if request.method == 'POST':
        user.delete()
        messages.success(request, 'Usuario administrador eliminado exitosamente.')
        return redirect('admin_user_list')
    return render(request, 'clientes/admin_user_confirm_delete.html', {'user': user})

# Registro de clientes
def registro_cliente(request):
    if request.method == 'POST':
        form = RegistroClienteForm(request.POST)
        if form.is_valid():
            cliente = form.save()
            # Autenticar y loguear al usuario
            user = authenticate(username=form.cleaned_data['username'], password=form.cleaned_data['password1'])
            login(request, user)
            messages.success(request, 'Registro exitoso. Por favor, inicia sesión.')
            return redirect('index')  # Redirigir a la página de inicio
        else:
            messages.error(request, 'Error en el registro. Por favor, revisa el formulario.')
    else:
        form = RegistroClienteForm()
    return render(request, 'clientes/registro_cliente.html', {'form': form})

# Login para clientes
def login_cliente(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                if not user.is_staff:
                    login(request, user)
                    return redirect('index')
                else:
                    messages.error(request, 'No tienes permiso para iniciar sesión aquí.')
            else:
                messages.error(request, 'Nombre de usuario o contraseña incorrectos.')
        else:
            messages.error(request, 'Formulario inválido.')
    else:
        form = AuthenticationForm()
    return render(request, 'clientes/login_cliente.html', {'form': form})

# Login para administradores
def login_admin(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None and user.is_staff:
                login(request, user)
                return redirect('admin_dashboard')
            else:
                form.add_error(None, 'Credenciales inválidas o no tienes permiso de administrador.')
    else:
        form = AuthenticationForm()
    return render(request, 'clientes/login_admin.html', {'form': form})

# Cerrar sesión de cliente (requiere autenticación)
@login_required
@require_POST
def logout_cliente(request):
    logout(request)
    messages.success(request, 'Has cerrado sesión exitosamente.')
    return redirect('index')

# Cerrar sesión de administrador (requiere autenticación)
@login_required
@require_POST
def logout_admin(request):
    logout(request)
    messages.success(request, 'Has cerrado sesión exitosamente.')
    return redirect('index')

# Crear una nueva apuesta (requiere autenticación)
@login_required
def apuesta_create(request):
    if request.method == 'POST':
        form = ApuestaForm(request.POST)
        if form.is_valid():
            apuesta = form.save(commit=False)
            apuesta.cliente = get_object_or_404(Cliente, user=request.user)
            apuesta.save()
            messages.success(request, 'Apuesta creada exitosamente.')
            return redirect('apuestas_list')
        else:
            messages.error(request, 'Error en el formulario. Por favor, revisa los datos.')
    else:
        form = ApuestaForm()
    return render(request, 'clientes/apuesta_form.html', {'form': form})

# Lista de apuestas (requiere autenticación)
@login_required
def apuestas_list(request):
    if request.user.is_staff:
        apuestas = Apuesta.objects.all()
    else:
        cliente = get_object_or_404(Cliente, user=request.user)
        apuestas = Apuesta.objects.filter(cliente=cliente)
    
    paginator = Paginator(apuestas, 25)  # Mostrar 25 apuestas por página
    page = request.GET.get('page')
    try:
        apuestas_paged = paginator.page(page)
    except PageNotAnInteger:
        apuestas_paged = paginator.page(1)
    except EmptyPage:
        apuestas_paged = paginator.page(paginator.num_pages)

    return render(request, 'clientes/apuestas_list.html', {'apuestas': apuestas_paged})

# Perfil del cliente (requiere autenticación)
@login_required
def perfil_cliente(request):
    cliente = get_object_or_404(Cliente, user=request.user)
    if request.method == 'POST':
        form = ClienteForm(request.POST, instance=cliente)
        if form.is_valid():
            form.save()
            messages.success(request, 'Perfil actualizado exitosamente.')
            return redirect('perfil_cliente')
        else:
            print("Formulario inválido:", form.errors)
            print("Datos recibidos:", request.POST)
            messages.error(request, 'Error en el formulario. Por favor, revisa los datos.')
    else:
        form = ClienteForm(instance=cliente)
    return render(request, 'clientes/perfil_cliente.html', {'form': form})

# Historial de apuestas del cliente (requiere autenticación)
@login_required
def historial_apuestas(request):
    cliente = get_object_or_404(Cliente, user=request.user)
    apuestas = Apuesta.objects.filter(cliente=cliente)
    return render(request, 'clientes/historial_apuestas.html', {'apuestas': apuestas})

# Lista de apuestas del cliente (requiere autenticación)
@login_required
def mis_apuestas(request):
    cliente = get_object_or_404(Cliente, user=request.user)
    apuestas = Apuesta.objects.filter(cliente=cliente)
    return render(request, 'clientes/mis_apuestas.html', {'apuestas': apuestas})

# Lista de tarjetas (requiere autenticación y ser administrador)
@login_required
@user_passes_test(is_admin)
def listar_tarjetas(request):
    tarjetas = Tarjeta.objects.all()
    return render(request, 'clientes/listar_tarjetas.html', {'tarjetas': tarjetas})

# Lista de tarjetas del cliente (requiere autenticación)
@login_required
def listar_tarjetas_cliente(request):
    cliente = get_object_or_404(Cliente, user=request.user)
    tarjetas = Tarjeta.objects.filter(cliente=cliente)
    return render(request, 'clientes/listar_tarjetas_cliente.html', {'tarjetas': tarjetas})

# Agregar una nueva tarjeta (requiere autenticación)
@login_required
def agregar_tarjeta(request):
    if request.method == 'POST':
        form = TarjetaForm(request.POST)
        if form.is_valid():
            tarjeta = form.save(commit=False)
            tarjeta.cliente = get_object_or_404(Cliente, user=request.user)
            tarjeta.save()
            messages.success(request, 'Tarjeta agregada exitosamente.')
            return redirect('listar_tarjetas_cliente')
        else:
            messages.error(request, 'Error en el formulario. Por favor, revisa los datos.')
    else:
        form = TarjetaForm()
    return render(request, 'clientes/agregar_tarjeta.html', {'form': form})

# Editar una tarjeta (requiere autenticación y ser administrador)
@login_required
@user_passes_test(is_admin)
def editar_tarjeta(request, id):
    tarjeta = get_object_or_404(Tarjeta, id=id)
    if request.method == 'POST':
        form = TarjetaForm(request.POST, instance=tarjeta)
        if form.is_valid():
            form.save()
            messages.success(request, 'Tarjeta actualizada exitosamente.')
            return redirect('listar_tarjetas')
        else:
            messages.error(request, 'Error en el formulario. Por favor, revisa los datos.')
    else:
        form = TarjetaForm(instance=tarjeta)
    return render(request, 'clientes/agregar_tarjeta.html', {'form': form})

# Eliminar una tarjeta (requiere autenticación y ser administrador)
@login_required
@user_passes_test(is_admin)
def eliminar_tarjeta(request, id):
    tarjeta = get_object_or_404(Tarjeta, id=id)
    if request.method == 'POST':
        tarjeta.delete()
        messages.success(request, 'Tarjeta eliminada exitosamente.')
        return redirect('listar_tarjetas')
    return render(request, 'clientes/eliminar_tarjeta.html', {'tarjeta': tarjeta})

# Lista de publicidades (requiere autenticación y ser administrador)
@login_required
@user_passes_test(lambda u: u.is_staff)
def lista_publicidad(request):
    publicidades_izquierda = Publicidad.objects.filter(posicion='izquierda')
    publicidades_derecha = Publicidad.objects.filter(posicion='derecha')
    return render(request, 'clientes/lista_publicidad.html', {
        'publicidades_izquierda': publicidades_izquierda,
        'publicidades_derecha': publicidades_derecha
    })

# Agregar una nueva publicidad (requiere autenticación y ser administrador)
@login_required
@user_passes_test(lambda u: u.is_staff)
def agregar_publicidad(request):
    if request.method == 'POST':
        form = PublicidadForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Publicidad agregada exitosamente.')
            return redirect('lista_publicidad')
        else:
            messages.error(request, 'Error en el formulario. Por favor, revisa los datos.')
    else:
        form = PublicidadForm()
    return render(request, 'clientes/agregar_publicidad.html', {'form': form})

# Editar una publicidad (requiere autenticación y ser administrador)
@login_required
@user_passes_test(lambda u: u.is_staff)
def editar_publicidad(request, id):
    publicidad = get_object_or_404(Publicidad, id=id)
    if request.method == 'POST':
        form = PublicidadForm(request.POST, request.FILES, instance=publicidad)
        if form.is_valid():
            form.save()
            messages.success(request, 'Publicidad actualizada exitosamente.')
            return redirect('lista_publicidad')
        else:
            messages.error(request, 'Error en el formulario. Por favor, revisa los datos.')
    else:
        form = PublicidadForm(instance=publicidad)
    return render(request, 'clientes/editar_publicidad.html', {'form': form})

# Eliminar una publicidad (requiere autenticación y ser administrador)
@login_required
@user_passes_test(lambda u: u.is_staff)
def eliminar_publicidad(request, id):
    publicidad = get_object_or_404(Publicidad, id=id)
    if request.method == 'POST':
        publicidad.delete()
        messages.success(request, 'Publicidad eliminada exitosamente.')
        return redirect('lista_publicidad')
    return render(request, 'clientes/eliminar_publicidad.html', {'publicidad': publicidad})

# Subir una imagen (requiere autenticación)
@login_required
def upload_image(request):
    if request.method == 'POST':
        form = ImageForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Imagen subida exitosamente.')
            return redirect('manage_images')
        else:
            messages.error(request, 'Error en el formulario. Por favor, revisa los datos.')
    else:
        form = ImageForm()
    return render(request, 'clientes/upload_image.html', {'form': form})

# Gestionar imágenes (requiere autenticación)
@login_required
def manage_images(request):
    images = Image.objects.all()
    return render(request, 'clientes/manage_images.html', {'images': images})

# Eliminar una imagen (requiere autenticación)
@login_required
def delete_image(request, image_id):
    image = get_object_or_404(Image, id=image_id)
    image.delete()
    messages.success(request, 'Imagen eliminada exitosamente.')
    return redirect('manage_images')

def acerca_de(request):
    return render(request, 'clientes/acerca_de.html')

def mision(request):
    return render(request, 'clientes/mision.html')

def vision(request):
    return render(request, 'clientes/vision.html')

def soporte_tecnico(request):
    if request.method == 'POST':
        nombre = request.POST['nombre']
        email = request.POST['email']
        mensaje = request.POST['mensaje']
        # Enviar correo electrónico (configura tus ajustes de correo en settings.py)
        send_mail(
            f'Soporte Técnico - {nombre}',
            mensaje,
            email,
            ['soporte@CrudOS.com'],
            fail_silently=False,
        )
        messages.success(request, 'Tu mensaje ha sido enviado exitosamente.')
    return render(request, 'clientes/soporte_tecnico.html')

        
