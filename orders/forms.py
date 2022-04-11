
# If you want to create a formset that allows you to edit books belonging to a particular author, you could do this:

# Cart
## OrderItem
### SelectedPresetsField

from django import forms
from . import models
from django_select2 import forms as s2forms

class PresetForm(forms.ModelForm):
    class Meta:
        model = models.Preset
        fields = [
            "name",
            "source_language",
            "turnaround_time",
            "global_default",
            "is_default",
            "target_languages",
            "speaker_id",
            "rush_12",
            "true_verbatim",
            "rush_24",
            "base_product",
            "user",
        ]


class OutputProductForm(forms.ModelForm):
    class Meta:
        model = models.OutputProduct
        fields = [
            "storage_paths",
            "entry",
            "order",
        ]
class RefactoredSelectMultipleWidget(s2forms.ModelSelect2MultipleWidget):
    def get_queryset(self):
        qs = models.Preset.objects.all()
        return qs

    def filter_queryset(self, request, term, queryset=None, **kwargs):
        # presets = Preset.objects.filter(user=request.user)
        presets = models.Preset.objects.all()
        return presets 

class OrderItemForm(forms.ModelForm):
    # presets_selected = forms.ModelMultipleChoiceField(
    # queryset=models.Preset.objects.all(),
    # label=u"Presets",
    # widget=s2forms.ModelSelect2TagWidget(
    #     model=models.Preset,
    #     search_fields=['name__icontains'],
    #     max_results=10,
    #     extra_attrs={'w-full '},
    #     css={'w-full'},
    # ))

    def __init__(self, user, *args, **kwargs):
        super(OrderItemForm, self).__init__(*args, **kwargs)
        if self.instance.entry.integration_source == "YouTube":
            self.fields['product_template'].queryset = models.Preset.objects.filter(partner="YouTube")
            self.fields['product_template'].instance = models.Preset.objects.all().filter(partner="YouTube")
        else:
            self.fields['product_template'].queryset = models.Preset.objects.all().filter(partner=None, global_default=True)
            self.fields['product_template'].instance = models.Preset.objects.all().filter(global_default=True, partner=True)
        self.fields['product_template'].widget.attrs.update(
            {
                "class": "w-full px-2 py-2 text-gray-700 bg-gray-200 rounded w-full block appearance-none bg-white border border-gray-500 rounded text-gray-800 py-1 px-4 pr-8",
                "onchange": 'updateCart();'
            }
        )
        self.fields['product_template'].label = ''

    class Meta:
        model = models.OrderItem
        fields = ['product_template']
        readonly_fields = ["entry", "media_length_ms"]
        # widgets = {
        #     'attr': RefactoredSelectMultipleWidget(model=models.Preset, search_fields=['name__icontains']),
        # }
