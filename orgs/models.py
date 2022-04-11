from django.db import models
from django.contrib.auth.models import User
import uuid


def hex_uuid():
    return uuid.uuid4().hex


class Organization(models.Model):
    name = models.CharField(max_length=256, db_index=True, null=False, blank=False)
    invoice_to = models.CharField(max_length=256)
    org_id = models.CharField(max_length=64, default=hex_uuid)
    is_legacy_customer = models.BooleanField(default=False)
    usage_tracking_method = models.CharField(max_length=128, null=True, blank=True)
    external_service = models.CharField(max_length=128, null=True, blank=True)
    external_service_id = models.CharField(max_length=128, null=True, blank=True, db_index=True)

    def __str__(self):
        return self.name


class OrganizationUser(models.Model):
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING, related_name="orgs")
    organization = models.ForeignKey(Organization, on_delete=models.DO_NOTHING, related_name="org_users")
    scopes = models.TextField()

    def __str__(self):
        return "{}: {}".format(self.organization.name, self.user.username)
