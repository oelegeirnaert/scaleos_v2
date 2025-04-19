#!/usr/bin/env python
import logging

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import SetPasswordForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.db.models import QuerySet
from django.shortcuts import redirect
from django.shortcuts import render
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.views.generic import DetailView
from django.views.generic import RedirectView
from django.views.generic import UpdateView

from scaleos.users.models import User

logger = logging.getLogger(__name__)


class UserDetailView(LoginRequiredMixin, DetailView):
    model = User
    slug_field = "id"
    slug_url_kwarg = "id"


user_detail_view = UserDetailView.as_view()


class UserUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = User
    fields = ["name"]
    success_message = _("Information successfully updated")

    def get_success_url(self) -> str:
        assert self.request.user.is_authenticated  # type guard
        return self.request.user.get_absolute_url()

    def get_object(self, queryset: QuerySet | None = None) -> User:
        assert self.request.user.is_authenticated  # type guard
        return self.request.user


user_update_view = UserUpdateView.as_view()


class UserRedirectView(LoginRequiredMixin, RedirectView):
    permanent = False

    def get_redirect_url(self) -> str:
        return reverse("users:detail", kwargs={"pk": self.request.user.pk})


user_redirect_view = UserRedirectView.as_view()


@login_required
def custom_set_password(request):
    """Allow users to set a new password without requiring the current password."""
    if request.method == "POST":
        form = SetPasswordForm(user=request.user, data=request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Your password has been set successfully!")
            return redirect("/")  # Redirect to homepage or dashboard
    else:
        form = SetPasswordForm(user=request.user)

    return render(request, "account/set_password.html", {"form": form})


@login_required
def reservations(request):
    from scaleos.reservations.models import Reservation

    user = request.user
    reservations = Reservation.objects.filter(user_id=user.pk)
    return render(
        request,
        user.page_template,
        {"user": user, "reservations": reservations},
    )


@login_required
def organizations(request):
    from scaleos.organizations.models import Organization

    user = request.user

    if not hasattr(user, "person"):
        return render(
            request,
            user.page_template,
            {"user": user, "organizations": None},
        )

    person = user.person
    organization_ids = person.owning_organizations.all().values_list(
        "organization_id",
        flat=True,
    )
    logger.info(organization_ids)
    organizations = Organization.objects.filter(id__in=organization_ids)

    if organizations.count() == 1:
        organization = organizations.first()
        return redirect("organizations:activate_organization", organization.slug)

    return render(
        request,
        user.page_template,
        {"user": user, "organizations": organizations},
    )
