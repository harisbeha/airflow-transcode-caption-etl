# Generated by Django 3.0.4 on 2020-04-30 23:41

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0004_auto_20200430_2337'),
    ]

    operations = [
        migrations.AddField(
            model_name='orderitem',
            name='product_template',
            field=models.ForeignKey(default=uuid.UUID('c2c2428c-1b49-4c96-964b-3dfa2f323bbd'), null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='product_template', to='orders.Preset'),
        ),
    ]
