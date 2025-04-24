import logging

from django.shortcuts import get_object_or_404
from django.template.loader import get_template
from django.views.decorators.cache import never_cache

from scaleos.events import models as event_models
from scaleos.shared import views_htmx as shared_htmx
from scaleos.shared.views_htmx import htmx_response

logger = logging.getLogger("scaleos")


@never_cache
def concept(request, concept_public_key):
    shared_htmx.do_htmx_get_checks(request)

    concept = get_object_or_404(event_models.Concept, public_key=concept_public_key)
    used_template = concept.detail_template
    logging.info("Template used: %s", used_template)
    return_string = get_template(used_template).render(
        context={
            "concept": concept,
        },
        request=request,
    )
    return shared_htmx.htmx_response(request, return_string)


def event_info(request, event_public_key):
    shared_htmx.do_htmx_get_checks(request)
    show_info = False
    try:
        request.GET["show"]
        show_info = True
    except KeyError:
        pass

    try:
        request.GET["hide"]
        show_info = False
    except KeyError:
        pass

    logger.info("Show info: %s", show_info)

    event = get_object_or_404(event_models.Event, public_key=event_public_key)

    template_used = "events/event/info.html"
    logger.debug("Template used: %s", template_used)
    html_fragment = get_template(template_used).render(
        context={
            "event": event,
            "show_info": show_info,
        },
        request=request,
    )

    return htmx_response(request, html_fragment)


def event_updates(request, event_public_key):
    shared_htmx.do_htmx_get_checks(request)
    show_info = False
    try:
        request.GET["show"]
        show_info = True
    except KeyError:
        pass

    try:
        request.GET["hide"]
        show_info = False
    except KeyError:
        pass

    logger.info("Show info: %s", show_info)

    event_updates = event_models.EventUpdate.objects.filter(
        event__public_key=event_public_key,
    ).order_by("-created_on")
    logger.info(event_updates)
    template_used = "events/event/updates.html"
    logger.debug("Template used: %s", template_used)
    html_fragment = get_template(template_used).render(
        context={
            "event_updates": event_updates,
            "show_info": show_info,
        },
        request=request,
    )

    return htmx_response(request, html_fragment)
