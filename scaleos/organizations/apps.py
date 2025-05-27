import contextlib

from django.apps import AppConfig


class OrganizationsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "scaleos.organizations"

    def ready(self):
        with contextlib.suppress(ImportError):
            import scaleos.organizations.signals  # noqa: F401
