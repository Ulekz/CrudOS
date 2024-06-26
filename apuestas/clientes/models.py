from django.db import models
from django.contrib.auth.models import User
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError
from django.utils import timezone
import datetime

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

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    nombre = models.CharField(max_length=100)
    apellido_paterno = models.CharField(max_length=100, default='Apellido Paterno')
    apellido_materno = models.CharField(max_length=100, default='Apellido Materno')
    direccion = models.CharField(max_length=255, default='Dirección desconocida')
    codigo_postal = models.CharField(max_length=10, default='00000')
    estado = models.CharField(max_length=100, default='Estado')
    municipio = models.CharField(max_length=100, default='Municipio')
    estado_civil = models.CharField(max_length=1, choices=ESTADO_CIVIL_CHOICES, default='S')
    sexo = models.CharField(max_length=1, choices=SEXO_CHOICES, default='M')
    dia_nacimiento = models.IntegerField(default=1)
    mes_nacimiento = models.IntegerField(default=1)
    anio_nacimiento = models.IntegerField(default=2000)
    email = models.EmailField(unique=True)
    telefono = models.CharField(max_length=15, default='Sin teléfono', validators=[RegexValidator(regex=r'^\+?1?\d{9,15}$')])
    fecha_registro = models.DateTimeField(auto_now_add=True)

    def clean(self):
        # Validar que la fecha de nacimiento sea una fecha válida
        try:
            if self.anio_nacimiento and self.mes_nacimiento and self.dia_nacimiento:
                nacimiento = datetime.date(self.anio_nacimiento, self.mes_nacimiento, self.dia_nacimiento)
                if nacimiento > timezone.now().date():
                    raise ValidationError("La fecha de nacimiento no puede ser en el futuro.")
        except ValueError:
            raise ValidationError("Fecha de nacimiento inválida.")

    def save(self, *args, **kwargs):
        self.full_clean()  # Asegura que clean() sea llamado antes de guardar
        self.nombre = self.nombre.title()
        self.apellido_paterno = self.apellido_paterno.title()
        self.apellido_materno = self.apellido_materno.title()
        self.direccion = self.direccion.title()
        self.estado = self.estado.title()
        self.municipio = self.municipio.title()
        super().save(*args, **kwargs)

    def get_full_name(self):
        return f"{self.user.first_name} {self.user.last_name}"

    def __str__(self):
        return self.get_full_name()

    class Meta:
        indexes = [
            models.Index(fields=['email']),
            models.Index(fields=['telefono']),
        ]

class Apuesta(models.Model):
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    monto = models.DecimalField(max_digits=10, decimal_places=2)
    fecha = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Apuesta de {self.cliente.get_full_name()} - {self.monto}"

class Tarjeta(models.Model):
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    nombre_titular = models.CharField(max_length=100)
    numero_tarjeta = models.CharField(max_length=16, validators=[RegexValidator(regex=r'^\d{16}$')])
    fecha_expiracion = models.DateField()
    cvv = models.CharField(max_length=4, validators=[RegexValidator(regex=r'^\d{3,4}$')])

    def clean(self):
        # Validar que la fecha de expiración no sea en el pasado
        if self.fecha_expiracion < timezone.now().date():
            raise ValidationError("La fecha de expiración no puede ser en el pasado.")

    def save(self, *args, **kwargs):
        self.full_clean()  # Asegura que clean() sea llamado antes de guardar
        self.nombre_titular = self.nombre_titular.title()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Tarjeta de {self.nombre_titular} - **** **** **** {self.numero_tarjeta[-4:]}"
    

class Publicidad(models.Model):
    POSICION_CHOICES = [
        ('izquierda', 'Izquierda'),
        ('derecha', 'Derecha'),
    ]
    titulo = models.CharField(max_length=100)
    archivo = models.FileField(upload_to='publicidad/')
    fecha_subida = models.DateTimeField(auto_now_add=True)
    posicion = models.CharField(max_length=10, choices=POSICION_CHOICES, default='izquierda')

    def __str__(self):
        return self.titulo
