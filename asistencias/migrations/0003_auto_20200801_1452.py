# Generated by Django 3.0.8 on 2020-08-01 14:52

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('asistencias', '0002_auto_20200730_0202'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='asistencia',
            options={'permissions': [('list_asistencia', 'Puede listar asistencias'), ('create_multiple_asistencia', 'Puede crear multiples asistencias'), ('destroy_curso_dia_asistencia', 'Puede borrar multiples asistencias')]},
        ),
    ]
