import logging
from pathlib import Path

from django.conf import settings
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from django.shortcuts import render
from django.views.decorators.cache import never_cache

from scaleos.events.models import CustomerConcept
from scaleos.organizations import models as organization_models
from scaleos.organizations import tasks as organization_tasks
from scaleos.organizations.forms import ResengoExcelUploadForm
from scaleos.shared.views import page_or_list_page

logger = logging.getLogger(__name__)


@never_cache
def concepts(request, organization_slug):
    context = {}
    organization = get_object_or_404(
        organization_models.Organization,
        slug=organization_slug,
    )
    context["organization"] = organization
    context["concepts"] = organization.concepts.exclude(Q(instance_of=CustomerConcept))
    return render(
        request,
        organization.page_template,
        context,
    )


def enterprise(request, enterprise_slug=None):
    return redirect(
        "organizations:activate_organization",
        organization_slug=enterprise_slug,
    )


def events(request, organization_slug):
    context = {}
    organization = get_object_or_404(
        organization_models.Organization,
        slug=organization_slug,
    )
    context["organization"] = organization
    context["events"] = organization.events_open_for_reservation
    return render(
        request,
        organization.page_template,
        context,
    )


def organization(request, organization_slug=None):
    context = {}

    if organization_slug is None:
        organizations = organization_models.Organization.objects.filter(
            published_on__isnull=False,
        )
        return page_or_list_page(
            request,
            organization_models.Organization,
            alternative_resultset=organizations,
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


def activate_organization(request, organization_slug):
    organization = get_object_or_404(
        organization_models.Organization,
        slug=organization_slug,
    )
    if organization.internal_url is None:
        organization.internal_url = request.build_absolute_uri()
        organization.save(update_fields=["internal_url"])

    request.session["active_organization_id"] = organization.id
    return redirect("organizations:organization", organization_slug=organization_slug)


def deactivate_organization(request):
    if "active_organization_id" in request.session:
        del request.session["active_organization_id"]
    return redirect("home")


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
                file_path = Path(settings.MEDIA_ROOT, file_name)
                with Path.open(file_path, "wb+") as destination:
                    for chunk in excel_file.chunks():
                        destination.write(chunk)

            # Launch the Celery task
            organization_tasks.import_resengo_excel.delay(
                str(file_path),
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
