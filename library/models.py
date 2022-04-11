from django.db import models
from django.contrib.auth.models import User

import django_tables2 as tables

from django.utils.safestring import mark_safe

class ThumbnailColumn(tables.Column):
    def render(self, value):
        return mark_safe(value)

class TruncatedTextColumn(tables.Column):
    def render(self, value):
        formatted_value = (value[:64] + '..') if len(value) > 64 else value
        return mark_safe(formatted_value)

class EntryTable(tables.Table):
    id = tables.CheckBoxColumn(accessor='id', attrs={"td": {"class": "px-5 py-5 border-b border-gray-200 bg-white text-sm"}, "th": {"id": "select-all", "class": "px-5 py-3 border-b-2 border-gray-200 bg-gray-100 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider"}})
    video_id = TruncatedTextColumn(accessor='external_id', attrs={"td": {"class": "px-5 py-5 border-b border-gray-200 bg-white text-sm"}, "th": {"class": "px-5 py-3 border-b-2 border-gray-200 bg-gray-100 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider"}})
    integration_source = TruncatedTextColumn(accessor='integration_source', attrs={"td": {"class": "px-5 py-5 border-b border-gray-200 bg-white text-sm"}, "th": {"class": "px-5 py-3 border-b-2 border-gray-200 bg-gray-100 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider"}})
    channel_title = TruncatedTextColumn(accessor='channel_title', attrs={"td": {"class": "px-5 py-5 border-b border-gray-200 bg-white text-sm"},"th": {"class": "px-5 py-3 border-b-2 border-gray-200 bg-gray-100 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider"}})
    thumbnail_url = ThumbnailColumn(accessor='thumbnail_html', attrs={"td": {"class": "px-5 py-5 border-b border-gray-200 bg-white text-sm"}, "th": {"class": "px-5 py-3 border-b-2 border-gray-200 bg-gray-100 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider"}})
    published_at = tables.DateTimeColumn(accessor='published_at', attrs={"td": {"class": "px-5 py-5 border-b border-gray-200 bg-white text-sm"},"th": {"class": "px-5 py-3 border-b-2 border-gray-200 bg-gray-100 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider"}})
    title = TruncatedTextColumn(accessor='title', attrs={"td": {"class": "px-5 py-5 border-b border-gray-200 bg-white text-sm"},"th": {"class": "px-5 py-3 border-b-2 border-gray-200 bg-gray-100 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider"}})
    media_length_ms = tables.Column(accessor='media_length_ms', attrs={"td": {"class": "px-5 py-5 border-b border-gray-200 bg-white text-sm"}, "th": {"class": "px-5 py-3 border-b-2 border-gray-200 bg-gray-100 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider"}})


    class Meta:
        template_name = "django_tables2/tailwind.html"
        fields = ('id', 'published_at', 'title', 'media_length_ms', 'thumbnail_url')
        attrs = {"class": "min-w-full leading-normal shadow rounded-md"}
        sequence = ('id', 'thumbnail_url', 'published_at', 'video_id', 'channel_title', 'title')

class OrderTable(tables.Table):
    id = tables.CheckBoxColumn(accessor='entry.id', attrs={"td": {"class": "px-5 py-5 border-b border-gray-200 bg-white text-sm"}, "th": {"id": "select-all", "class": "px-5 py-3 border-b-2 border-gray-200 bg-gray-100 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider"}})
    thumbnail_html = ThumbnailColumn(accessor='entry.thumbnail_html', attrs={"td": {"class": "px-5 py-5 border-b border-gray-200 bg-white text-sm"}, "th": {"class": "px-5 py-3 border-b-2 border-gray-200 bg-gray-100 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider"}})
    title = TruncatedTextColumn(accessor='entry.title', attrs={"td": {"class": "px-5 py-5 border-b border-gray-200 bg-white text-sm"},"th": {"class": "px-5 py-3 border-b-2 border-gray-200 bg-gray-100 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider"}})
    media_length_ms = tables.Column(accessor='media_length_ms', attrs={"td": {"class": "px-5 py-5 border-b border-gray-200 bg-white text-sm"}, "th": {"class": "px-5 py-3 border-b-2 border-gray-200 bg-gray-100 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider"}})
    completed = tables.DateTimeColumn(accessor='cart.completed', attrs={"td": {"class": "px-5 py-5 border-b border-gray-200 bg-white text-sm"},"th": {"class": "px-5 py-3 border-b-2 border-gray-200 bg-gray-100 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider"}})
    product = tables.Column(accessor='product_template.name', attrs={"td": {"class": "px-5 py-5 border-b border-gray-200 bg-white text-sm"}, "th": {"class": "px-5 py-3 border-b-2 border-gray-200 bg-gray-100 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider"}})
    status = tables.Column(accessor='status', attrs={"td": {"class": "px-5 py-5 border-b border-gray-200 bg-white text-sm"}, "th": {"class": "px-5 py-3 border-b-2 border-gray-200 bg-gray-100 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider"}})
    payment_status = tables.Column(accessor='payment_status', attrs={"td": {"class": "px-5 py-5 border-b border-gray-200 bg-white text-sm"}, "th": {"class": "px-5 py-3 border-b-2 border-gray-200 bg-gray-100 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider"}})

    class Meta:
        template_name = "django_tables2/tailwind.html"
        fields = ('id', 'title', 'media_length_ms', 'thumbnail_html', 'product', 'status', 'payment_status')
        attrs = {"class": "min-w-full leading-normal shadow rounded-md"}
        sequence = ('id', 'thumbnail_html', 'title')



# Thumbnail, OrderID, Product, Title, VideoID, Status, MediaLength, ViewDetails

# Turn into a timestamped model
class Entry(models.Model):
    user = models.ForeignKey(User, related_name="user_entries", on_delete=models.DO_NOTHING)
    title = models.CharField(max_length=255, null=True, blank=True)
    description = models.CharField(max_length=255, null=True, blank=True)
    media_url = models.CharField(max_length=255, null=True, blank=True)
    thumbnail_url = models.CharField(max_length=255, null=True, blank=True)
    thumbnail_html = models.CharField(max_length=255, null=True, blank=True)
    # From Metadata
    metadata_media_length_ms = models.IntegerField(default=0)
    # Actual length
    published_at = models.DateTimeField(null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    media_length_ms = models.IntegerField(default=0)
    integration_source = models.CharField(max_length=255)
    external_id = models.CharField(max_length=255, null=True, blank=True)
    import_status = models.CharField(max_length=255, default="NOT IMPORTED")
    seo_metadata = models.TextField(null=True, blank=True)
    channel_title = models.TextField(null=True, blank=True)
    email = models.TextField(null=True, blank=True)

    # Get OrderItem summary for Entry
    def get_order_summary_for_entry(self):
        from orders.models import OrderItem
        order_summary = OrderItem.objects.filter(cart__user=self.user, entry=self).values("name", "job_type", "presets_selected",)
        return order_summary

    # Get OutputProduct summary for Entry
    def get_output_product_summary(self):
        from orders.models import OutputProduct
        output_products = OutputProduct.objects.filter(entry=self).values_list("storage_data")
        return output_products

    # create OrderItem from Entry
    def create_order_item_from_entry(self):
        order = OrderItem.get_or_create(entry=self, )
        return order

    # TODO Actually pull data for this
    def has_orders(self):
        return False