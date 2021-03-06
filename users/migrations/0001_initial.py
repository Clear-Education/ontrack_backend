# Generated by Django 3.0.8 on 2020-07-13 15:43

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import users.managers


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0011_update_proxy_permissions'),
        ('instituciones', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('deleted_at', models.DateTimeField(blank=True, db_index=True, default=None, editable=False, null=True)),
                ('email', models.EmailField(max_length=254, unique=True)),
                ('name', models.CharField(max_length=150, null=True)),
                ('phone', models.CharField(max_length=50, null=True)),
                ('date_of_birth', models.DateField(blank=True, null=True)),
                ('picture', models.ImageField(blank=True, null=True, upload_to='')),
                ('is_staff', models.BooleanField(default=False)),
                ('is_active', models.BooleanField(default=True)),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now)),
                ('last_login', models.DateTimeField(null=True)),
                ('groups', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='auth.Group')),
                ('institucion', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='instituciones.Institucion')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.Permission', verbose_name='user permissions')),
            ],
            options={
                'permissions': [('createadmin_user', 'Can create users with group Admin'), ('list_user', 'Can list all users'), ('alta_user', 'Can re-activate a deleted User'), ('change_other_user', 'Can edit other users info')],
            },
            managers=[
                ('objects', users.managers.UserManager()),
            ],
        ),
    ]
