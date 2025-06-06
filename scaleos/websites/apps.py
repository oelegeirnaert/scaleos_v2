import contextlib
from django.apps import AppConfig


class WebsitesConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "scaleos.websites"

    def ready(self):
        with contextlib.suppress(ImportError):

            import scaleos.websites.signals  # noqa
