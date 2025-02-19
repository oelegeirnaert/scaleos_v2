import logging

from django.shortcuts import get_object_or_404
from django.template.loader import get_template
from django.views.decorators.cache import never_cache

from scaleos.events import models as event_models
from scaleos.shared import views_htmx as shared_htmx

logger = logging.getLogger("scaleos")


@never_cache
def concept(request, public_key):
    shared_htmx.do_htmx_get_checks(request)

    concept = get_object_or_404(event_models.Concept, public_key=public_key)
    used_template = concept.detail_template
    logging.info("Template used: %s", used_template)
    return_string = get_template(used_template).render(
        context={
            "concept": concept,
        },
        request=request,
    )
    return shared_htmx.htmx_response(request, return_string)
