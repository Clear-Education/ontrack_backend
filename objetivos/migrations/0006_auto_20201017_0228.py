# Generated by Django 3.0.8 on 2020-10-17 02:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('objetivos', '0005_alumnoobjetivo_fecha_relacionada'),
    ]

    operations = [
        migrations.AlterField(
            model_name='alumnoobjetivo',
            name='fecha_relacionada',
            field=models.DateField(auto_now_add=True),
        ),
    ]