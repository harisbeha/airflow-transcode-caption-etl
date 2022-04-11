# Generated by Django 3.0.4 on 2020-04-29 09:43

from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('orgs', '0002_organization_organizationuser'),
    ]

    operations = [
        migrations.CreateModel(
            name='BillingInfo',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('balance', models.PositiveIntegerField(default=0, verbose_name='Track balance')),
                ('stripe_customer_id', models.TextField()),
                ('stripe_tokens', models.TextField(default=None, null=True)),
                ('stripe_subscription_id', models.TextField(null=True)),
                ('payment_methods', models.TextField()),
                ('next_billing_date', models.DateField(blank=True, null=True)),
                ('contact_email', models.TextField()),
                ('address_1', models.TextField()),
                ('address_2', models.TextField()),
                ('city', models.TextField()),
                ('postal_code', models.TextField()),
                ('country', models.TextField()),
                ('status', models.IntegerField(choices=[(0, 'awaiting_subscription'), (1, 'active'), (2, 'grace'), (3, 'canceled'), (4, 'frozen')], default=0)),
                ('organization', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='org_billing', to='orgs.Organization')),
                ('user', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='billing_user', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'user billing entity',
                'verbose_name_plural': 'user billing entities',
                'ordering': ['-next_billing_date'],
            },
        ),
        migrations.CreateModel(
            name='Coupon',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(max_length=12)),
                ('coupon_type', models.CharField(choices=[('Account', 'Account'), ('Order', 'Order')], max_length=128)),
                ('discount_cost', models.DecimalField(blank=True, decimal_places=2, help_text='Amount in Dollars', max_digits=5, null=True, validators=[django.core.validators.MinValueValidator(0)])),
                ('discount_percent', models.DecimalField(blank=True, decimal_places=2, help_text='Percentage takes preference', max_digits=3, null=True, validators=[django.core.validators.MaxValueValidator(100), django.core.validators.MinValueValidator(0)])),
                ('expires', models.DateField()),
                ('priority', models.PositiveIntegerField(default=0)),
                ('allow_stacking', models.BooleanField(choices=[(False, 'deny'), (True, 'allow')], default=False, help_text='Whether or not this coupon can stack with other coupons.')),
            ],
            options={
                'ordering': ['-priority'],
            },
        ),
        migrations.CreateModel(
            name='Plan',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('stripe_id', models.TextField(null=True)),
                ('name', models.TextField()),
                ('description', models.TextField()),
                ('price', models.DecimalField(decimal_places=2, help_text='Amount in Dollars', max_digits=5)),
                ('features', models.TextField()),
                ('interval', models.CharField(choices=[('month', 'Monthly'), ('quarter', 'Quarterly'), ('year', 'Yearly')], default='month', max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=128)),
                ('short_description', models.CharField(max_length=64)),
                ('description', models.TextField()),
                ('is_discountable', models.BooleanField()),
                ('unit_of_measure', models.CharField(max_length=64)),
                ('display_name', models.CharField(max_length=64)),
                ('is_addon', models.BooleanField()),
                ('base_price', models.FloatField()),
            ],
        ),
        migrations.CreateModel(
            name='Transaction',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('transaction_type', models.CharField(max_length=64)),
                ('amount', models.DecimalField(decimal_places=2, max_digits=6, verbose_name='Amount')),
                ('transaction_details', models.TextField(blank=True, verbose_name='Charge details')),
                ('service', models.CharField(max_length=64)),
                ('timestamp', models.DateTimeField()),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('billing_info', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='transactions', to='billing.BillingInfo')),
            ],
            options={
                'ordering': ['-timestamp'],
            },
        ),
    ]
