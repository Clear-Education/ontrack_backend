# Generated by Django 3.1 on 2020-08-28 01:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('instituciones', '0005_auto_20200807_0241'),
    ]

    operations = [
        migrations.AddField(
            model_name='institucion',
            name='cuit',
            field=models.BigIntegerField(blank=True, null=True, verbose_name='CUIT'),
        ),
        migrations.AlterField(
            model_name='institucion',
            name='pais',
            field=models.CharField(blank=True, choices=[('AR', 'Argentina'), ('UR', 'Uruguay'), ('CH', 'Chile'), ('BR', 'Brasil'), ('BV', 'Bolivia'), ('PE', 'Peru'), ('PG', 'Paraguay')], max_length=250, verbose_name='País'),
        ),
    ]
