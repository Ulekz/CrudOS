# Generated by Django 5.0.6 on 2024-07-10 03:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('clientes', '0010_image'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cliente',
            name='apellido_materno',
            field=models.CharField(default='Arreola', max_length=100),
        ),
        migrations.AlterField(
            model_name='cliente',
            name='apellido_paterno',
            field=models.CharField(default='Tejeda', max_length=100),
        ),
    ]
