from django.urls import path

from scaleos.events import views_htmx as vw_htmx

app_name = "events_htmx"

urlpatterns = [
    path(
        "concept/<str:public_key>/",
        vw_htmx.concept,
        name="concept",
    ),
]
