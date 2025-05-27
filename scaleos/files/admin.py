# admin.py

from django.contrib import admin
from polymorphic.admin import PolymorphicChildModelAdmin
from polymorphic.admin import PolymorphicParentModelAdmin

from scaleos.files import models as file_models


class BaseFileChildAdmin(PolymorphicChildModelAdmin):
    base_model = file_models.BaseFile


@admin.register(file_models.ImageFile)
class ImageFileAdmin(BaseFileChildAdmin):
    list_display = ("name", "file", "is_vector", "width", "height")
    readonly_fields = ["checksum", "created_on"]


@admin.register(file_models.AudioFile)
class AudioFileAdmin(BaseFileChildAdmin):
    list_display = ("name", "file", "duration", "artist", "album")


@admin.register(file_models.DocumentFile)
class DocumentFileAdmin(BaseFileChildAdmin):
    list_display = ("name", "file", "doc_type")


@admin.register(file_models.VideoFile)
class VideoFileAdmin(BaseFileChildAdmin):
    list_display = ("name", "source", "video", "url", "duration")


@admin.register(file_models.BaseFile)
class BaseFileAdmin(PolymorphicParentModelAdmin):
    base_model = file_models.BaseFile
    child_models = (
        file_models.ImageFile,
        file_models.AudioFile,
        file_models.DocumentFile,
        file_models.VideoFile,
    )
    list_display = ("name", "file", "created_on")
    readonly_fields = ["checksum", "created_on"]
