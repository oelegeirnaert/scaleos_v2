import logging

from django.shortcuts import get_object_or_404
from django.template.loader import get_template
from django.views.decorators.cache import never_cache

from scaleos.catering import models as catering_models
from scaleos.shared import views_htmx as shared_htmx

logger = logging.getLogger("scaleos")


@never_cache
def catering(request, catering_public_key):
    shared_htmx.do_htmx_get_checks(request)

    catering = get_object_or_404(
        catering_models.Catering,
        public_key=catering_public_key,
    )
    used_template = catering.detail_template
    logging.info("Template used: %s", used_template)
    return_string = get_template(used_template).render(
        context={
            "catering": catering,
        },
        request=request,
    )
    return shared_htmx.htmx_response(request, return_string)
