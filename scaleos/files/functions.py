# functions.py

import hashlib
from pathlib import Path

from .models import AudioFile
from .models import DocumentFile
from .models import ImageFile


def resolve_file_subclass(file):
    ext = Path(file.name).suffix.lower()

    if ext in [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".tiff", ".webp", ".svg"]:
        return ImageFile
    if ext in [".mp3", ".wav", ".ogg", ".flac"]:
        return AudioFile
    if ext in [".pdf", ".doc", ".docx", ".xls", ".xlsx", ".ppt", ".pptx"]:
        return DocumentFile
    return None  # unknown or unsupported


def get_checksum_from_filefield(file_field, algorithm="sha256"):
    file_field.open()
    hash_func = getattr(hashlib, algorithm)()
    for chunk in file_field.chunks():
        hash_func.update(chunk)
    file_field.close()
    return hash_func.hexdigest()
