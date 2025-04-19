from django.apps import AppConfig


class CoreConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "scaleos.core"

    def ready(self):
        # Import signals to register them
        import scaleos.core.signals  # noqa: F401
