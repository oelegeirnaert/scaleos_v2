# signals.py

import logging
from pathlib import Path

from django.core.files.base import ContentFile
from django.db.models.signals import post_save
from django.dispatch import receiver
from PIL import Image
from PIL import UnidentifiedImageError

from scaleos.files import models as file_models
from scaleos.files.tasks import convert_svg_to_png

logger = logging.getLogger(__name__)


@receiver(post_save, sender=file_models.ImageFile)
def process_image_file(sender, instance, **kwargs):  # noqa: C901, PLR0912, PLR0915
    logger.setLevel(logging.DEBUG)
    logger.debug("Processing image file %s", instance.pk)

    if not instance.file:
        logger.debug("File from instance is none. Skipping")
        return

    changed_fields = {}

    if instance.file and not instance.checksum:
        checksum = instance.get_checksum()
        changed_fields["checksum"] = checksum

    ext = Path(instance.file.name).suffix.lower()
    is_vector = ext == ".svg"
    width, height = None, None

    if not is_vector:
        try:
            instance.file.open()
            img = Image.open(instance.file)
            img.load()
            width, height = img.size
            logger.debug("Image dimensions: %sx%s", width, height)

            if not instance.image:
                logger.debug("Moving raster image to `image` field and clear `file`.")
                instance.file.seek(0)
                image_content = ContentFile(instance.file.read())
                image_name = Path(instance.file.name).name

                instance.image.save(image_name, image_content, save=False)
                instance.file.delete(save=False)  # Remove file from disk/storage
                instance.file = None  # Clear field
                changed_fields["image"] = instance.image
                changed_fields["file"] = None
        except UnidentifiedImageError:
            logger.warning("File %s is not a valid image.", instance.file.name)
            return
        except Exception:
            logger.exception("Failed to process raster image")
            return
        finally:
            instance.file.close()

    if instance.is_vector != is_vector:
        changed_fields["is_vector"] = is_vector
    if instance.width != width:
        changed_fields["width"] = width
    if instance.height != height:
        changed_fields["height"] = height

    if changed_fields:
        for field, value in changed_fields.items():
            setattr(instance, field, value)

        from django.db.models.signals import post_save as signal_post_save

        signal_post_save.disconnect(process_image_file, sender=file_models.ImageFile)
        instance.save(update_fields=list(changed_fields.keys()))
        signal_post_save.connect(process_image_file, sender=file_models.ImageFile)

    if is_vector and not instance.image:
        logger.debug("Image is SVG and `image` is empty. Triggering PNG conversion.")
        convert_svg_to_png.delay(instance.id)


@receiver(post_save, sender=file_models.AudioFile)
def process_audio_file(sender, instance, **kwargs):
    try:
        from mutagen import File as MutagenFile

        audio = MutagenFile(instance.file)
        duration = None
        artist = ""
        album = ""

        if audio and hasattr(audio, "info") and hasattr(audio.info, "length"):
            duration = audio.info.length
        if hasattr(audio, "tags") and audio.tags:
            artist = audio.tags.get("TPE1", "")[0]
            album = audio.tags.get("TALB", "")[0]

        changes = {}
        if instance.duration != duration:
            changes["duration"] = duration
        if instance.artist != artist:
            changes["artist"] = artist
        if instance.album != album:
            changes["album"] = album

        if changes:
            file_models.AudioFile.objects.filter(pk=instance.pk).update(**changes)

    except Exception:
        logger.exception("Failed to process audio file")


@receiver(post_save, sender=file_models.DocumentFile)
def process_document_file(sender, instance, **kwargs):
    ext = instance.file.name.lower().split(".")[-1]
    ext_map = {
        "doc": "word",
        "docx": "word",
        "xls": "excel",
        "xlsx": "excel",
        "pdf": "pdf",
        "ppt": "ppt",
        "pptx": "ppt",
    }
    new_doc_type = ext_map.get(ext, "")

    if new_doc_type != instance.doc_type:
        file_models.DocumentFile.objects.filter(pk=instance.pk).update(
            doc_type=new_doc_type,
        )


def extract_video_duration(video_path: Path) -> float | None:
    try:
        import cv2

        cap = cv2.VideoCapture(str(video_path))
        if cap.isOpened():
            fps = cap.get(cv2.CAP_PROP_FPS)
            frame_count = cap.get(cv2.CAP_PROP_FRAME_COUNT)
            if fps and frame_count:
                return frame_count / fps
    except Exception as e:  # noqa: BLE001
        logger.info("Failed to process video: %s", e)
    finally:
        if "cap" in locals():
            cap.release()
    return None


def detect_video_source(url: str) -> str:
    if "youtube.com" in url or "youtu.be" in url:
        return "youtube"
    if "vimeo.com" in url:
        return "vimeo"
    return "other"


@receiver(post_save, sender=file_models.VideoFile)
def process_video_file(sender, instance, **kwargs):
    source = ""
    duration = None

    if instance.video:
        source = "upload"
        duration = extract_video_duration(Path(instance.video.path))
    elif instance.url:
        source = detect_video_source(instance.url)

    changes = {}
    if instance.source != source:
        changes["source"] = source
    if instance.duration != duration:
        changes["duration"] = duration

    if changes:
        file_models.VideoFile.objects.filter(pk=instance.pk).update(**changes)
