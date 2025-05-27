import contextlib

from django.apps import AppConfig


class ReservationsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "scaleos.reservations"

    def ready(self):
        with contextlib.suppress(ImportError):
            import scaleos.reservations.signals  # noqa: F401
