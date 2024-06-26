from django import forms
from django.contrib.auth.models import User
from .models import Cliente, Apuesta, Tarjeta, Publicidad
from django.core.exceptions import ValidationError
from django.utils import timezone

class RegistroClienteForm(forms.ModelForm):
    username = forms.CharField(max_length=30)
    password1 = forms.CharField(widget=forms.PasswordInput)
    password2 = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = Cliente
        fields = [
            'nombre', 'apellido_paterno', 'apellido_materno', 'direccion', 'codigo_postal',
            'estado', 'municipio', 'estado_civil', 'sexo', 'dia_nacimiento', 
            'mes_nacimiento', 'anio_nacimiento', 'email', 'telefono'
        ]

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("El nombre de usuario ya existe. Elige otro.")
        return username

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("El correo electrónico ya está registrado.")
        return email

    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Las contraseñas no coinciden.")
        return password2

    def save(self, commit=True):
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

class ClienteForm(forms.ModelForm):
    class Meta:
        model = Cliente
        fields = [
            'nombre', 'apellido_paterno', 'apellido_materno', 'direccion', 'codigo_postal',
            'estado', 'municipio', 'estado_civil', 'sexo', 'dia_nacimiento', 
            'mes_nacimiento', 'anio_nacimiento', 'email', 'telefono'
        ]

class ApuestaForm(forms.ModelForm):
    class Meta:
        model = Apuesta
        fields = ['monto']
        
class TarjetaForm(forms.ModelForm):
    class Meta:
        model = Tarjeta
        fields = ['nombre_titular', 'numero_tarjeta', 'fecha_expiracion', 'cvv']

    def clean_fecha_expiracion(self):
        fecha_expiracion = self.cleaned_data.get('fecha_expiracion')
        if fecha_expiracion < timezone.now().date():
            raise forms.ValidationError("La fecha de expiración no puede ser en el pasado.")
        return fecha_expiracion

class AdminUserForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput, required=False)

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'is_staff']

    def save(self, commit=True):
        user = super().save(commit=False)
        if self.cleaned_data['password']:
            user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
        return user

class PublicidadForm(forms.ModelForm):
    class Meta:
        model = Publicidad
        fields = ['titulo', 'archivo']
