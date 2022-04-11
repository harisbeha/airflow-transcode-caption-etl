from django import forms
from integrations.youtube.models import GoogleAPIOauthInfo

class YouTubeSettingsForm(forms.ModelForm):
    class Meta:
        model = GoogleAPIOauthInfo
        exclude = []
        # fields = ["auto_import", "auto_import_interval", "auto_import_max_daily", "auto_import_meetings", "auto_import_webinars"]