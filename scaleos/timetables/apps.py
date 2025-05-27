import contextlib

from django.apps import AppConfig


class TimetablesConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "scaleos.timetables"

    def ready(self):
        with contextlib.suppress(ImportError):
            import scaleos.timetables.signals  # noqa: F401
