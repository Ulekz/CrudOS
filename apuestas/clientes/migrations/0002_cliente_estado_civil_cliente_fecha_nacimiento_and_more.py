# Generated by Django 5.0.6 on 2024-06-21 17:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('clientes', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='cliente',
            name='estado_civil',
            field=models.CharField(choices=[('S', 'Soltero/a'), ('C', 'Casado/a'), ('D', 'Divorciado/a'), ('V', 'Viudo/a')], default='S', max_length=1),
        ),
        migrations.AddField(
            model_name='cliente',
            name='fecha_nacimiento',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='cliente',
            name='sexo',
            field=models.CharField(choices=[('M', 'Masculino'), ('F', 'Femenino'), ('O', 'Otro')], default='M', max_length=1),
        ),
    ]
