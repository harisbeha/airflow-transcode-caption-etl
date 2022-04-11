# Generated by Django 3.0.4 on 2020-04-29 09:43

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('orgs', '0002_organization_organizationuser'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('library', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='AccountConfiguration',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('configuration_data', models.TextField(default='{}')),
                ('account', models.OneToOneField(on_delete=django.db.models.deletion.DO_NOTHING, to=settings.AUTH_USER_MODEL)),
                ('default_preset', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='user_preset', to='library.Entry')),
            ],
        ),
        migrations.CreateModel(
            name='AccessToken',
            fields=[
                ('uuid', models.UUIDField(default=uuid.uuid4, primary_key=True, serialize=False)),
                ('access_token', models.TextField(db_index=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('is_active', models.BooleanField(default=True)),
                ('description', models.TextField(blank=True, null=True)),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='user_created_tokens', to=settings.AUTH_USER_MODEL)),
                ('member', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='access_tokens', to='orgs.OrganizationUser')),
            ],
        ),
    ]