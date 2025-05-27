import io

import factory
from django.core.files.uploadedfile import SimpleUploadedFile
from factory.django import DjangoModelFactory
from PIL import Image

from scaleos.files import models as file_models


class BaseFileFactory(DjangoModelFactory[file_models.BaseFile]):
    class Meta:
        model = file_models.BaseFile

    file = factory.LazyAttribute(
        lambda o: SimpleUploadedFile("test.txt", b"test content"),
    )


class ImageFileFactory(BaseFileFactory):
    class Meta:
        model = file_models.ImageFile

    @factory.lazy_attribute
    def file(self):
        # Create a 1x1 pixel PNG image in memory
        img_io = io.BytesIO()
        img = Image.new("RGBA", (1, 1), (255, 0, 0, 255))  # red pixel
        img.save(img_io, format="PNG")
        img_io.seek(0)

        return SimpleUploadedFile(
            "test.png",
            img_io.read(),
            content_type="image/png",
        )

    @factory.lazy_attribute
    def image(self):
        # Create a 1x1 pixel JPG image in memory
        img_io = io.BytesIO()
        img = Image.new("RGB", (1, 1), (255, 0, 0))  # red pixel, no alpha for JPG
        img.save(img_io, format="JPEG")
        img_io.seek(0)

        return SimpleUploadedFile(
            "test.jpg",
            img_io.read(),
            content_type="image/jpeg",
        )


class VideoFileFactory(BaseFileFactory):
    class Meta:
        model = file_models.VideoFile


class AudioFileFactory(BaseFileFactory):
    class Meta:
        model = file_models.AudioFile


class DocumentFileFactory(BaseFileFactory):
    class Meta:
        model = file_models.DocumentFile
