# Generated by Django 5.0.6 on 2024-06-24 22:08

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('clientes', '0005_publicidad'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='publicidad',
            name='posicion',
        ),
    ]
