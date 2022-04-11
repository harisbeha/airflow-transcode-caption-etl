from django.db import models


DEFAULT_MESSAGE = "User does not have permission to complete action: {}"
DEFAULT_VIEW_ERROR_RESPONSE = "If you feel like you received this message in error, please contact your support admin"


class APIKeyErrorCodes(models.TextChoices):
    LIST = DEFAULT_MESSAGE.format("list:api-keys"), "List"
    GET = DEFAULT_MESSAGE.format("get:api-keys"), "Get"
    UPDATE = DEFAULT_MESSAGE.format("update:api-keys"), "Update"
    DISABLE = DEFAULT_MESSAGE.format("disable:api-keys"), "Disable"
    CREATE = DEFAULT_MESSAGE.format("create:api-keys"), "Create"


class WorkflowTrackerEnum(models.TextChoices):
    PENDING = "PENDING", "Pending"
    IN_PROGRESS = "IN_PROGRESS", "In Progress"
    DELETED = "DELETED", "Deleted"
    ERROR = "ERROR", "Error"
    FINALIZING = "FINALIZING", "Finalizing"
    COMPLETE = "COMPLETE", "Complete"


class OrderStatus(models.TextChoices):
    IMPORTED = "IMPORTED", "Imported"
    PENDING = "PENDING", "Pending"
    LOW_BALANCE = "LOW_BALANCE", "Low Balance"
    REJECTED = "REJECTED", "Rejected"
    SUBMITTED = "SUBMITTED", "Submitted"
    COMPLETE = "COMPLETE", "Complete"


class AddOns(models.TextChoices):
    SPEAKER_ID = 'SPEAKER_ID', 'Speaker ID'
    TRUE_VERBATIM = 'TRUE_VERBATIM', 'True Verbatim'


class OrderType(models.TextChoices):
    STANDARD = "STANDARD", "Standard"
    MACHINE = "MACHINE", "Machine"
    AUDIO_DESCRIPTION = "AUDIO_DESCRIPTION", "Audio Description"
    TRANSLATION = "TRANSLATION", "Translation"
    FOREIGN_TRANSCRIPTION = "FOREIGN_TRANSCRIPTION", "Foreign Transcription"


class AD_TYPE(models.TextChoices):
    GENERATE_MANIFEST = 'GENERATE_MANIFEST', 'Generate Manifest'
    SYNTHESIZE_AUDIO = 'SYNTHESIS_AUDIO', 'Synthesize Audio'


class ExpediteEnum(models.TextChoices):
    STANDARD = 72, '72 Hours'
    ONE_DAY = 24, '24 Hours'
    TWO_DAYS = 48, '48 Hours'


class LanguageEnum(models.TextChoices):
    ARABIC = 'ar', 'Arabic'
    CANTONESE = 'zh-yue', 'Cantonese (Traditional)'
    DUTCH = 'nl', 'Dutch'
    ENGLISH = 'en', 'English'
    FRENCH = 'fr', 'French'
    CANADIAN_FRENCH = 'fr-ca', 'French (Canadian)'
    FINNISH = 'fi', 'Finnish'
    GERMAN = 'de', 'German'
    GREEK = 'gr', 'Greek'
    HEBREW = 'he', 'Hebrew'
    HINDI = 'hi', 'Hindi'
    ITALIAN = 'it', 'Italian'
    INDONESIAN = 'id', 'Indonesian'
    JAPANESE = 'ja', 'Japanese'
    KOREAN = 'ko', 'Korean'
    MALAY = 'ma', 'Malay'
    MANDARIN_SIMPLE = 'zh-cmn', 'Mandarin (Simplified)'
    MANDARIN_TRADITIONAL = 'zh-tw', 'Mandarin (Traditional)'
    NORWEGIAN = 'no', 'Norwegian'
    POLISH = 'pl', 'Polish'
    PORTUGUESE = 'pt', 'Portuguese'
    PORTUGAL_PORTUGUESE = 'pt-pt', 'Portuguese (Portugal)'
    RUSSIAN = 'ru', 'Russian'
    SWEDISH = 'se', 'Swedish'
    SLOVAK = 'sk', 'Slovak'
    SPANISH = 'es', 'Spanish'
    SPAIN_SPANISH = 'es-es', 'Spanish (Spain)'
    THAI = 'th', 'Thai'
    TURKISH = 'tr', 'Turkish'
    VIETNAMESE = 'vn', 'Vietnamese'
