import logging

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.shortcuts import render
from django.utils.translation import gettext_lazy as _
from django.views.decorators.cache import never_cache

# views/language.py
from templated_email import get_templated_mail

from scaleos.notifications import models as notification_models
from scaleos.shared.mixins import ITS_NOW

logger = logging.getLogger(__name__)


# Create your views here.
@never_cache
def notification(request, notification_public_key=None):
    context = {}
    if notification_public_key is None and request.user.is_authenticated:
        notifications = notification_models.Notification.objects.filter(
            public_key=notification_public_key,
        )
        context["details"] = notifications
        return render(request, "detail_list.html", context)

    notification = get_object_or_404(
        notification_models.Notification,
        public_key=notification_public_key,
    )

    if notification.seen_on is None:
        notification_models.Notification.objects.filter(
            public_key=notification_public_key,
        ).update(seen_on=ITS_NOW)

    request.session["active_organization_id"] = notification.sending_organization.pk

    if notification.redirect_url:
        logger.debug("redirecting to %s", notification.redirect_url)
        return HttpResponseRedirect(notification.redirect_url)

    context["notification"] = notification

    email = get_templated_mail(
        template_name=notification.mail_template,
        from_email="no-reply@example.com",
        to=["john@example.com"],  # required but not used for preview
        context=context,
    )

    email_subject = email.subject
    plain_body = email.body
    html_body = ""
    if email.alternatives:
        html_body = email.alternatives[0][0]  # first alternative is the HTML version

    context["plain_body"] = plain_body
    context["html_body"] = html_body
    context["email_subject"] = email_subject
    return render(request, notification.page_template, context)


@login_required
def open_notification(request, notification_public_key=None):
    context = {}
    notification = get_object_or_404(
        notification_models.Notification,
        public_key=notification_public_key,
    )
    if notification.redirect_url:
        return HttpResponseRedirect(notification.redirect_url)
    if notification.button_link:
        return HttpResponseRedirect(notification.button_link)
    msg = _("we cannot open this notification")
    messages.error(request, msg)
    return render(request, notification.page_template, context)


@login_required
def notificationsettings(request):
    context = {}
    notification_settings = request.user.notification_settings
    context["notification_settings"] = notification_settings
    return render(request, notification_settings.page_template, context)


def unsubscribe(request, notification_public_key=None):
    context = {}
    notification = get_object_or_404(
        notification_models.Notification,
        public_key=notification_public_key,
    )
    context["notification"] = notification
    request.session["active_organization_id"] = notification.sending_organization.pk
    return render(request, "notifications/notification/unsubscribe.html", context)
