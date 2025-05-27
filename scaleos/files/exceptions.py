from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


def unsupported_file() -> ValueError:
    msg = _("unsupported file type")
    raise ValueError(msg)


def empty_file() -> ValueError:
    msg = _("django file is none")
    raise ValueError(msg)


def unsupported_file_type(ext) -> ValidationError:
    msg = _("Unsupported file type: %s", ext)
    raise ValidationError(msg)


def no_content_type() -> ValueError:
    msg = _("No content type returned by URL.")
    raise ValueError(msg)


def unsupported_content_type(content_type) -> ValueError:
    msg = _("Unsupported content type: %s", content_type)
    raise ValueError(msg)


def unsupported_content_type_returned_by_url():
    msg = _("Unsupported content type returned by URL.")
    raise ValueError(msg)
