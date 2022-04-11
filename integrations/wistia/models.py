# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

class WistiaAuth(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.DO_NOTHING,
        related_name="zoom_user_profiles")
    api_key = models.TextField()

    auto_import = models.BooleanField()
    auto_import_interval = models.CharField(max_length=12)

    auto_import_max_daily = models.IntegerField(default=50)
    auto_import_meetings = models.BooleanField()
    auto_import_webinars = models.BooleanField()
