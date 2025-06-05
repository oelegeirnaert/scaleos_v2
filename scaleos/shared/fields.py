import uuid

from autoslug import AutoSlugField
from cryptography.fernet import InvalidToken
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils.functional import cached_property
from django.utils.translation import gettext_lazy as _

from scaleos.shared.encryption import KeyManager


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

    @cached_property
    def public_reference(self):
        if self.public_key is None:
            return None
        trans_reference = _("reference")
        return f"{trans_reference.capitalize()}: {self.verbose_name.title()} #{
            str(self.public_key).split('-')[0].upper()
        }"


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


class SegmentField(models.Model):
    class SegmentType(models.TextChoices):
        B2B = "B2B", _("b2b")
        B2C = "B2C", _("b2c")
        BOTH = "BOTH", _("both")

    segment = models.CharField(
        verbose_name=_(
            "segment",
        ),
        max_length=50,
        choices=SegmentType.choices,
        default=SegmentType.BOTH,
    )

    class Meta:
        abstract = True

    @property
    def segment_name(self):
        if self.segment == self.SegmentType.B2B:
            return _("businesses")
        if self.segment == self.SegmentType.B2C:
            return _("private individuals")
        if self.segment == self.SegmentType.BOTH:
            return _("everyone")
        return self.get_segment_display()


class EncryptedTextField(models.TextField):
    """
    Custom Django field that encrypts text using Fernet before saving,
    and decrypts it when loading.
    """

    def get_prep_value(self, value):
        if value is None:
            return value
        f = KeyManager.get_fernet()
        return f.encrypt(value.encode()).decode()

    def from_db_value(self, value, expression, connection):
        if value is None:
            return value
        f = KeyManager.get_fernet()
        return f.decrypt(value.encode()).decode()

    def to_python(self, value):
        if value is None or isinstance(value, str):
            try:
                f = KeyManager.get_fernet()
                return f.decrypt(value.encode()).decode()
            except InvalidToken:
                return value  # Raw value in forms/admin
        return value
