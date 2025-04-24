import uuid

from autoslug import AutoSlugField
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils.functional import cached_property
from django.utils.translation import gettext_lazy as _


class NameField(models.Model):
    name = models.CharField(
        verbose_name=_("name"),
        max_length=100,
        default="",
        blank=True,
    )
    slug = AutoSlugField(populate_from="name", null=True, unique=True)

    class Meta:
        abstract = True

    def __str__(self):
        if self.name:  # pragma: no cover
            return self.name
        return super().__str__()


class LogInfoFields(models.Model):
    created_on = models.DateTimeField(auto_now_add=True, null=True)
    modified_on = models.DateTimeField(auto_now=True, null=True)
    created_by = models.ForeignKey(
        get_user_model(),
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    modified_by = models.ForeignKey(
        get_user_model(),
        related_name="%(class)s_modifications",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )

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

    @cached_property
    def html_public_key(self):
        """Prefixed because a html id may not start with a number"""
        return f"htmlPK{str(self.public_key).replace('-', '')}"


class OriginFields(models.Model):
    origin_content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    origin_object_id = models.PositiveIntegerField(null=True, blank=True)
    origin = GenericForeignKey("origin_content_type", "origin_object_id")

    class Meta:
        abstract = True
