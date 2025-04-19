from django.urls import path

from scaleos.events import views as event_views

app_name = "events"
urlpatterns = [
    path(
        "<str:event_public_key>/",
        view=event_views.event,
        name="event",
    ),
    path(
        "concept/<str:concept_public_key>/",
        view=event_views.concept,
        name="concept",
    ),
]
