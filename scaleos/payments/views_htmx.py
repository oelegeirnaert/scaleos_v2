import logging

from django.shortcuts import get_object_or_404
from django.template.loader import get_template
from django.views.decorators.cache import never_cache

from scaleos.payments import models as payment_models
from scaleos.shared import views_htmx as shared_htmx
from scaleos.shared.views_htmx import htmx_response

logger = logging.getLogger("scaleos")


@never_cache
def paymentrequest(request, paymentrequest_public_key=None):
    shared_htmx.do_htmx_get_checks(request)
    paymentrequest = get_object_or_404(
        payment_models.PaymentRequest,
        public_key=paymentrequest_public_key,
    )
    used_template = paymentrequest.detail_template
    logging.info("Template used: %s", used_template)
    return_string = get_template(used_template).render(
        context={
            "detail": paymentrequest,
        },
        request=request,
    )
    return htmx_response(request, return_string)
