# Generated by Django 3.0.8 on 2020-07-30 21:08

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('calificaciones', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='calificacion',
            options={'permissions': [('list_calificacion', 'Puede listar calificaciones'), ('create_multiple_calificacion', 'Puede listar calificaciones')]},
        ),
    ]