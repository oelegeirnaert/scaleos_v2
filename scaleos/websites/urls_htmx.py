from django.urls import path

from scaleos.websites import views_htmx as vw_htmx

app_name = "websites_htmx"

urlpatterns = [
    path(
        "ask-segment/",
        vw_htmx.ask_segment,
        name="ask_segment",
    ),
    path(
        "ask-segment/<str:segment>/",
        vw_htmx.set_segment,
        name="set_segment",
    ),
    path(
        "clear-segment/",
        vw_htmx.clear_segment,
        name="clear_segment",
    ),
]
