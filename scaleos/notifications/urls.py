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
    path(
        "<str:notification_public_key>/open/",
        view=notification_views.open_notification,
        name="open_notification",
    ),
    path(
        "unsubscribe/<str:notification_public_key>",
        notification_views.unsubscribe,
        name="unsubscribe",
    ),
]
