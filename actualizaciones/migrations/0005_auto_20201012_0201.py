# Generated by Django 3.0.8 on 2020-10-12 02:01

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('actualizaciones', '0004_auto_20201002_0315'),
    ]

    operations = [
        migrations.AlterField(
            model_name='actualizacion',
            name='padre',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='comentarios', to='actualizaciones.Actualizacion'),
        ),
    ]
