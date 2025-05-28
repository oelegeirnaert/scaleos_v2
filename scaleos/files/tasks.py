# tasks.py

import logging

# your_app/tasks.py
import mimetypes
import os
import tempfile
from pathlib import Path
from urllib.parse import urlparse

import cairosvg
import requests
from django.conf import settings
from django.core.files import File

from config import celery_app  # Adjust to your project name
from scaleos.files.exceptions import empty_file
from scaleos.files.exceptions import no_content_type
from scaleos.files.exceptions import unsupported_content_type
from scaleos.files.exceptions import unsupported_file
from scaleos.files.functions import resolve_file_subclass
from scaleos.files.models import AudioFile
from scaleos.files.models import ImageFile
from scaleos.files.validators import validate_file_extension
from scaleos.files.validators import validate_file_size

logger = logging.getLogger(__name__)


@celery_app.task(bind=True, soft_time_limit=60 * 60, max_retries=3)
def convert_svg_to_png(self, image_id):
    """
    Converts an SVG file to PNG and saves it to the `image` field of ImageFile.
    """
    logger.setLevel(logging.DEBUG)
    logger.debug("Converting SVG to PNG")
    try:
        image = ImageFile.objects.get(id=image_id)

        if image.is_vector and image.file.name.endswith(".svg"):
            svg_path = image.file.path
            png_path = svg_path.replace(".svg", ".png")

            # Convert SVG to PNG
            with Path(svg_path).open("rb") as svg_file:
                cairosvg.svg2png(file_obj=svg_file, write_to=png_path)

            # Save the PNG to the `image` field without overwriting the original SVG
            with Path(png_path).open("rb") as png_file:
                django_file = File(png_file)
                image.image.save(Path(png_path).name, django_file, save=True)

            return f"Successfully generated PNG preview for: {image.name}"

    except Exception as e:  # noqa: BLE001
        try:
            self.retry(exc=e)
        except self.MaxRetriesExceededError:
            return f"SVG to PNG conversion failed permanently: {e!s}"
    else:
        return "File is not a vector SVG."


def handle_image_file(filename, django_file, temp_file_path, org, related_ids=None):
    related_ids = related_ids or {}
    dish_id = related_ids.get("dish_id")
    product_id = related_ids.get("product_id")
    image_instance = ImageFile.objects.create(
        name=filename,
        organization=org,
    )

    image_instance.file.save(filename, django_file)

    with Path(temp_file_path).open("rb") as f:
        image_instance.image.save(filename, File(f))

    image_instance.save()

    if dish_id:
        from scaleos.catering.models import DishImage

        if not DishImage.objects.filter(dish_id=dish_id).exists():
            DishImage.objects.create(dish_id=dish_id, image_id=image_instance.id)

    if product_id:
        from scaleos.catering.models import ProductImage

        if not ProductImage.objects.filter(product_id=product_id).exists():
            ProductImage.objects.create(
                product_id=product_id,
                image_id=image_instance.id,
            )

    return {"type": "image", "id": image_instance.id}


def handle_audio_file(filename, django_file, org):
    audio_instance = AudioFile.objects.create(
        name=filename,
        organization=org,
    )
    audio_instance.file.save(filename, django_file)
    audio_instance.save()

    return {"type": "audio", "id": audio_instance.id}


@celery_app.task(bind=True, soft_time_limit=60, max_retries=3)
def download_file_from_url(self, file_url, *, organization_id=None, related_ids=None):
    related_ids = related_ids or {}
    dish_id = related_ids.get("dish_id")
    product_id = related_ids.get("product_id")

    temp_file_path = None

    try:
        response = requests.get(file_url, stream=True, timeout=30)
        response.raise_for_status()
        content_type = response.headers.get("Content-Type", "").lower()

        if not content_type:
            no_content_type()

        # Guess file extension
        extension = mimetypes.guess_extension(content_type.split(";")[0]) or ""
        filename = Path(urlparse(file_url).path).name or f"downloaded{extension}"

        # Save content to a temporary file
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            for chunk in response.iter_content(1024 * 1024):
                temp_file.write(chunk)
            temp_file.flush()
            temp_file_path = temp_file.name  # Save the path for later use

        # Reopen the temp file and wrap it in Django File
        temp_file_path = Path(temp_file_path)
        with temp_file_path.open("rb") as reopened_file:
            django_file = File(reopened_file, name=filename)

            # Fetch organization if given
            org = None
            if organization_id:
                from scaleos.organizations.models import Organization

                org = Organization.objects.filter(id=organization_id).first()

            # Handle based on content type
            if "image" in content_type:
                return handle_image_file(
                    filename,
                    django_file,
                    temp_file_path,
                    org,
                    related_ids={"dish_id": dish_id, "product_id": product_id},
                )

            if "audio" in content_type:
                return handle_audio_file(filename, django_file, org)

            unsupported_content_type(content_type=content_type)

    except Exception as e:
        raise self.retry(exc=e, countdown=10) from e

    finally:
        if temp_file_path:
            try:
                Path(temp_file_path).unlink()
            except (FileNotFoundError, PermissionError) as e:
                logger.debug("Failed to delete temp file %s: %s", temp_file_path, e)


def upload_files(organization, organization_file_dir):
    logger.setLevel(logging.DEBUG)
    logger.info("Uploading images for organization %s", organization)

    file_folder = os.path.join(  # noqa: PTH118
        settings.BASE_DIR,
        "data",
        organization_file_dir,
        "files",
    )  # Full path to the image folder

    if not os.path.exists(file_folder):  # noqa: PTH110
        logger.warning("Directory not found: %s", file_folder)
        return

    files = list(os.listdir(file_folder))
    if len(files) == 0:
        logger.warning("No files found in the folder: %s", file_folder)
        return

    uploaded = []
    errors = []

    for a_file_name in files:
        logger.debug("Uploading file: %s", a_file_name)
        a_file_path = Path(file_folder, a_file_name)
        logger.debug("From path: %s", a_file_path)

        try:
            with a_file_path.open("rb") as f:
                django_file = File(f, name=a_file_name)
                if django_file is None:
                    empty_file()

                validate_file_size(django_file)
                validate_file_extension(django_file)
                subclassmodel = resolve_file_subclass(django_file)

                if subclassmodel is None:
                    unsupported_file()

                instance, instance_created = subclassmodel.objects.get_or_create(
                    name=a_file_name,
                    organization_id=organization.pk,
                )
                instance.file = django_file
                logger.debug("Saving instance: %s", instance)
                instance.save()

                uploaded.append(
                    {
                        "id": instance.id,
                        "name": instance.name,
                        "type": subclassmodel.__name__,
                    },
                )

        except Exception as e:  # noqa: BLE001
            errors.append(
                {
                    "name": a_file_path.name,
                    "error": str(e),
                },
            )

    if errors:
        for error in errors:
            logger.warning("Error uploading file: %s", error)
