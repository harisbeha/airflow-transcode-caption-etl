from django.contrib import admin
from reversion.admin import VersionAdmin

from orders.models import Cart, OutputProduct, OrderItem, Preset
from django.forms import Form, ModelForm

admin.site.register(Cart)
admin.site.register(OrderItem)


class PresetAdminForm(ModelForm):

    class Meta:
        model = Preset
        fields = "__all__"

@admin.register(Preset)
class PresetAdmin(admin.ModelAdmin):
    form = PresetAdminForm
    list_display = [
        "name",
        "job_type",
        "source_language",
        "turnaround_time",
        "global_default",
        "is_default",
        "target_languages",
        "speaker_id",
        "rush_12",
        "true_verbatim",
        "rush_24",
    ]
    # readonly_fields = [
    #     "name",
    #     "source_language",
    #     "turnaround_time",
    #     "global_default",
    #     "is_default",
    #     "target_languages",
    #     "speaker_id",
    #     "rush_12",
    #     "true_verbatim",
    #     "rush_24",
    # ]


@admin.register(OutputProduct)
class OutputProductAdmin(VersionAdmin):
    pass

