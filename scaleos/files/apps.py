import contextlib

from django.apps import AppConfig


class FilesConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "scaleos.files"

    def ready(self):
        with contextlib.suppress(ImportError):
            import scaleos.files.signals  # noqa: F401
