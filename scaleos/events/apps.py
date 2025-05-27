import contextlib

from django.apps import AppConfig


class EventsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "scaleos.events"

    def ready(self):
        with contextlib.suppress(ImportError):
            import scaleos.events.signals as s

            s.register_signals_for_all_event_subclasses()
