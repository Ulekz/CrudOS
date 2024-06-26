from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.views.decorators.http import require_POST
from django.db import IntegrityError
from django.http import HttpResponse
from django.contrib.auth.models import User
from .forms import RegistroClienteForm, ClienteForm, ApuestaForm, AdminUserForm, TarjetaForm, PublicidadForm
from django.contrib.auth.forms import AuthenticationForm
from .models import Cliente, Apuesta, Tarjeta, Publicidad
import csv
import pandas as pd
import matplotlib.pyplot as plt
from io import BytesIO
import base64
from django.utils.timezone import localtime
from django.contrib import messages
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

# Create your views here.

def is_admin(user):
    return user.is_staff

def index(request):
    publicidades_izquierda = Publicidad.objects.filter(titulo="Izquierda")
    publicidades_derecha = Publicidad.objects.filter(titulo="Derecha")
    return render(request, 'clientes/index.html', {
        'publicidades_izquierda': publicidades_izquierda,
        'publicidades_derecha': publicidades_derecha
    })


@login_required
@user_passes_test(is_admin)
def admin_dashboard(request):
    return render(request, 'clientes/admin_dashboard.html')

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
def graficas(request):
    clientes = Cliente.objects.all()
    fechas_registro = [cliente.fecha_registro.date() for cliente in clientes]
    fechas = list(set(fechas_registro))
    fechas.sort()
    conteo_clientes = [fechas_registro.count(fecha) for fecha in fechas]

    plt.figure(figsize=(10, 6))
    plt.plot(fechas, conteo_clientes, marker='o')
    plt.title('Número de Clientes Registrados por Fecha')
    plt.xlabel('Fecha')
    plt.ylabel('Número de Clientes')
    plt.grid(True)

    buffer = BytesIO()
    plt.savefig(buffer, format='png')
    plt.close()
    image_png = buffer.getvalue()
    buffer.close()
    graphic = base64.b64encode(image_png)
    graphic = graphic.decode('utf-8')

    return render(request, 'clientes/graficas.html', {'graphic': graphic})

@login_required
def clientes_list(request):
    if request.user.is_staff:
        clientes = Cliente.objects.all()
    else:
        clientes = Cliente.objects.filter(user=request.user)
    
    paginator = Paginator(clientes, 25)  # Mostrar 25 clientes por página.
    page = request.GET.get('page')
    try:
        clientes_paged = paginator.page(page)
    except PageNotAnInteger:
        clientes_paged = paginator.page(1)
    except EmptyPage:
        clientes_paged = paginator.page(paginator.num_pages)

    return render(request, 'clientes/clientes_list.html', {'clientes': clientes_paged})

@login_required
def cliente_detail(request, id):
    cliente = get_object_or_404(Cliente, id=id)
    if request.user.is_staff or cliente.user == request.user:
        return render(request, 'clientes/cliente_detail.html', {'cliente': cliente})
    else:
        return redirect('clientes_list')

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


@login_required
def cliente_update(request, id):
    cliente = get_object_or_404(Cliente, id=id)
    if request.user.is_staff or cliente.user == request.user:
        if request.method == 'POST':
            form = ClienteForm(request.POST, instance=cliente)
            if form.is_valid():
                form.save()
                return redirect('clientes_list')
        else:
            form = ClienteForm(instance=cliente)
        return render(request, 'clientes/cliente_form.html', {'form': form})
    else:
        return redirect('clientes_list')

@login_required
@user_passes_test(is_admin)
def cliente_delete(request, id):
    cliente = get_object_or_404(Cliente, id=id)
    if request.method == 'POST':
        cliente.delete()
        return redirect('clientes_list')
    return render(request, 'clientes/cliente_confirm_delete.html', {'cliente': cliente})

@login_required
@user_passes_test(is_admin)
def admin_user_list(request):
    users = User.objects.all()
    return render(request, 'clientes/admin_user_list.html', {'users': users})

@login_required
@user_passes_test(is_admin)
def admin_user_create(request):
    if request.method == 'POST':
        form = AdminUserForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('admin_user_list')
    else:
        form = AdminUserForm()
    return render(request, 'clientes/admin_user_form.html', {'form': form})

@login_required
@user_passes_test(is_admin)
def admin_user_update(request, id):
    user = get_object_or_404(User, id=id)
    if request.method == 'POST':
        form = AdminUserForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            return redirect('admin_user_list')
    else:
        form = AdminUserForm(instance=user)
    return render(request, 'clientes/admin_user_form.html', {'form': form})

@login_required
@user_passes_test(is_admin)
def admin_user_delete(request, id):
    user = get_object_or_404(User, id=id)
    if request.method == 'POST':
        user.delete()
        return redirect('admin_user_list')
    return render(request, 'clientes/admin_user_confirm_delete.html', {'user': user})

def registro_cliente(request):
    if request.method == 'POST':
        form = RegistroClienteForm(request.POST)
        if form.is_valid():
            cliente = form.save()
            messages.success(request, 'Registro exitoso. Por favor, inicia sesión.')
            return redirect('login_cliente')
        else:
            messages.error(request, 'Error en el registro. Por favor, revisa el formulario.')
    else:
        form = RegistroClienteForm()
    return render(request, 'clientes/registro_cliente.html', {'form': form})

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

