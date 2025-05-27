# validators.py

import functools
import operator
from pathlib import Path

from django.core.exceptions import ValidationError

from scaleos.files.exceptions import unsupported_file_type

# File size limit (in bytes)
MAX_FILE_SIZE = 20 * 1024 * 1024  # 20 MB

ALLOWED_EXTENSIONS = {
    "image": [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".tiff", ".webp", ".svg"],
    "audio": [".mp3", ".wav", ".ogg", ".flac"],
    "document": [".pdf", ".doc", ".docx", ".xls", ".xlsx", ".ppt", ".pptx"],
}


def validate_file_size(file):
    if file.size > MAX_FILE_SIZE:
        msg = f"File size should not exceed {MAX_FILE_SIZE / (1024 * 1024)} MB."
        raise ValidationError(msg)


def validate_file_extension(file):
    ext = Path(file.name).suffix.lower()
    valid_exts = functools.reduce(operator.iadd, ALLOWED_EXTENSIONS.values(), [])
    if ext not in valid_exts:
        unsupported_file_type()
