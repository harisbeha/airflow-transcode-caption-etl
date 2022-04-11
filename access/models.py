from django.db import models
from django.contrib.auth.models import User, AbstractUser
import uuid, json


class AccountConfiguration(models.Model):
    account = models.OneToOneField(to=User, on_delete=models.DO_NOTHING)
    configuration_data = models.TextField(default=json.dumps({}))
    default_preset = models.ForeignKey('library.Entry', related_name="user_preset", on_delete=models.DO_NOTHING)
    default_notification_email = models.TextField(null=True)
    default_webhook_url = models.TextField(null=True)
    default_alert_url = models.TextField(null=True)
    notify_bad_media = models.BooleanField(default=False)
    notify_delayed = models.BooleanField(default=False)
    notify_poor_quality = models.BooleanField(default=False)
    
    def __str__(self):
        return "{}: {}".format(self.account, self.configuration_data)

    @property
    def json(self):
        return json.loads(self.configuration_data)


class AccessToken((models.Model)):
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4)
    access_token = models.TextField(db_index=True, null=False, blank=False)
    member = models.ForeignKey('orgs.OrganizationUser', on_delete=models.DO_NOTHING, related_name='access_tokens')
    created_by = models.ForeignKey(User, related_name="user_created_tokens", on_delete=models.DO_NOTHING)
    created = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    description = models.TextField(null=True, blank=True)

    def __str__(self):
        return "{}: {}".format(
            self.member.user.username,
            self.description
        )


def onboard_user(user_data):
    email = user_data.get("email", "")
    first_name = user_data.get("first_name", "")
    last_name =  user_data.get("last_name", "")
    create_single_user_org(user_data)
    create_stripe_customer_id(user_data)
    create_billing_profile_for_user(user_data)
    analytics.identify('019mr8mf4r', {
        'email': 'john@example.com',
        'name': 'John Smith',
        'friends': 30
    })
    return True

def create_billing_profile_for_user(user_data):
    pass

def create_stripe_customer_id(user_data):
    pass

def create_single_user_org(user_data):
    pass

# class TestCustomUser(AbstractUser):
#     is_customer = models.BooleanField(default=False)

#     def __str__(self):
#         return self.email