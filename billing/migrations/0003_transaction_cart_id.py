# Generated by Django 3.0.4 on 2020-05-10 20:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('billing', '0002_auto_20200510_1950'),
    ]

    operations = [
        migrations.AddField(
            model_name='transaction',
            name='cart_id',
            field=models.TextField(blank=True, null=True),
        ),
    ]
