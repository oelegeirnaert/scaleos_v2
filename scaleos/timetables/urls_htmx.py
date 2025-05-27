from django.urls import path

from scaleos.timetables import views_htmx as vw_htmx

app_name = "timetables_htmx"

urlpatterns = [
    path(
        "",
        vw_htmx.timetable,
        name="timetable",
    ),
    path(
        "<str:timetable_public_key>",
        vw_htmx.timetable,
        name="timetable",
    ),
]
