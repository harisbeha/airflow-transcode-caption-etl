from django import forms
from integrations.wistia.models import WistiaAuth

class WistiaAuthForm(forms.ModelForm):
    class Meta:
        model = WistiaAuth
        fields = ["api_key", "auto_import", "auto_import_interval", "auto_import_max_daily"]
