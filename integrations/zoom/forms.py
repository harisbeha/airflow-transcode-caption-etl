from django import forms
from integrations.zoom.models import ZoomAuth

class ZoomSettingsForm(forms.ModelForm):
    class Meta:
        model = ZoomAuth
        fields = ["auto_import", "auto_import_interval", "auto_import_max_daily", "auto_import_meetings", "auto_import_webinars"]