import logging

from django.shortcuts import render
from django.views.decorators.cache import never_cache

logger = logging.getLogger(__name__)


@never_cache
def create_app(request, app_label, model_name):
    project_name = "scaleos"
    context = {}
    context["app_label"] = app_label
    context["model_name"] = model_name
    context["project"] = "scaleos"
    context["shell_file_name"] = f"app_{app_label}.sh"
    context["destination_directory"] = f"{project_name}/{app_label}"
    return render(
        request=request,
        template_name="utils/app/create.html",
        context=context,
        content_type="text/plain",
    )
