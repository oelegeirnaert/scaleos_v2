from django.urls import path
from scaleos_v2.utils import views as util_views


app_name = "utils"
urlpatterns = [
    path("app/create/<str:app_label>/<str:model_name>/", view=util_views.create_app, name="create_app"),
]