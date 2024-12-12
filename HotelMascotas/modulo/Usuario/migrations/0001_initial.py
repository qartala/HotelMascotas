# Generated by Django 5.1 on 2024-10-22 01:48

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('Colaborador', '0001_initial'),
        ('Producto', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Calificacion',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('comentario', models.TextField()),
                ('calificacion', models.PositiveSmallIntegerField(default=5)),
                ('fecha_creacion', models.DateTimeField(auto_now_add=True)),
                ('usuario', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Usuario',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tipo_cuenta', models.CharField(max_length=20)),
                ('telefono', models.CharField(blank=True, max_length=15, null=True)),
                ('direccion', models.CharField(blank=True, max_length=255, null=True)),
                ('fecha_nacimiento', models.DateField(blank=True, null=True)),
                ('idUsuario', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('membresia', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='Producto.membresia')),
            ],
        ),
        migrations.CreateModel(
            name='Ficha',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre_perro', models.CharField(max_length=100)),
                ('nombre_dueno', models.CharField(max_length=100)),
                ('raza', models.CharField(max_length=100)),
                ('edad', models.IntegerField()),
                ('peso', models.FloatField()),
                ('chip', models.CharField(max_length=10)),
                ('comida', models.CharField(max_length=100)),
                ('vacunas', models.TextField()),
                ('alergias', models.TextField()),
                ('enfermedades', models.TextField()),
                ('imagen_mascota', models.ImageField(blank=True, null=True, upload_to='')),
                ('id_usuario', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Usuario.usuario')),
            ],
        ),
        migrations.CreateModel(
            name='ReservaServicio',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('servicio', models.CharField(max_length=100)),
                ('fecha_reservada', models.DateField()),
                ('precio', models.PositiveIntegerField()),
                ('hora_inicio', models.TimeField(blank=True, null=True)),
                ('hora_fin', models.TimeField(blank=True, null=True)),
                ('pagado', models.BooleanField(default=False)),
                ('colaborador', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Colaborador.colaborador')),
                ('mascota', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Usuario.ficha')),
            ],
            options={
                'unique_together': {('colaborador', 'servicio', 'fecha_reservada', 'hora_inicio', 'hora_fin', 'mascota')},
            },
        ),
    ]
