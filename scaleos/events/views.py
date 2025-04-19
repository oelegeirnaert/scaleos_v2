import logging

from django.shortcuts import get_object_or_404
from django.shortcuts import render
from django.views.decorators.cache import cache_page

from scaleos.events import models as event_models

logger = logging.getLogger(__name__)


@cache_page(60 * 15)
def event(request, event_public_key):
    context = {}
    event = get_object_or_404(
        event_models.Event,
        public_key=event_public_key,
    )
    context["event"] = event
    template_used = event.page_template
    logger.debug("Templated used: %s", template_used)
    return render(
        request,
        template_used,
        context,
    )


def concept(request, concept_public_key):
    context = {}
    if concept_public_key:
        concept = get_object_or_404(
            event_models.Concept,
            public_key=concept_public_key,
        )
        context["concept"] = concept
    return render(request, concept.page_template, context)
