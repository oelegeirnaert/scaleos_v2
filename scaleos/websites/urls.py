from django.urls import path

from scaleos.websites import views as website_views

app_name = "websites"
urlpatterns = [
    path(
        "",
        view=website_views.website,
        name="website",
    ),
    path(
        "<str:domain_name>/",
        view=website_views.website,
        name="website",
    ),
    path(
        "<str:domain_name>/<str:page_slug>/",
        view=website_views.page,
        name="page",
    ),
]
