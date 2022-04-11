from django import forms
from access.models import AccountConfiguration

class AccountSettingsForm(forms.ModelForm):
    class Meta:
        model = AccountConfiguration
        fields = ["default_preset", "default_webhook_url", "default_alert_url", "default_notification_email", "notify_delayed", "notify_poor_quality", "notify_bad_media"]
