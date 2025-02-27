from django.urls import path

from scaleos.hr import views as hr_views

app_name = "hr"
urlpatterns = [
    path(
        "person/",
        view=hr_views.person,
        name="person",
    ),
]
