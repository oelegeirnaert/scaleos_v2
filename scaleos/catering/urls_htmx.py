from django.urls import path

from scaleos.catering import views_htmx as vw_htmx

app_name = "catering_htmx"

urlpatterns = [
    path(
        "",
        vw_htmx.catering,
        name="catering",
    ),
    path(
        "<str:catering_public_key>",
        vw_htmx.catering,
        name="catering",
    ),
]
