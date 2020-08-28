# Generated by Django 3.1 on 2020-08-28 03:06

from django.db import migrations, models
import users.models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0009_auto_20200828_0304'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='last_name',
            field=models.CharField(blank=True, max_length=150, null=True, validators=[users.models.validate_name], verbose_name='Apellido'),
        ),
        migrations.AlterField(
            model_name='user',
            name='phone',
            field=models.CharField(blank=True, max_length=50, null=True, validators=[users.models.validate_phone], verbose_name='Teléfono'),
        ),
    ]
