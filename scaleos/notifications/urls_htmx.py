from django.urls import path

from scaleos.notifications import views_htmx as vw_htmx

app_name = "notifications_htmx"

urlpatterns = [
    path(
        "user/<uuid:user_notification_settings_public_key>/",
        vw_htmx.disable,
        name="disable",
    ),
]
