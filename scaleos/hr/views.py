# Create your views here.
import logging

from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.views.decorators.cache import cache_page

from scaleos.hr import models as hr_models

logger = logging.getLogger(__name__)


@login_required
@cache_page(60 * 15)
def person(request):
    context = {}

    if hasattr(request.user, "person"):
        logger.info("Getting a person profile")
        person = request.user.person
    else:
        logger.debug("Creating a person profile")
        person = hr_models.Person.objects.create(user_id=request.user.pk)

    context["person"] = person
    template_used = person.page_template
    logger.debug("Templated used: %s", template_used)
    return render(
        request,
        template_used,
        context,
    )
