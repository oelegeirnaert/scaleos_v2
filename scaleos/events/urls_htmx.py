from django.urls import path

from scaleos.events import views_htmx as vw_htmx

app_name = "events_htmx"

urlpatterns = [
    path(
        "concept/filter/",
        vw_htmx.concept_filter,
        name="concept_filter",
    ),
    path(
        "concept/<str:concept_public_key>/",
        vw_htmx.concept,
        name="concept",
    ),
    path(
        "<uuid:event_public_key>/info/",
        vw_htmx.event_info,
        name="event_info",
    ),
    path(
        "<uuid:event_public_key>/updates/",
        vw_htmx.event_updates,
        name="event_updates",
    ),
    path(
        "filter/",
        vw_htmx.event_filter,
        name="event_filter",
    ),
    path(
        "filter/organizers/",
        vw_htmx.organizer_options,
        name="organizer_options",
    ),
    path(
        "filter/segments/",
        vw_htmx.segment_options,
        name="segment_options",
    ),
    path(
        "filter/types/",
        vw_htmx.type_options,
        name="type_options",
    ),
    path(
        "filter/years/",
        vw_htmx.year_options,
        name="year_options",
    ),
    path(
        "filter/months/",
        vw_htmx.month_options,
        name="month_options",
    ),
    path(
        "filter/days/",
        vw_htmx.day_options,
        name="day_options",
    ),
]
