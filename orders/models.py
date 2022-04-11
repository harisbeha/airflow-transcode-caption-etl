from django.contrib.auth.models import User
from django.db import models
from django.db.models.manager import Manager
from datetime import timedelta
import json, uuid

from service.enums import OrderStatus, OrderType

from django.db import models
from django.utils.translation import ugettext_lazy as _
from datetime import datetime, timedelta
from uuid import uuid4


class CompletedCartManager(Manager):
    def get_queryset(self):
        return super(CompletedCartManager, self).get_queryset().exclude(order_status=OrderStatus.REJECTED.value).exclude(deleted=True)

class PendingCartManager(Manager):
    def get_queryset(self):
        return super(PendingCartManager, self).get_queryset().exclude(order_status=OrderStatus.PENDING.value).exclude(deleted=True)

class AbandonedCartManager(Manager):
    def get_queryset(self):
        return super(AbandonedCartManager, self).get_queryset().exclude(order_status=OrderStatus.REJECTED.value).exclude(deleted=True)

class RejectedCartManager(Manager):
    def get_queryset(self):
        return super(RejectedCartManager, self).get_queryset().filter(order_status=OrderStatus.PENDING)

    def abandon_cart(self):
        self.abandoned = datetime.now()
        self.order_status = OrderStatus.PENDING
        self.save()

    def reject_order(self):
        self.order_status = OrderStatus.PENDING
        self.save()

class Cart(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, primary_key=True) # Doubles as an idempotency key
    user = models.ForeignKey(User, related_name="user_carts", on_delete=models.DO_NOTHING)
    requested_by = models.ForeignKey(User, on_delete=models.DO_NOTHING, related_name='orders', null=True, blank=True)
    billing_info = models.ForeignKey("billing.BillingInfo", on_delete=models.DO_NOTHING, null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    checked_out = models.BooleanField(default=False)
    completed_date = models.DateTimeField(null=True, blank=True)
    payment_id = models.CharField(max_length=255, null=True, blank=True)
    abandoned = models.DateTimeField(verbose_name=_('abandoned date'), default=None, blank=True, null=True)
    payment_status = models.CharField(max_length=64, null=True, blank=True)

    objects = Manager()

    # Custom Managers
    completed_orders = CompletedCartManager()
    pending_orders = PendingCartManager()
    rejected_carts = RejectedCartManager()
    abandoned_carts = AbandonedCartManager()

    class Meta:
        verbose_name = _('cart')
        verbose_name_plural = _('carts')
        ordering = ('-created',)
        
    def calculate_subtotal(self):
        pass

    def calculate_total(self):
        pass

    def is_empty(self):
        return not self.orderitem_set.exists()

class Preset(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, primary_key=True)
    user = models.ForeignKey(User, related_name="user_presets", on_delete=models.DO_NOTHING, null=True, blank=True)
    name = models.CharField(max_length=255)
    source_language = models.CharField(max_length=255, null=True, default="en")
    target_languages = models.CharField(max_length=255, null=True, default="en")
    turnaround_time = models.CharField(max_length=255, default="STD")
    base_product = models.ForeignKey("billing.Product", on_delete=models.DO_NOTHING)
    rush_12 = models.BooleanField(default=False)
    rush_24 = models.BooleanField(default=False)
    true_verbatim = models.BooleanField(default=False)
    speaker_id = models.BooleanField(default=False)
    job_type = models.CharField(max_length=255, default="TX")
    is_default = models.BooleanField(default=False)
    price = models.FloatField(default=1.00)
    global_default = models.BooleanField(default=False)
    partner = models.CharField(max_length=255, null=True, blank=True)
    discount_per_minute = models.DecimalField(decimal_places=2, null=True, blank=True, max_digits=3)

    def __str__(self):
        label = "{0} (${1:.2f})".format(self.name, self.calculate_non_discounted_price())
        return label

    def get_pricing_matrix(self):
        return {}

    def get_base_price_for_job_type(self):
        return 1.0

    def get_addon_price(self, addon=None):
        return 1.0

    def get_addon_price_matrix(self):
        return {}

    def has_language_surcharge(self):
        return False

    def calculate_non_discounted_price(self):
        base_price = self.get_base_price_for_job_type()

        # Eliminate Rush12 for now
        # rush_12_cost = self.get_addon_price("rush_12")
        rush_24_cost = self.get_addon_price("rush_24")
        true_verbatim_cost = self.get_addon_price("true_verbatim")
        speaker_id_cost = self.get_addon_price("speaker_id")

        calculated_price = 0.0

        # Start with base price
        calculated_price += float(base_price)

        # If Rushed, add surcharge
        if self.rush_24:
            calculated_price += float(rush_24_cost)

        if self.speaker_id:
            calculated_price += float(speaker_id_cost)

        if self.true_verbatim:
            calculated_price += float(true_verbatim_cost)
        # return calculated_price
        return float(self.price)

class OrderItem(models.Model):
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    presets_selected = models.ManyToManyField(Preset, related_name="order_presets", null=True, blank=True)
    product_template = models.ForeignKey(Preset, related_name="product_template", null=True, on_delete=models.DO_NOTHING)
    # "Quantity"
    media_length_ms = models.IntegerField(default=0)
    entry = models.ForeignKey('library.Entry', on_delete=models.DO_NOTHING)
    cart = models.ForeignKey(Cart, on_delete=models.DO_NOTHING, null=True, blank=True)
    final_price = models.FloatField(default=0.00)
    status = models.CharField(max_length=255, blank=True, null=True, default='Pending')
    payment_status = models.CharField(max_length=255, blank=True, null=True, default='Payment Pending')

    def __str__(self):
        return self.entry.title or self.entry.external_id

    @property
    def minutes(self):
        minutes = float(self.media_length_ms) / float(60000.00)
        return minutes 

    def get_order_item_user(self):
        return self.cart.user
    
    @property
    def has_completed_product(self):
        return self.outputproduct_set.exists()

    @property
    def calculated_price(self):
        price = float(self.product_template.price) * float(self.minutes)
        return price
    
    @property
    def calculated_savings(self):
        savings = 0.0
        if self.product_template.discount_per_minute:
            calculated = float(self.product_template.discount_per_minute) * float(self.minutes)
            savings += calculated
        return savings

    @property
    def has_completed_product(self):
        return self.outputproduct_set.exists()

class OutputProduct(models.Model):
    """
    storage_paths should look something like this
    (if the client ordered a certain format the download link will be present)
    {
        "final_elementlist": "https://url-goes-here.com",
        "dfxp": "https://url-goes-here.com",
        "audio_descriptoin_audio_file": "https://url-goes-here.com"
        ...
    }
    """
    entry = models.ForeignKey("library.Entry", related_name="order_entries", on_delete=models.DO_NOTHING)
    order = models.ForeignKey(OrderItem, related_name="order_output_products", on_delete=models.DO_NOTHING)
    progress = models.IntegerField(default=0)
    status = models.CharField(max_length=255, blank=True, null=True, default='DISPATCHED')
    storage_paths = models.TextField(default=json.dumps({}))

    @property
    def json(self):
        return json.loads(self.storage_paths)
