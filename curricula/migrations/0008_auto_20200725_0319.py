# Generated by Django 3.0.8 on 2020-07-25 03:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('curricula', '0007_delete_alumno'),
    ]

    operations = [
        migrations.AlterField(
            model_name='aniolectivo',
            name='nombre',
            field=models.CharField(max_length=150),
        ),
    ]
