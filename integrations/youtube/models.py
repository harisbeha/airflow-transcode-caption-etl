from django.db import models
from django.contrib.auth.models import User

class GoogleAPIOauthInfo(models.Model):
    access_token = models.TextField()
    refresh_token = models.TextField(null=True, blank=True)
    credentials = models.TextField(null=True, blank=True)
    expiry = models.TextField(null=True, blank=True)
    refresh_token = models.TextField()
    auth_token = models.TextField()
    scopes = models.TextField()
    user = models.ForeignKey(
    User,
    on_delete=models.DO_NOTHING,
    related_name="youtube_user_profiles")