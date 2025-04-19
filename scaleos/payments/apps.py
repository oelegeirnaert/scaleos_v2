from django.apps import AppConfig


class PaymentsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "scaleos.payments"

    def ready(self):
        # Ensure signals get loaded after the app is ready
        import scaleos.payments.signals  # noqa: F401
