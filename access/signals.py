from django.dispatch import receiver
from django.db.models import signals
from django.contrib.auth.models import User
from access.models import AccountConfiguration


@receiver(signals.post_save, sender=User)
def account_configuration_signal(sender, **kwargs):
    instance = kwargs['instance']
    AccountConfiguration.objects.get_or_create(account=instance)
