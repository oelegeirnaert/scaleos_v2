# validators.py (in your app)
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


def validate_ean(value):
    if not value.isdigit():
        msg = _("EAN must contain only digits.")
        raise ValidationError(msg)

    max_ean_length = 13
    if len(value) != max_ean_length:
        msg = _("EAN must be exactly 13 digits long.")
        raise ValidationError(msg)
