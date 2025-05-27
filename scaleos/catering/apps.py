import contextlib

from django.apps import AppConfig


class CateringConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "scaleos.catering"

    def ready(self):
        with contextlib.suppress(ImportError):
            import scaleos.catering.signals  # noqa: F401
