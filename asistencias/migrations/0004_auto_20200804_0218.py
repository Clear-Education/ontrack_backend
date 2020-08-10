# Generated by Django 3.0.8 on 2020-08-04 02:18

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('asistencias', '0003_auto_20200801_1452'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='asistencia',
            options={'permissions': [('list_asistencia', 'Puede listar asistencias'), ('create_multiple_asistencia', 'Puede crear multiples asistencias'), ('destroy_curso_dia_asistencia', 'Puede borrar multiples asistencias'), ('porcentaje_asistencia', 'Puede obtener el porcentaje de asistencias')]},
        ),
        migrations.DeleteModel(
            name='AsistenciaAnioLectivo',
        ),
    ]
