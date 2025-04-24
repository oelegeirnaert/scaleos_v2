# Create your views here.
import logging

from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.views.decorators.cache import cache_page

from scaleos.hr import models as hr_models

logger = logging.getLogger(__name__)

# views/language.py


@login_required
@cache_page(60 * 15)
def person(request):
    context = {}

    if request.user and request.user.is_authenticated:
        person, created = hr_models.Person.objects.get_or_create(
            user_id=request.user.pk,
        )

    context["person"] = person
    template_used = person.page_template
    logger.debug("Templated used: %s", template_used)
    return render(
        request,
        template_used,
        context,
    )
