from __future__ import unicode_literals

from datetime import datetime

import stripe
import time

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils.text import slugify
from django.db.models import Count, F, Value
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver

from django.contrib.auth.models import User

import analytics

class Plan(models.Model):
    stripe_id = models.TextField(null=True)
    name = models.TextField()
    description = models.TextField()
    price = models.DecimalField(max_digits=5, decimal_places=2, help_text='Amount in Dollars')
    features = models.TextField()
    interval = models.CharField(default="month", choices=[('month', 'Monthly'),('quarter', 'Quarterly',), ('year', 'Yearly',)], max_length=100)

    def __str__(self):
        return slugify("{} {} {}".format(self.name, self.interval, self.price))

    def get_stripe_id(self):
        return self.stripe_id

    def provision_stripe(self):
        plan = stripe.Plan.create(
            name=self.name,
            id=self.get_stripe_id(),
            interval=self.interval,
            currency="usd",
            amount=self.price,
            api_key=settings.STRIPE_API_KEY,
        )


class Coupon(models.Model):
    class Meta:
        ordering = ['-priority']

    code = models.CharField(max_length=12)
    coupon_type = models.CharField(max_length=128, choices=[("Account", "Account"), ("Order", "Order")])
    discount_cost = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True,
                                        help_text='Amount in Dollars', validators=[MinValueValidator(0)])
    discount_percent = models.DecimalField(max_digits=3, decimal_places=2, blank=True, null=True,
                                           help_text='Percentage takes preference',
                                           validators=[MaxValueValidator(100), MinValueValidator(0)])
    expires = models.DateField()
    priority = models.PositiveIntegerField(default=0)
    allow_stacking = models.BooleanField(default = False, choices = [(False, 'deny'), (True, 'allow')],
        help_text = "Whether or not this coupon can stack with other coupons.")

    def __str__(self):
        return 'Coupon "%s" for %s off (valid until %s)' % (self.code, self.discount, self.expires)

    @property
    def discount(self):
        if self.discount_percent:
            return '%s%%' % self.discount_percent
        return '$%s' % self.discount_cost

    def full_clean(self, exclude=None, validate_unique=True):
        if self.discount_percent and self.discount_cost or not (self.discount_percent or self.discount_cost):
            raise ValidationError('Enter either a discount percent or cost')

        if self.expires <= datetime.today().date():
            raise ValidationError('Coupon expires too soon')

    def apply(self, price):
        if self.discount_cost:
            price -= self.discount_cost
        if self.discount_percent:
            price *= (100-self.discount_percent)/100

class BillingInfo(models.Model):
    class Meta:
        verbose_name = 'user billing entity'
        verbose_name_plural = 'user billing entities'
        ordering = ['-next_billing_date']

    # State constants.
    STATE_AWAITING_SUBSCRIPTION = 0
    STATE_ACTIVE = 1
    STATE_GRACE = 2
    STATE_CANCELED = 3
    STATE_FROZEN = 4

    user = models.OneToOneField(User, blank=True, null=True, related_name='billing_user', on_delete=models.DO_NOTHING)
    organization = models.OneToOneField("orgs.Organization", related_name="org_billing", on_delete=models.DO_NOTHING, null=True, blank=True)
    balance = models.PositiveIntegerField("Track balance", default=0)

    stripe_customer_id = models.TextField()
    # csv
    stripe_tokens = models.TextField(null=True, default=None)
    stripe_subscription_id = models.TextField(null=True)

    payment_methods = models.TextField()

    next_billing_date = models.DateField(blank=True, null=True)

    contact_email = models.TextField()

    address_1 = models.TextField()
    address_2 = models.TextField()
    city = models.TextField()
    postal_code = models.TextField()
    country = models.TextField()

    status = models.IntegerField(choices=[
        (STATE_AWAITING_SUBSCRIPTION, 'awaiting_subscription'),
        (STATE_ACTIVE, 'active'),
        (STATE_GRACE, 'grace'), 
        (STATE_CANCELED, 'canceled'),
        (STATE_FROZEN, 'frozen'),
    ], default=STATE_AWAITING_SUBSCRIPTION)

    def __str__(self):
        if self.user:
            return "%s's billing entity" % self.user
        return 'New billing entity'

    def get_stripe_customer(self):
        stripe.api_key = settings.STRIPE_API_KEY
        customer = stripe.Customer.retrieve(self.stripe_customer_id)
        print(customer)
        return customer

    def set_default_payment_method(self, payment_method_id):
        stripe.api_key = settings.STRIPE_API_KEY
        payment_method = stripe.PaymentMethod.retrieve(payment_method_id)
        customer = stripe.Customer.modify(self.stripe_customer_id, default_source=payment_method)
        print(customer["default_source"])
        return customer

    def get_default_payment_method(self):
        stripe.api_key = settings.STRIPE_API_KEY
        payment_method = stripe.PaymentMethod.list(
            customer=self.stripe_customer_id,
            type="card",
        )
        return payment_method

    # Do in Auth0 CB
    def provision_stripe(self):
        pass
        # customer = stripe.Customer.create(
        #     email=self.user.email,
        #     source=self.stripe_token,
        #     api_key=settings.STRIPE_API_KEY)
        # self.stripe_customer_id = customer.id
        # self.stripe_token=None

    def associate_plan(self, plan):
        subscription = stripe.Subscription.create(
            customer=self.stripe_customer_id,
            items=[
                {"plan": plan.get_stripe_id()},
            ])
        self.stripe_subscription_id = subscription.id

