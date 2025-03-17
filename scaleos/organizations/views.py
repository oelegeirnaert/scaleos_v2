import logging
from pathlib import Path

from django.conf import settings
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import get_object_or_404
from django.shortcuts import render
from django.views.decorators.cache import never_cache

from scaleos.organizations import models as organization_models
from scaleos.organizations import tasks as organization_tasks
from scaleos.organizations.forms import ResengoExcelUploadForm

logger = logging.getLogger(__name__)


@never_cache
def concepts(request, organization_slug):
    context = {}
    organization = get_object_or_404(
        organization_models.Organization,
        slug=organization_slug,
    )
    context["organization"] = organization
    context["concepts"] = organization.concepts.all()
    return render(
        request,
        organization.page_template,
        context,
    )


def enterprise(request, enterprise_slug=None):
    context = {}
    enterprise = get_object_or_404(organization_models.Enterprise, slug=enterprise_slug)
    context["enterprise"] = enterprise
    return render(
        request,
        enterprise.page_template,
        context,
    )


def organization(request, organization_slug=None):
    context = {}

    if organization_slug is None:
        organizations = organization_models.Organization.objects.filter(
            published_on__isnull=False,
        )
        context["organizations"] = organizations
        return render(
            request,
            organization_models.Organization.list_template(),
            context,
        )

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


@login_required
@never_cache
def customers(request, organization_slug):
    context = {}
    organization = get_object_or_404(
        organization_models.Organization,
        slug=organization_slug,
    )
    context["organization"] = organization
    context["customers"] = organization.customers.all()
    return render(
        request,
        organization.page_template,
        context,
    )


@staff_member_required
def import_resengo_excel(request, organization_slug):
    if request.method == "POST":
        organization = get_object_or_404(
            organization_models.Organization,
            slug=organization_slug,
        )
        form = ResengoExcelUploadForm(request.POST, request.FILES)
        if form.is_valid():
            excel_file = request.FILES["excel_file"]
            overwrite_existing_data = form.cleaned_data[
                "overwrite_existing_data"
            ]  # Get the value of the checkbox

            # Save the file temporarily
            with transaction.atomic():
                file_name = excel_file.name
                file_path = Path(settings.MEDIA_ROOT / file_name)
                with Path.open(file_path, "wb+") as destination:
                    for chunk in excel_file.chunks():
                        destination.write(chunk)

            # Launch the Celery task
            organization_tasks.import_resengo_excel.delay(
                file_path,
                organization.id,
                request.user.id,
                overwrite_existing_data,
            )  # Use .delay() to run the task in the background

            messages.success(
                request,
                "Your Excel file is being imported. \
                    You will be notified when it's complete.",
            )
        else:
            messages.error(request, "Error uploading file")
    else:
        form = ResengoExcelUploadForm()

    return render(request, "core/import_excel.html", {"form": form})
