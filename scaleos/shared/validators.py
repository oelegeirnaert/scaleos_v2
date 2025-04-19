from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


def validate_percentage(value):
    hundred = 100
    if value < 0 or value > hundred:
        msg = _("percentage value must be between 0 and 100")
        raise ValidationError(msg)