# Implement me
def convert_user_billing_to_org(self):
    pass

# As we build out the enterprise-style billing, we will likely blend this into a "Transaction" ledger
# Each user will have a double-entry bookkeeping ledger, and our "Provider"/"Broker" accounts will as well
class Transaction(models.Model):
    """
    A record of each credit purchase made by a user.
    """
    transaction_type = models.CharField(max_length=64, null=True, blank=True)
    billing_info = models.ForeignKey(BillingInfo, related_name="transactions", on_delete=models.DO_NOTHING, null=True, blank=True)
    ordered_by = models.ForeignKey(User, related_name="items_ordered", on_delete=models.DO_NOTHING)
    amount = models.DecimalField("Amount", max_digits=6, decimal_places=2, null=True, blank=True)
    cart_id = models.TextField(null=True, blank=True)

    transaction_details = models.TextField("Charge details", null=True, blank=True)
    external_id = models.CharField(max_length=255, null=True, blank=True)
    external_api_version = models.TextField(null=True, blank=True)
    service = models.CharField(max_length=64, null=True, blank=True)

    timestamp = models.DateTimeField(null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)

    service_timestamp = models.IntegerField(null=True, blank=True)

    data_json = models.TextField(null=True, blank=True)
    metadata_json = models.TextField(null=True, blank=True)
    
    date_created = models.DateTimeField(null=True, blank=True) 

    class Meta:
        ordering = ["-timestamp"]

    def __str__(self):
        return "{0} - {1}".format(self.service, self.external_id)

    def json(self):
        import json
        data = json.loads(self.data_json)
        return data


# @receiver(post_save, sender=Transaction)
# def increase_balance_on_credits_purchase(sender, instance, created, **kwargs):
#     """
#     Increase the user's track credit on each new Purchase.
#     """
#     billing_profile = instance.billing_info
#     billable_minutes = instance.calculate_billable_minutes()
#     if created:
#         billing_profile.track_credit = F("balance") + billable_minutes
#         billing_profile.save()


# @receiver(post_save, sender="orders.Order")
# def increase_balance_on_order_cancel(sender, instance, **kwargs):
#     """
#     Increase the user's track credit when a Track is deleted.
#     """
#     billing_profile = instance.billing_info
#     # TODO: take into consideration billing info does not exist i.e. internally created orders
#     if billing_profile:
#         billable_minutes = instance.calculate_billable_minutes()
#         billing_profile.balance = F("balance") + billable_minutes
#         billing_profile.save()


# @receiver(pre_save, sender="orders.Order")
# def decrease_balance_on_order(sender, instance, **kwargs):
#     """
#     Decrease the user's credit when an Order is created.
#     If the track credit is reduced below 0, IntegrityError will be raised
#     and the saving of the track will be prevented.
#     """
#     if instance.pk is None:  # Only fire for new objects
#         billing_profile = instance.billing_info
#         billable_minutes = instance.calculate_billable_minutes()
#         billing_profile.balance = F("balance") - billable_minutes
#         billing_profile.save()

class Product(models.Model):
    name = models.CharField(max_length=128)
    short_description = models.CharField(max_length=64)
    description = models.TextField()
    is_discountable = models.BooleanField()
    unit_of_measure = models.CharField(max_length=64)
    display_name = models.CharField(max_length=64)
    is_addon = models.BooleanField()
    base_price = models.FloatField()

    def __str__(self):
        return str(self.name)

def post_save_customer_create(sender, instance, created, *args, **kwargs):
    if created:
        stripe.api_key = settings.STRIPE_API_KEY
        billing_profile, created_status = BillingInfo.objects.get_or_create(user=instance)

        if billing_profile.stripe_customer_id is None or billing_profile.stripe_customer_id == '':
            new_customer_id = stripe.Customer.create(email=instance.email)
            billing_profile.stripe_customer_id = new_customer_id['id']
            billing_profile.save()

        analytics.identify(instance.id, {
            'email': instance.email,
            'name': "{0} {1}".format(instance.first_name, instance.last_name),
            'stripe_id': "{0}".format(billing_profile.stripe_customer_id)
        })


post_save.connect(post_save_customer_create,
                  sender=User)

def post_checkout_order_dispatch(sender, instance, created, *args, **kwargs):
    if created:
        stripe.api_key = settings.STRIPE_API_KEY
        billing_profile, created_status = BillingInfo.objects.get(user=instance.cart.ordered_by)

        analytics.identify(instance.id, {
            'email': instance.email,
            'name': "{0} {1}".format(instance.first_name, instance.last_name),
            'stripe_id': "{0}".format(billing_profile.stripe_customer_id)
        })

        for item in instance.cart.orderitem_set.all():
            pass
            # msg = item.to_pubsub_format()
            # from transport.pubsub_interface import


        # analytics.track()

# post_save.connect(post_checkout_order_dispatch,
#                  sender=Transaction)