# Generated by Django 3.1 on 2020-08-28 01:15

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('alumnos', '0002_auto_20200824_0243'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='alumnocurso',
            options={'permissions': [('list_alumnocurso', 'Puede listar alumnocurso'), ('create_multiple_alumnocurso', 'Puede crear multiples alumnocurso'), ('delete_multiple_alumnocurso', 'Puede borrar multiples alumnocurso')]},
        ),
    ]
