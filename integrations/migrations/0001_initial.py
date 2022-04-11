# Generated by Django 3.0.4 on 2020-04-29 09:43

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='ZoomAuth',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('zoom_refresh_token', models.TextField()),
                ('auto_import', models.BooleanField()),
                ('auto_import_interval', models.CharField(max_length=12)),
                ('auto_import_max_daily', models.IntegerField(default=50)),
                ('auto_import_meetings', models.BooleanField()),
                ('auto_import_webinars', models.BooleanField()),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='zoom_user_profiles', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='GoogleAPIOauthInfo',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('access_token', models.TextField()),
                ('credentials', models.TextField(blank=True, null=True)),
                ('expiry', models.TextField(blank=True, null=True)),
                ('refresh_token', models.TextField()),
                ('scopes', models.TextField()),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='youtube_user_profiles', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
