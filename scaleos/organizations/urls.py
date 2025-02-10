from django.urls import path

from scaleos.organizations import views as organization_views

app_name = "organizations"
urlpatterns = [
    path(
        "<str:organization_slug>/concept/",
        view=organization_views.concepts,
        name="concepts",
    ),
]
