# Generated by Django 5.0.6 on 2024-07-10 04:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('clientes', '0011_alter_cliente_apellido_materno_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cliente',
            name='apellido_materno',
            field=models.CharField(default='Apellido Materno', max_length=100),
        ),
        migrations.AlterField(
            model_name='cliente',
            name='apellido_paterno',
            field=models.CharField(default='Apellido Paterno', max_length=100),
        ),
    ]
