import logging

from django.shortcuts import get_object_or_404
from django.shortcuts import render
from django.views.decorators.cache import cache_page

from scaleos.organizations import models as organization_models

logger = logging.getLogger(__name__)


@cache_page(60 * 15)  # in seconds: 15 min cached
def concepts(request, organization_slug):
    organization = get_object_or_404(
        organization_models.Organization,
        slug=organization_slug,
    )
    return render(
        request,
        organization.page_template,
        {
            "organization": organization,
        },
    )
