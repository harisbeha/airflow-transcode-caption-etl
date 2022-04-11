from django.forms import forms, widgets, fields
from service import enums
from api import utils

from orgs.models import OrganizationUser


class BaseOrderForm(forms.Form):
    specific_order_type = None
    title = fields.CharField(max_length=64, label='Title', required=False)
    media_url = fields.URLField(max_length=1024, label="Media Url", required=True)
    add_ons = fields.MultipleChoiceField(choices=enums.AddOns.choices, required=False, label='Add-Ons')
    expedite = fields.ChoiceField(
        choices=enums.ExpediteEnum.choices,
        initial=(enums.ExpediteEnum.STANDARD.value, enums.ExpediteEnum.STANDARD.label),
        required=False,
        label='Expedite'
    )
    language = fields.ChoiceField(
        choices=enums.LanguageEnum.choices,
        initial=(enums.LanguageEnum.ENGLISH.value, enums.LanguageEnum.ENGLISH.label),
        required=True,
        label='Language'
    )
    idempotency_key = fields.CharField(max_length=128, label='Idempotency Key', required=False)

    def __init__(self, requesting_user, *args, **kwargs):
        self.organziation_user = self._get_org_user(requesting_user)
        super(BaseOrderForm, self).__init__(*args, **kwargs)

    def _get_org_user(self, requesting_user):
        return OrganizationUser.objects.filter(user=requesting_user).first()

    def clean(self):
        cleaned_data = super(BaseOrderForm, self).clean()
        order_type = self.specific_order_type if self.specific_order_type else cleaned_data.get('order_type')
        turn_around_hours = cleaned_data.pop('expedite')

        order_details = {}
        source_language, target_languages = self._get_languages(cleaned_data)
        order_details['source_language'] = source_language
        order_details['target_languages'] = target_languages

        add_ons = self._get_add_ons(cleaned_data)
        if add_ons:
            order_details['add_ons'] = add_ons

        audio_description_type = self._get_ad_type(cleaned_data)
        if audio_description_type:
            order_details['audio_description_output_type'] = audio_description_type

        for field, value in cleaned_data.items():
            order_details[field] = value
        order_details['media_url'] = cleaned_data['media_url']

        order_details = utils.decipher_order(order_details, self.organziation_user)
        return dict(
            order_type=order_type,
            turn_around_hours=turn_around_hours,
            order_details=order_details,
            requested_by=self.organziation_user.id,
            organization=self.organziation_user.organization.id
        )

    @staticmethod
    def _get_languages(cleaned_data):
        language = cleaned_data.pop('language')
        source_language = language
        target_language = language
        return source_language, target_language

    @staticmethod
    def _get_add_ons(cleaned_data):
        print(cleaned_data.get('add_ons'))
        return cleaned_data.get('add_ons')

    def _get_ad_type(self, cleaned_data):
        return None


class TranscriptionOrderForm(BaseOrderForm):
    order_type = fields.ChoiceField(
        choices=[(enums.OrderType.STANDARD.value, enums.OrderType.STANDARD.label), (enums.OrderType.MACHINE.value, enums.OrderType.MACHINE.label), (enums.OrderType.FOREIGN_TRANSCRIPTION.value, enums.OrderType.FOREIGN_TRANSCRIPTION.label)],
        initial=(enums.OrderType.STANDARD.value, enums.OrderType.STANDARD.label),
        required=True
    )


class TranslationOrderForm(BaseOrderForm):
    order_type = None
    true_verbatim = None
    speaker_id = None
    specific_order_type = enums.OrderType.STANDARD.value
    target_languages = fields.MultipleChoiceField(
        choices=enums.LanguageEnum.choices,
        # widget=widgets.CheckboxSelectMultiple(),
        initial=(enums.LanguageEnum.SPANISH.value, enums.LanguageEnum.SPANISH.label)
    )

    @staticmethod
    def _get_languages(cleaned_data):
        return cleaned_data.pop('language'), cleaned_data.pop('target_languages')


class AudioDescriptionOrderForm(BaseOrderForm):
    order_type=None
    true_verbatim = None
    speaker_id = None
    specific_order_type = enums.OrderType.AUDIO_DESCRIPTION.value
    audio_description_output_type = fields.ChoiceField(
        choices=enums.AD_TYPE.choices,
        initial=(enums.AD_TYPE.GENERATE_MANIFEST.value, enums.AD_TYPE.GENERATE_MANIFEST.label),
        label='Audio Description Output Type')
    language = fields.ChoiceField(
        choices=enums.LanguageEnum.choices,
        initial=(enums.LanguageEnum.ENGLISH.value, enums.LanguageEnum.ENGLISH.label),
        required=False,
        label='Language', disabled=True
    )

    def __init__(self, *args, **kwargs):
        super(AudioDescriptionOrderForm, self).__init__(*args, **kwargs)

    def _get_ad_type(self, cleaned_data):
        return cleaned_data['audio_description_output_type']
