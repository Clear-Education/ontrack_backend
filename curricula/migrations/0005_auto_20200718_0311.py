# Generated by Django 3.0.8 on 2020-07-18 03:11

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('curricula', '0004_auto_20200715_2359'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='aniolectivo',
            options={'permissions': [('list_aniolectivo', 'Puede listar años lectivos')]},
        ),
    ]
