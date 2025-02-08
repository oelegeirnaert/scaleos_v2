import uuid

from django.db import models
from django.utils.translation import gettext_lazy as _


class NameField(models.Model):
    name = models.CharField(verbose_name=_("name"), max_length=100, default="")

    class Meta:
        abstract = True

    def __str__(self):
        if self.name:  # pragma: no cover
            return self.name
        return super().__str__()


class LogInfoFields(models.Model):
    created_on = models.DateTimeField(auto_now_add=True, null=True)
    modified_on = models.DateTimeField(auto_now=True, null=True)

    class Meta:
        abstract = True
        get_latest_by = ["created_on"]


class PublicKeyField(models.Model):
    public_key = models.UUIDField(unique=True, null=True, editable=False)

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        if self.public_key is None:  # pragma: no cover
            self.public_key = uuid.uuid4()

        super().save(*args, **kwargs)
