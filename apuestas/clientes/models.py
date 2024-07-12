from django.db import models
from django.contrib.auth.models import User
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError
from django.utils import timezone
import datetime

# Modelo Cliente
class Cliente(models.Model):
    SEXO_CHOICES = [
        ('M', 'Masculino'),
        ('F', 'Femenino'),
        ('O', 'Otro'),
    ]
    ESTADO_CIVIL_CHOICES = [
        ('S', 'Soltero/a'),
        ('C', 'Casado/a'),
        ('D', 'Divorciado/a'),
        ('V', 'Viudo/a'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)  # Relación uno a uno con el modelo User
    nombre = models.CharField(max_length=100)  # Nombre del cliente
    apellido_paterno = models.CharField(max_length=100, default='Apellido Paterno')  # Apellido paterno del cliente
    apellido_materno = models.CharField(max_length=100, default='Apellido Materno')  # Apellido materno del cliente
    direccion = models.CharField(max_length=255, default='Dirección desconocida')  # Dirección del cliente
    codigo_postal = models.CharField(max_length=10, default='00000')  # Código postal del cliente
    estado = models.CharField(max_length=100, default='Estado')  # Estado donde reside el cliente
    municipio = models.CharField(max_length=100, default='Municipio')  # Municipio donde reside el cliente
    estado_civil = models.CharField(max_length=1, choices=ESTADO_CIVIL_CHOICES, default='S')  # Estado civil del cliente
    sexo = models.CharField(max_length=1, choices=SEXO_CHOICES, default='M')  # Sexo del cliente
    dia_nacimiento = models.IntegerField(default=1)  # Día de nacimiento del cliente
    mes_nacimiento = models.IntegerField(default=1)  # Mes de nacimiento del cliente
    anio_nacimiento = models.IntegerField(default=2000)  # Año de nacimiento del cliente
    email = models.EmailField(unique=True)  # Email del cliente
    telefono = models.CharField(max_length=15, default='Sin teléfono', validators=[RegexValidator(regex=r'^\+?1?\d{9,15}$')])  # Teléfono del cliente
    fecha_registro = models.DateTimeField(auto_now_add=True)  # Fecha de registro del cliente

    def clean(self):
        """
        Validar que la fecha de nacimiento sea una fecha válida y lógica.
        """
        try:
            if self.anio_nacimiento and self.mes_nacimiento and self.dia_nacimiento:
                nacimiento = datetime.date(self.anio_nacimiento, self.mes_nacimiento, self.dia_nacimiento)
                if nacimiento > timezone.now().date():
                    raise ValidationError("La fecha de nacimiento no puede ser en el futuro.")
                age = timezone.now().year - nacimiento.year - ((timezone.now().month, timezone.now().day) < (nacimiento.month, nacimiento.day))
                if age < 0:
                    raise ValidationError("Fecha de nacimiento inválida.")
        except ValueError:
            raise ValidationError("Fecha de nacimiento inválida.")

    def save(self, *args, **kwargs):
        """
        Asegura que clean() sea llamado antes de guardar.
        Capitaliza nombres y direcciones antes de guardar.
        """
        self.full_clean()
        self.nombre = self.nombre.title()
        self.apellido_paterno = self.apellido_paterno.title()
        self.apellido_materno = self.apellido_materno.title()
        self.direccion = self.direccion.title()
        self.estado = self.estado.title()
        self.municipio = self.municipio.title()
        super().save(*args, **kwargs)

    def get_full_name(self):
        """
        Devuelve el nombre completo del cliente.
        """
        return f'{self.nombre} {self.apellido_paterno} {self.apellido_materno}'

    def __str__(self):
        return self.get_full_name()

    class Meta:
        indexes = [
            models.Index(fields=['email']),
            models.Index(fields=['telefono']),
        ]

# Modelo Apuesta
class Apuesta(models.Model):
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)  # Relación con el modelo Cliente
    monto = models.DecimalField(max_digits=10, decimal_places=2)  # Monto de la apuesta
    fecha = models.DateTimeField(auto_now_add=True)  # Fecha de la apuesta

    def __str__(self):
        return f"Apuesta de {self.cliente.get_full_name()} - {self.monto}"

# Modelo Tarjeta
class Tarjeta(models.Model):
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)  # Relación con el modelo Cliente
    nombre_titular = models.CharField(max_length=100)  # Nombre del titular de la tarjeta
    numero_tarjeta = models.CharField(max_length=16, validators=[RegexValidator(regex=r'^\d{16}$')])  # Número de la tarjeta
    fecha_expiracion = models.DateField()  # Fecha de expiración de la tarjeta
    cvv = models.CharField(max_length=4, validators=[RegexValidator(regex=r'^\d{3,4}$')])  # CVV de la tarjeta

    def clean(self):
        """
        Validar que la fecha de expiración no sea en el pasado.
        """
        if self.fecha_expiracion < timezone.now().date():
            raise ValidationError("La fecha de expiración no puede ser en el pasado.")

    def save(self, *args, **kwargs):
        """
        Asegura que clean() sea llamado antes de guardar.
        Capitaliza el nombre del titular antes de guardar.
        """
        self.full_clean()
        self.nombre_titular = self.nombre_titular.title()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Tarjeta de {self.nombre_titular} - **** **** **** {self.numero_tarjeta[-4:]}"

# Modelo Publicidad
class Publicidad(models.Model):
    POSICION_CHOICES = [
        ('izquierda', 'Izquierda'),
        ('derecha', 'Derecha'),
    ]
    titulo = models.CharField(max_length=100)  # Título de la publicidad
    archivo = models.FileField(upload_to='publicidad/')  # Archivo de la publicidad
    fecha_subida = models.DateTimeField(auto_now_add=True)  # Fecha de subida de la publicidad
    posicion = models.CharField(max_length=10, choices=POSICION_CHOICES, default='izquierda')  # Posición de la publicidad

    def __str__(self):
        return self.titulo

# Modelo Image
class Image(models.Model):
    POSITION_CHOICES = [
        ('left', 'Izquierda'),
        ('right', 'Derecha'),
    ]

    title = models.CharField(max_length=255)  # Título de la imagen
    image = models.ImageField(upload_to='images/')  # Archivo de la imagen
    position = models.CharField(max_length=10, choices=POSITION_CHOICES, default='left')  # Posición de la imagen
    uploaded_at = models.DateTimeField(auto_now_add=True)  # Fecha de subida de la imagen

    def __str__(self):
        return self.title
