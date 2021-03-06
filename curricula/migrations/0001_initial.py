# Generated by Django 3.0.8 on 2020-07-13 15:43

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('instituciones', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Anio',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=150)),
                ('fecha_creacion', models.DateTimeField(auto_now_add=True)),
                ('color', models.CharField(max_length=150)),
            ],
            options={
                'permissions': [('list_anio', 'Puede listar anio')],
            },
        ),
        migrations.CreateModel(
            name='Materia',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=150)),
                ('fecha_creacion', models.DateTimeField(auto_now_add=True)),
                ('color', models.CharField(max_length=150)),
                ('anio', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='curricula.Anio')),
            ],
            options={
                'permissions': [('list_materia', 'Puede listar materias')],
            },
        ),
        migrations.CreateModel(
            name='Evaluacion',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=150)),
                ('fecha_creacion', models.DateTimeField(auto_now_add=True)),
                ('ponderacion', models.FloatField()),
                ('materia', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='curricula.Materia')),
            ],
            options={
                'permissions': [('list_evaluacion', 'Puede listar evaluaciones')],
            },
        ),
        migrations.CreateModel(
            name='Carrera',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=150)),
                ('descripcion', models.TextField()),
                ('fecha_creacion', models.DateTimeField(auto_now_add=True)),
                ('color', models.CharField(max_length=150)),
                ('institucion', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='instituciones.Institucion')),
            ],
            options={
                'permissions': [('list_carrera', 'Puede listar carreras')],
            },
        ),
        migrations.AddField(
            model_name='anio',
            name='carrera',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='curricula.Carrera'),
        ),
    ]
