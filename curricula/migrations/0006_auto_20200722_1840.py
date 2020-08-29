# Generated by Django 3.0.8 on 2020-07-22 21:40

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('instituciones', '0003_auto_20200713_1302'),
        ('curricula', '0005_auto_20200718_0311'),
    ]

    operations = [
        migrations.CreateModel(
            name='Alumno',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('dni', models.IntegerField(blank=True, unique=True)),
                ('nombre', models.CharField(max_length=150)),
                ('apellido', models.CharField(max_length=150)),
                ('email', models.EmailField(max_length=254, null=True)),
                ('legajo', models.CharField(max_length=150, unique=True)),
                ('fecha_nacimiento', models.DateField(blank=True, null=True)),
                ('direccion', models.CharField(max_length=150, null=True)),
                ('localidad', models.CharField(max_length=150, null=True)),
                ('provincia', models.CharField(max_length=150, null=True)),
                ('fecha_creacion', models.DateTimeField(auto_now_add=True)),
                ('fecha_inscripcion', models.DateField(null=True)),
                ('institucion', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='instituciones.Institucion')),
            ],
            options={
                'permissions': [('list_alumno', 'Puede listar alumnos')],
            },
        ),
        migrations.RemoveField(
            model_name='evaluacion',
            name='materia_evaluacion',
        ),
        migrations.AddField(
            model_name='evaluacion',
            name='anio_lectivo',
            field=models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, related_name='evaluaciones', to='curricula.AnioLectivo'),
        ),
        migrations.AddField(
            model_name='evaluacion',
            name='materia',
            field=models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, related_name='evaluaciones', to='curricula.Materia'),
        ),
        migrations.DeleteModel(
            name='MateriaEvaluacion',
        ),
    ]
