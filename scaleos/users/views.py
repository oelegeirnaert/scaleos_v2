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
from django.views.i18n import set_language

from scaleos.users.models import User

logger = logging.getLogger(__name__)


def custom_set_language(request):
    response = set_language(request)

    if request.user.is_authenticated:
        language = request.POST.get("language")
        if language is None:
            return response

        if not hasattr(request.user, "website_language"):
            return response

        request.user.website_language = language
        request.user.save(update_fields=["website_language"])

    return response


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
def account(request):
    context = {}
    context["user"] = request.user
    return render(request, request.user.page_template, context)


@login_required
def reservation(request, reservation_public_key=None):
    from scaleos.reservations.models import Reservation

    user = request.user
    reservations = Reservation.objects.filter(user_id=user.pk)
    return render(
        request,
        user.page_template,
        {"user": user, "reservations": reservations},
    )


@login_required
def notification(request, notification_public_key=None):
    from scaleos.notifications.models import UserNotification

    user = request.user
    notifications = UserNotification.objects.filter(to_user_id=user.pk)
    return render(
        request,
        user.page_template,
        {"user": user, "notifications": notifications},
    )


@login_required
def organization(request, organization_public_key=None):
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
