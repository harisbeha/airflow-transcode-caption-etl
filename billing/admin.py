from django.contrib import admin

from billing.models import Product, Plan, Transaction, BillingInfo

admin.site.register(Product)
admin.site.register(Plan)
admin.site.register(Transaction)
admin.site.register(BillingInfo)
