import contextlib
import logging

from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from django.template.loader import get_template
from django.urls import reverse
from django.views.decorators.cache import never_cache

from scaleos.shared import views_htmx as shared_htmx
from scaleos.websites import models as website_models

logger = logging.getLogger("scaleos")


@never_cache
def ask_segment(request):
    shared_htmx.do_htmx_get_checks(request)

    website = request.website
    used_template = "websites/website/ask_segment.html"
    logging.info("Template used: %s", used_template)
    return_string = get_template(used_template).render(
        context={
            "website": website,
        },
        request=request,
    )
    return shared_htmx.htmx_response(request, return_string)


def set_segment(request, segment):
    match segment:
        case "business":
            request.session["segment"] = website_models.Page.SegmentType.B2B
        case "personal":
            request.session["segment"] = website_models.Page.SegmentType.B2C
        case "both":
            request.session["segment"] = website_models.Page.SegmentType.BOTH

    return redirect("/")


def clear_segment(request):
    try:
        del request.session["segment"]
    except KeyError:
        contextlib.suppress(KeyError)

    return redirect("/")
