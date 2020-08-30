# Generated by Django 3.1 on 2020-08-26 00:07

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('alumnos', '0001_initial'),
        ('instituciones', '0005_auto_20200807_0241'),
        ('curricula', '0008_auto_20200725_0319'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='RolSeguimiento',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=256)),
                ('fecha_creacion', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='Seguimiento',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fecha_creacion', models.DateTimeField(auto_now_add=True)),
                ('fecha_inicio', models.DateField(auto_now_add=True)),
                ('fecha_cierre', models.DateField()),
                ('descripcion', models.TextField(blank=True, verbose_name='Información General')),
                ('nombre', models.CharField(max_length=256)),
                ('en_progreso', models.BooleanField()),
                ('alumnos', models.ManyToManyField(to='alumnos.AlumnoCurso')),
                ('anio_lectivo', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='curricula.aniolectivo')),
                ('institucion', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='instituciones.institucion')),
                ('materias', models.ManyToManyField(to='curricula.Materia')),
            ],
            options={
                'verbose_name_plural': 'Seguimientos',
                'ordering': ['fecha_creacion'],
                'permissions': [('status_seguimiento', 'Cambiar el estado de seguimiento'), ('list_seguimiento', 'Listar seguimiento')],
            },
        ),
        migrations.CreateModel(
            name='IntegranteSeguimiento',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fecha_hasta', models.DateField(null=True)),
                ('fecha_desde', models.DateField()),
                ('fecha_creacion', models.DateTimeField(auto_now_add=True)),
                ('rol', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='seguimientos.rolseguimiento')),
                ('seguimiento', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='seguimientos.seguimiento')),
                ('usuario', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]