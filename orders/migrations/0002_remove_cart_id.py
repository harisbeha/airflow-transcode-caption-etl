# Generated by Django 3.0.4 on 2020-04-29 22:35

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='cart',
            name='id',
        ),
    ]
