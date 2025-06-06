from django.urls import path

from scaleos.websites import views as website_views

app_name = "websites"
urlpatterns = [


    path(
        "<str:page_slug>/",
        view=website_views.page,
        name="page",
    ),
]
