import datetime
from django import forms
from django.contrib.auth.models import User
from .models import Cliente, Apuesta, Tarjeta, Publicidad, Image
from django.core.exceptions import ValidationError
from django.utils import timezone

# Formulario de registro de clientes
class RegistroClienteForm(forms.ModelForm):
    username = forms.CharField(max_length=30)  # Campo para el nombre de usuario
    password1 = forms.CharField(widget=forms.PasswordInput)  # Campo para la contraseña
    password2 = forms.CharField(widget=forms.PasswordInput)  # Campo para confirmar la contraseña

    class Meta:
        model = Cliente
        fields = [
            'nombre', 'apellido_paterno', 'apellido_materno', 'direccion', 'codigo_postal',
            'estado', 'municipio', 'estado_civil', 'sexo', 'dia_nacimiento', 
            'mes_nacimiento', 'anio_nacimiento', 'email', 'telefono'
        ]

    def clean_username(self):
        # Validar que el nombre de usuario no exista
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("El nombre de usuario ya existe. Elige otro.")
        return username

    def clean_email(self):
        # Validar que el email no esté registrado
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("El correo electrónico ya está registrado.")
        return email

    def clean_password2(self):
        # Validar que las contraseñas coincidan y tengan al menos 8 caracteres
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Las contraseñas no coinciden.")
        if len(password1) < 8:
            raise forms.ValidationError("La contraseña debe tener al menos 8 caracteres.")
        return password2

    def clean(self):
        cleaned_data = super().clean()
        dia = cleaned_data.get('dia_nacimiento')
        mes = cleaned_data.get('mes_nacimiento')
        anio = cleaned_data.get('anio_nacimiento')

        if dia is None or mes is None or anio is None:
            raise forms.ValidationError("La fecha de nacimiento es obligatoria.")

        try:
            datetime.date(anio, mes, dia)
        except ValueError:
            raise forms.ValidationError("Fecha de nacimiento inválida.")

        return cleaned_data

    def save(self, commit=True):
        # Crear el usuario y el cliente asociado
        user = User.objects.create_user(
            username=self.cleaned_data['username'],
            password=self.cleaned_data['password1'],
            email=self.cleaned_data['email']
        )
        cliente = super().save(commit=False)
        cliente.user = user
        if commit:
            cliente.save()
        return cliente

# Formulario para actualizar información del cliente
class ClienteForm(forms.ModelForm):
    class Meta:
        model = Cliente
        fields = [
            'nombre', 'apellido_paterno', 'apellido_materno', 'direccion', 
            'codigo_postal', 'estado', 'municipio', 'estado_civil', 'sexo', 
            'dia_nacimiento', 'mes_nacimiento', 'anio_nacimiento', 'email', 'telefono'
        ]

    def clean(self):
        cleaned_data = super().clean()
        dia = cleaned_data.get('dia_nacimiento')
        mes = cleaned_data.get('mes_nacimiento')
        anio = cleaned_data.get('anio_nacimiento')

        if dia is None or mes is None or anio is None:
            raise forms.ValidationError("La fecha de nacimiento es obligatoria.")

        try:
            dia = int(dia)
            mes = int(mes)
            anio = int(anio)
        except ValueError:
            raise forms.ValidationError("La fecha de nacimiento debe ser un número válido.")

        try:
            datetime.date(anio, mes, dia)
        except ValueError:
            raise forms.ValidationError("Fecha de nacimiento inválida.")

        return cleaned_data
    
# Formulario para crear una apuesta
class ApuestaForm(forms.ModelForm):
    class Meta:
        model = Apuesta
        fields = ['monto']

# Formulario para agregar una tarjeta
class TarjetaForm(forms.ModelForm):
    class Meta:
        model = Tarjeta
        fields = ['nombre_titular', 'numero_tarjeta', 'fecha_expiracion', 'cvv']

    def clean_fecha_expiracion(self):
        # Validar que la fecha de expiración no sea en el pasado
        fecha_expiracion = self.cleaned_data.get('fecha_expiracion')
        if fecha_expiracion < timezone.now().date():
            raise forms.ValidationError("La fecha de expiración no puede ser en el pasado.")
        return fecha_expiracion

    def clean_numero_tarjeta(self):
        # Validar que el número de tarjeta tenga 16 dígitos
        numero_tarjeta = self.cleaned_data.get('numero_tarjeta')
        if len(numero_tarjeta) != 16:
            raise forms.ValidationError("El número de tarjeta debe tener 16 dígitos.")
        return numero_tarjeta

    def clean_cvv(self):
        # Validar que el CVV tenga 3 o 4 dígitos
        cvv = self.cleaned_data.get('cvv')
        if len(cvv) not in [3, 4]:
            raise forms.ValidationError("El CVV debe tener 3 o 4 dígitos.")
        return cvv

# Formulario para administrar usuarios
class AdminUserForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput, required=False)  # Campo para la contraseña

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'is_staff']

    def save(self, commit=True):
        # Guardar el usuario y establecer la contraseña si es proporcionada
        user = super().save(commit=False)
        if self.cleaned_data['password']:
            user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
        return user

# Formulario para agregar una publicidad
class PublicidadForm(forms.ModelForm):
    class Meta:
        model = Publicidad
        fields = ['titulo', 'archivo']

# Formulario para subir una imagen
class ImageForm(forms.ModelForm):
    class Meta:
        model = Image
        fields = ['title', 'image', 'position']
