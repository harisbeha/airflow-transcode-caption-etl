from django.db import models


DEFAULT_MESSAGE = "PENDING"

class OrderStatus(models.TextChoices):
    PENDING = DEFAULT_MESSAGE.format("PENDING"), "PENDING"
