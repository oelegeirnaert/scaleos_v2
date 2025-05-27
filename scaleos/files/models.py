import hashlib

from django.db import models
from django.utils.translation import gettext_lazy as _
from polymorphic.models import PolymorphicModel

from scaleos.shared.fields import LogInfoFields
from scaleos.shared.fields import NameField
from scaleos.shared.fields import PublicKeyField
from scaleos.shared.mixins import AdminLinkMixin


class BaseFile(
    PolymorphicModel,
    AdminLinkMixin,
    NameField,
    PublicKeyField,
    LogInfoFields,
):
    organization = models.ForeignKey(
        "organizations.Organization",
        on_delete=models.CASCADE,
        related_name="files",
        null=True,
        blank=False,
    )

    file = models.FileField(upload_to="uploads/%Y/%m/%d/", blank=True, null=True)
    checksum = models.CharField(max_length=64, blank=True, editable=False)

    class Meta:
        verbose_name = _("file")
        verbose_name_plural = _("files")

    def get_checksum(self):
        self.file.open()
        h = hashlib.sha256()
        for chunk in self.file.chunks():
            h.update(chunk)
        self.file.close()
        return h.hexdigest()


class ImageFile(BaseFile):
    image = models.ImageField(upload_to="uploads/images/", blank=True, null=True)
    is_vector = models.BooleanField(default=False)
    width = models.PositiveIntegerField(null=True, blank=True)
    height = models.PositiveIntegerField(null=True, blank=True)


class AudioFile(BaseFile):
    duration = models.FloatField(null=True, blank=True)  # in seconds
    artist = models.CharField(max_length=255, default="", blank=True)
    album = models.CharField(max_length=255, default="", blank=True)


class DocumentFile(BaseFile):
    class FileType(models.TextChoices):
        WORD = "WORD", _("word")
        EXCEL = "EXCEL", _("excel")
        PDF = "PDF", _("pdf")
        PPT = "PPT", _("powerpoint")
        UNKNOWN = "UNKNOWN", _("unknown")

    doc_type = models.CharField(
        max_length=10,
        choices=FileType.choices,
        default=FileType.UNKNOWN,
        blank=True,
    )


class VideoFile(BaseFile):
    # Either a video file or a URL must be provided
    class VideoSource(models.TextChoices):
        UPLOADED = "upload", _("Self-hosted")
        YOUTUBE = "youtube", _("YouTube")
        VIMEO = "vimeo", _("Vimeo")
        OTHER = "other", _("Other")

    video = models.FileField(
        upload_to="uploads/videos/",
        blank=True,
        null=True,
        help_text="Upload a video file",
    )
    url = models.URLField(
        blank=True,
        default="",
        help_text="External video URL (YouTube, Vimeo, etc.)",
    )
    duration = models.FloatField(
        null=True,
        blank=True,
        help_text="Duration in seconds (auto-extracted if self-hosted)",
    )
    source = models.CharField(
        max_length=50,
        choices=VideoSource.choices,
        default="",
        blank=True,
    )

    def clean(self):
        from django.core.exceptions import ValidationError

        if not self.video and not self.url:
            msg = _("you must provide either a video file or a URL.")
            raise ValidationError(msg)
        if self.video and self.url:
            msg = _("Provide either a video file or a URL, not both.")
            raise ValidationError(msg)

    def __str__(self):
        return self.name or self.video.name or self.url
