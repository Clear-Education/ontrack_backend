# Generated by Django 3.0.8 on 2020-09-30 02:39

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('seguimientos', '0010_auto_20200917_2132'),
    ]

    operations = [
        migrations.CreateModel(
            name='Actualizacion',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cuerpo', models.CharField(max_length=500)),
                ('fecha_creacion', models.DateTimeField(auto_now_add=True)),
                ('fecha_modificacion', models.DateTimeField(auto_now=True)),
                ('padre', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='hijo', to='actualizaciones.Actualizacion')),
                ('seguimiento', models.ForeignKey(blank=True, on_delete=django.db.models.deletion.CASCADE, to='seguimientos.Seguimiento')),
                ('usuario', models.ForeignKey(blank=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'permissions': [('list_actualizacion', 'Puede listar actualizaciones')],
            },
        ),
        migrations.CreateModel(
            name='ActualizacionAdjunto',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fecha_creacion', models.DateTimeField(auto_now_add=True)),
                ('url', models.URLField()),
                ('actualizacion', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='adjuntos', to='actualizaciones.Actualizacion')),
            ],
        ),
    ]