# Generated by Django 3.0.8 on 2020-09-16 22:49

from django.db import migrations, models
import instituciones.models


class Migration(migrations.Migration):

    dependencies = [
        ('instituciones', '0007_remove_institucion_cuit'),
    ]

    operations = [
        migrations.AlterField(
            model_name='institucion',
            name='identificador',
            field=models.CharField(blank=True, max_length=250, validators=[instituciones.models.clean_identificador]),
        ),
    ]
