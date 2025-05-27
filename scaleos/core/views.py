# Create your views here.

import logging

from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect

logger = logging.getLogger(__name__)


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
