from django.urls import path

from scaleos.events import views_htmx as vw_htmx

app_name = "events_htmx"

urlpatterns = [
    path(
        "concept/<str:concept_public_key>/",
        vw_htmx.concept,
        name="concept",
    ),
    path(
        "event/<uuid:event_public_key>/info",
        vw_htmx.event_info,
        name="event_info",
    ),
    path(
        "event/<uuid:event_public_key>/updates",
        vw_htmx.event_updates,
        name="event_updates",
    ),
]
