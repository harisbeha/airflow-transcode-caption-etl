def get_standard_preset(user):
    from orders.models import Preset
    standard_preset = Preset.objects.get(global_default=True, user=user)
    return standard_preset