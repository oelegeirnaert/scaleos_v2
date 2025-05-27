import calendar
import logging

from django.contrib.contenttypes.models import ContentType
from django.db.models import Q
from django.shortcuts import HttpResponse
from django.shortcuts import get_object_or_404
from django.template.loader import get_template
from django.utils.translation import gettext as _
from django.views.decorators.cache import cache_page
from django.views.decorators.cache import never_cache
from django.views.decorators.vary import vary_on_headers

from scaleos.events import models as event_models
from scaleos.organizations import models as organization_models
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


@vary_on_headers("Accept-Language")
@cache_page(60 * 15)
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


@vary_on_headers("Accept-Language")
@cache_page(60 * 15)
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


def concept_filter(request):
    shared_htmx.do_htmx_post_checks(request)
    logger.setLevel(logging.DEBUG)
    logger.debug(list(request.POST.items()))
    template_used = "card_list.html"
    logger.debug("Template used: %s", template_used)

    active_organization_id = request.session.get("active_organization_id", None)
    if active_organization_id:
        active_organization = organization_models.Organization.objects.get(
            id=active_organization_id,
        )
        segment = request.session.get("segment", None)
        if segment == event_models.Concept.SegmentType.B2B:
            logger.debug("LOADING B2B events")
            results = active_organization.b2b_concepts
        elif segment == event_models.Concept.SegmentType.B2C:
            logger.debug("LOADING B2C events")
            results = active_organization.b2c_concepts
        else:
            logger.debug("LOADING ALL events")
            results = active_organization.all_concepts

    html_fragment = get_template(template_used).render(
        context={
            "cards": results,
        },
        request=request,
    )

    return htmx_response(request, html_fragment)


def event_filter(request):
    shared_htmx.do_htmx_post_checks(request)
    logger.setLevel(logging.DEBUG)
    logger.debug(list(request.POST.items()))
    active_organization = request.session.get("active_organization_id", None)
    if active_organization:
        active_organization = organization_models.Organization.objects.get(
            id=active_organization,
        )
        segment = request.POST.get("segment", None)
        if segment == event_models.Concept.SegmentType.B2B:
            logger.debug("LOADING B2B events")
            results = active_organization.upcoming_public_b2b_events
        elif segment == event_models.Concept.SegmentType.B2C:
            logger.debug("LOADING B2C events")
            results = active_organization.upcoming_public_b2c_events
        else:
            logger.debug("LOADING ALL events")
            results = active_organization.upcoming_public_events
    else:
        results = event_models.Event.objects.all()

    template_used = "card_list.html"
    logger.debug("Template used: %s", template_used)
    html_fragment = get_template(template_used).render(
        context={
            "cards": results,
        },
        request=request,
    )

    return htmx_response(request, html_fragment)


def organizer_options(request):
    logger.setLevel(logging.DEBUG)
    logger.debug("Getting organizers")
    shared_htmx.do_htmx_get_checks(request)
    customer_concept_organization_filter = Q()
    event_organization_filter = Q()
    organization_id = request.session.get("active_organization_id", None)
    if organization_id:
        logger.debug("we have an organization, so apply additional filter")
        customer_concept_organization_filter = Q(organizer_id=organization_id)
        event_organization_filter = Q(concept__organizer_id=organization_id)
    customer_concept_ids = event_models.CustomerConcept.objects.filter(
        customer_concept_organization_filter,
    ).values_list("id", flat=True)
    event_organizers = (
        event_models.Event.objects.filter(
            event_organization_filter & Q(concept__isnull=False),
        )
        .exclude(concept_id__in=customer_concept_ids)
        .values_list("concept__organizer_id", flat=True)
        .distinct()
    )
    result = organization_models.Organization.objects.filter(id__in=event_organizers)
    logger.debug("Results found: %s", result.count())

    result = [(organizer.public_key, organizer.name) for organizer in result]
    html_fragment = get_template("events/event/listbox_option.html").render(
        context={
            "search_field": "organizers",
            "select_options": result,
        },
        request=request,
    )
    return HttpResponse(html_fragment)


