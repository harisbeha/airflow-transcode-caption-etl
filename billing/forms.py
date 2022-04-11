
from django import forms
from billing.models import BillingInfo

class BillingInfoForm(forms.ModelForm):

    class Meta:
        model = BillingInfo
        fields = '__all__'
        # fields = ("name", "company", "address_one", "address_two", "city", "state", "postal_code", "country",)