@login_required
@require_POST
def logout_cliente(request):
    logout(request)
    return redirect('index')

@login_required
@require_POST
def logout_admin(request):
    logout(request)
    return redirect('index')

@login_required
def apuesta_create(request):
    if request.method == 'POST':
        form = ApuestaForm(request.POST)
        if form.is_valid():
            apuesta = form.save(commit=False)
            apuesta.cliente = get_object_or_404(Cliente, user=request.user)
            apuesta.save()
            return redirect('apuestas_list')
    else:
        form = ApuestaForm()
    return render(request, 'clientes/apuesta_form.html', {'form': form})

@login_required
def apuestas_list(request):
    if request.user.is_staff:
        apuestas = Apuesta.objects.all()
    else:
        cliente = get_object_or_404(Cliente, user=request.user)
        apuestas = Apuesta.objects.filter(cliente=cliente)
    return render(request, 'clientes/apuestas_list.html', {'apuestas': apuestas})

@login_required
def perfil_cliente(request):
    cliente = get_object_or_404(Cliente, user=request.user)
    if request.method == 'POST':
        form = ClienteForm(request.POST, instance=cliente)
        if form.is_valid():
            form.save()
            return redirect('perfil_cliente')
    else:
        form = ClienteForm(instance=cliente)
    return render(request, 'clientes/perfil_cliente.html', {'form': form})

@login_required
def historial_apuestas(request):
    cliente = get_object_or_404(Cliente, user=request.user)
    apuestas = Apuesta.objects.filter(cliente=cliente)
    return render(request, 'clientes/historial_apuestas.html', {'apuestas': apuestas})

@login_required
def mis_apuestas(request):
    cliente = get_object_or_404(Cliente, user=request.user)
    apuestas = Apuesta.objects.filter(cliente=cliente)
    return render(request, 'clientes/mis_apuestas.html', {'apuestas': apuestas})

@login_required
@user_passes_test(is_admin)
def listar_tarjetas(request):
    tarjetas = Tarjeta.objects.all()
    return render(request, 'clientes/listar_tarjetas.html', {'tarjetas': tarjetas})

@login_required
def listar_tarjetas_cliente(request):
    cliente = get_object_or_404(Cliente, user=request.user)
    tarjetas = Tarjeta.objects.filter(cliente=cliente)
    return render(request, 'clientes/listar_tarjetas_cliente.html', {'tarjetas': tarjetas})

@login_required
def agregar_tarjeta(request):
    if request.method == 'POST':
        form = TarjetaForm(request.POST)
        if form.is_valid():
            tarjeta = form.save(commit=False)
            tarjeta.cliente = get_object_or_404(Cliente, user=request.user)
            tarjeta.save()
            return redirect('listar_tarjetas_cliente')
    else:
        form = TarjetaForm()
    return render(request, 'clientes/agregar_tarjeta.html', {'form': form})

@login_required
@user_passes_test(is_admin)
def editar_tarjeta(request, id):
    tarjeta = get_object_or_404(Tarjeta, id=id)
    if request.method == 'POST':
        form = TarjetaForm(request.POST, instance=tarjeta)
        if form.is_valid():
            form.save()
            return redirect('listar_tarjetas')
    else:
        form = TarjetaForm(instance=tarjeta)
    return render(request, 'clientes/agregar_tarjeta.html', {'form': form})

@login_required
@user_passes_test(is_admin)
def eliminar_tarjeta(request, id):
    tarjeta = get_object_or_404(Tarjeta, id=id)
    if request.method == 'POST':
        tarjeta.delete()
        return redirect('listar_tarjetas')
    return render(request, 'clientes/eliminar_tarjeta.html', {'tarjeta': tarjeta})

@login_required
@user_passes_test(lambda u: u.is_staff)
def lista_publicidad(request):
    publicidades_izquierda = Publicidad.objects.filter(posicion='izquierda')
    publicidades_derecha = Publicidad.objects.filter(posicion='derecha')
    return render(request, 'clientes/lista_publicidad.html', {
        'publicidades_izquierda': publicidades_izquierda,
        'publicidades_derecha': publicidades_derecha
    })

@login_required
@user_passes_test(lambda u: u.is_staff)
def agregar_publicidad(request):
    if request.method == 'POST':
        form = PublicidadForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('lista_publicidad')
    else:
        form = PublicidadForm()
    return render(request, 'clientes/agregar_publicidad.html', {'form': form})

@login_required
@user_passes_test(lambda u: u.is_staff)
def editar_publicidad(request, id):
    publicidad = get_object_or_404(Publicidad, id=id)
    if request.method == 'POST':
        form = PublicidadForm(request.POST, request.FILES, instance=publicidad)
        if form.is_valid():
            form.save()
            return redirect('lista_publicidad')
    else:
        form = PublicidadForm(instance=publicidad)
    return render(request, 'clientes/editar_publicidad.html', {'form': form})

@login_required
@user_passes_test(lambda u: u.is_staff)
def eliminar_publicidad(request, id):
    publicidad = get_object_or_404(Publicidad, id=id)
    if request.method == 'POST':
        publicidad.delete()
        return redirect('lista_publicidad')
    return render(request, 'clientes/eliminar_publicidad.html', {'publicidad': publicidad})
