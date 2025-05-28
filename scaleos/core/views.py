# Create your views here.

import logging

from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from django.shortcuts import render
from django.urls import reverse

from scaleos.websites.models import Website

logger = logging.getLogger(__name__)


def home(request):
    active_organization_id = request.session.get("active_organization_id", None)
    if active_organization_id:
        website = get_object_or_404(Website, organization_id=active_organization_id)
        return redirect(reverse("websites:website", args=[website.domain_name]))

    return render(request, "pages/home.html")


@login_required
def activate_debug(request):
    if request.user.is_staff:
        current_status = request.session.get("debug", False)
        if current_status:
            request.session["debug"] = False
        else:
            request.session["debug"] = True
    # Get the previous page from the HTTP_REFERER header
    referer = request.headers.get("referer", "/")
    return redirect(referer)
