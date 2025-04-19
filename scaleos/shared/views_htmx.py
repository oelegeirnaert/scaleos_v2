import logging

from django.http import HttpResponse
from django.template.loader import get_template
from django.utils.translation import gettext_lazy as _

logger = logging.getLogger("scaleos")


def do_htmx_get_checks(request):
    if not request.htmx:
        msg = _("this is not a HTMX request")
        logger.error(msg)
        raise NotImplementedError(msg)


def do_htmx_post_checks(request):
    if not request.htmx:
        msg = _("this is not a HTMX request")
        logger.error(msg)
        raise NotImplementedError(msg)

    if request.method != "POST":
        msg = _("this is not a POST request")
        logger.error(msg)
        raise NotImplementedError(msg)


def htmx_response(request, html_fragment):
    try:
        request.GET["popup"]
        logger.info("YAY popup")
    except KeyError:
        return HttpResponse(html_fragment)

    html_fragment = get_template("popup.html").render(
        context={
            "popup_body": html_fragment,
        },
        request=request,
    )
    return HttpResponse(html_fragment)
