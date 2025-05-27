from django.urls import path

from scaleos.core import views as core_views

app_name = "core"

urlpatterns = [
    path(
        "activate-debug",
        view=core_views.activate_debug,
        name="activate_debug",
    ),
]