def type_options(request):
    logger.setLevel(logging.DEBUG)
    logger.debug("Getting concept types")
    shared_htmx.do_htmx_get_checks(request)
    organization_id = request.session.get("active_organization_id", None)
    if organization_id is None:
        events = (
            event_models.Event.objects.all()
            .values_list("polymorphic_ctype_id", flat=True)
            .distinct()
        )
        result = ContentType.objects.filter(id__in=events)
        result = [(ct.id, ct.name) for ct in result]
        html_fragment = get_template("events/event/listbox_option.html").render(
            context={
                "search_field": "types",
                "select_options": result,
            },
            request=request,
        )
        return HttpResponse(html_fragment)
    if organization_id:
        logger.debug("we have an organization, so apply additional filter")
        customer_concept_organization_filter = Q(organizer_id=organization_id)
        event_organization_filter = Q(concept__organizer_id=organization_id)
    customer_concept_ids = event_models.CustomerConcept.objects.filter(
        customer_concept_organization_filter,
    ).values_list("id", flat=True)
    events = (
        event_models.Event.objects.filter(
            event_organization_filter & Q(concept__isnull=False),
        )
        .exclude(concept_id__in=customer_concept_ids)
        .values_list("polymorphic_ctype_id", flat=True)
        .distinct()
    )
    result = ContentType.objects.filter(id__in=events)

    if result is None or result.count() == 0:
        return HttpResponse("")

    logger.debug("Results found: %s", result.count())

    result = [(ct.id, ct.name) for ct in result]
    html_fragment = get_template("events/event/listbox_option.html").render(
        context={
            "search_field": "types",
            "select_options": result,
        },
        request=request,
    )
    return HttpResponse(html_fragment)


def segment_options(request):
    logger.setLevel(logging.DEBUG)
    logger.debug("Getting segments")
    shared_htmx.do_htmx_get_checks(request)
    result = event_models.Concept.SegmentType.choices
    html_fragment = get_template("events/event/listbox_option.html").render(
        context={
            "search_field": "segments",
            "select_options": result,
        },
        request=request,
    )
    return HttpResponse(html_fragment)


def year_options(request):
    logger.setLevel(logging.DEBUG)
    logger.debug("Getting years")
    shared_htmx.do_htmx_get_checks(request)
    organization_id = request.session.get("active_organization_id", None)
    result = None
    if organization_id:
        organization = organization_models.Organization.objects.get(id=organization_id)
        result = organization.upcoming_public_events.values_list(
            "starting_at__year",
            flat=True,
        ).distinct()
    if result is None:
        return HttpResponse("")

    result = [(year, year) for year in result]

    html_fragment = get_template("events/event/listbox_option.html").render(
        context={
            "search_field": "years",
            "select_options": result,
        },
        request=request,
    )
    return HttpResponse(html_fragment)


def month_options(request):
    logger.setLevel(logging.DEBUG)
    logger.debug("Getting months")
    organization_id = request.session.get("active_organization_id", None)
    result = None
    if organization_id:
        organization = organization_models.Organization.objects.get(id=organization_id)
        result = organization.upcoming_public_events.values_list(
            "starting_at__month",
            flat=True,
        ).distinct()
    if result is None:
        return HttpResponse("")

    result = [(month, _(calendar.month_name[month])) for month in result]
    html_fragment = get_template("events/event/listbox_option.html").render(
        context={
            "search_field": "months",
            "select_options": result,
        },
        request=request,
    )
    return HttpResponse(html_fragment)


def day_options(request):
    logger.setLevel(logging.DEBUG)
    logger.debug("Getting days")
    shared_htmx.do_htmx_get_checks(request)
    organization_id = request.session.get("active_organization_id", None)
    result = None
    if organization_id:
        organization = organization_models.Organization.objects.get(id=organization_id)
        result = organization.upcoming_public_events.values_list(
            "starting_at__day",
            flat=True,
        ).distinct()
    if result is None:
        return HttpResponse("")

    result = [(day, day) for day in result]
    html_fragment = get_template("events/event/listbox_option.html").render(
        context={
            "search_field": "days",
            "select_options": result,
        },
        request=request,
    )
    return HttpResponse(html_fragment)
