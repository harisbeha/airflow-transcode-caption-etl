from django.db import models


DEFAULT_MESSAGE = "PENDING"

class WorkflowTrackerEnum(models.TextChoices):
    PENDING = DEFAULT_MESSAGE.format("PENDING"), "PENDING"
