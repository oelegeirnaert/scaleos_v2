# Create your models here.
import logging

from django.db import models
from django.utils.translation import gettext_lazy as _
from ollama import Client
from polymorphic.models import PolymorphicModel

from scaleos.shared.fields import LogInfoFields
from scaleos.shared.fields import NameField
from scaleos.shared.fields import PublicKeyField
from scaleos.shared.mixins import AdminLinkMixin

logger = logging.getLogger(__name__)


# Create your models here.
class Service(
    PolymorphicModel,
    NameField,
    AdminLinkMixin,
    PublicKeyField,
    LogInfoFields,
):
    computer = models.ForeignKey(
        "hardware.Computer",
        verbose_name=_(
            "computer",
        ),
        related_name="services",
        on_delete=models.CASCADE,
        null=True,
    )

    class Meta:
        verbose_name = _("service")
        verbose_name_plural = _("services")


class OllamaService(Service):
    ai_model = models.CharField(default="mistral")
    port = models.IntegerField(default=11434)

    class Meta:
        verbose_name = _("ollama service")
        verbose_name_plural = _("ollama services")

    def client(self):
        return Client(host=f"http://{self.computer.name}:{self.port}")
