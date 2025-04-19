from django.urls import path

from scaleos.notifications import views as notification_views

app_name = "notifications"
urlpatterns = [
    path(
        "settings/",
        view=notification_views.notificationsettings,
        name="notificationsettings",
    ),
    path(
        "",
        view=notification_views.notification,
        name="notification",
    ),
    path(
        "<str:notification_public_key>/",
        view=notification_views.notification,
        name="notification",
    ),
]
