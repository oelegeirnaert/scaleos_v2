import logging

from django.shortcuts import get_object_or_404
from django.shortcuts import render
from django.views.decorators.cache import never_cache

from scaleos.organizations import models as organization_models

logger = logging.getLogger(__name__)


@never_cache
def concepts(request, organization_slug):
    context = {}
    organization = get_object_or_404(
        organization_models.Organization,
        slug=organization_slug,
    )
    context["organization"] = organization
    return render(
        request,
        organization.page_template,
        context,
    )


def organization(request, organization_slug):
    context = {}
    organization = get_object_or_404(
        organization_models.Organization,
        slug=organization_slug,
    )
    context["organization"] = organization
    return render(
        request,
        organization.page_template,
        context,
    )
