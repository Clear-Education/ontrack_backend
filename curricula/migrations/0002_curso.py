# Generated by Django 3.0.8 on 2020-07-13 22:41

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('curricula', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Curso',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=150)),
                ('fecha_creacion', models.DateTimeField(auto_now_add=True)),
                ('anio', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='curricula.Anio')),
            ],
            options={
                'permissions': [('list_curso', 'Puede listar cursos')],
            },
        ),
    ]