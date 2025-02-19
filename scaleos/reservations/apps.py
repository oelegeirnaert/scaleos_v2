from django.apps import AppConfig


class ReservationsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "scaleos.reservations"

    def ready(self):
        pass  # Import signals to make sure they are registered
