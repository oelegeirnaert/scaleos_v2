from django.shortcuts import render, redirect
from django.shortcuts import get_object_or_404
import logging
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
    context["destination_directory"] = f""
    return render(request=request, template_name="utils/app/create.html", context=context, content_type="text/plain")