# Generated by Django 5.0.6 on 2024-07-12 04:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('clientes', '0012_alter_cliente_apellido_materno_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='image',
            name='position',
            field=models.CharField(choices=[('left', 'Arriba'), ('right', 'Abajo')], default='left', max_length=10),
        ),
    ]