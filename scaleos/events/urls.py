from django.urls import path

from scaleos.events import views as event_views

app_name = "events"
urlpatterns = [
    path(
        "<str:public_key>/",
        view=event_views.event,
        name="event",
    ),
]
