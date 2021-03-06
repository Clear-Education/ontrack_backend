# Generated by Django 3.0.8 on 2020-10-17 15:36

from django.db import migrations, models
import objetivos.models


class Migration(migrations.Migration):

    dependencies = [
        ('objetivos', '0006_auto_20201017_0228'),
    ]

    operations = [
        migrations.AddField(
            model_name='alumnoobjetivo',
            name='fecha_calculo',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='alumnoobjetivo',
            name='fecha_relacionada',
            field=models.DateField(blank=True, default=objetivos.models.default_fecha),
        ),
    ]
