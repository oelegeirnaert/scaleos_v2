from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.shortcuts import render
from django.views.decorators.cache import never_cache
from templated_email import get_templated_mail

from scaleos.notifications import models as notification_models
from scaleos.shared.mixins import ITS_NOW


# Create your views here.
@never_cache
def notification(request, notification_public_key=None):
    context = {}
    if notification_public_key is None and request.user.is_authenticated:
        notifications = notification_models.Notification.objects.filter(
            user_id=request.user.id,
        )
        context["details"] = notifications
        return render(request, "detail_list.html", context)

    notification = get_object_or_404(
        notification_models.Notification,
        public_key=notification_public_key,
    )

    request.session["active_organization_id"] = notification.sending_organization.pk

    if notification.seen_on is None:
        notification.seen_on = ITS_NOW
        notification.save(update_fields=["seen_on"])

    if notification.redirect_url:
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
def notificationsettings(request):
    context = {}
    notification_settings = request.user.notification_settings
    context["notification_settings"] = notification_settings
    return render(request, notification_settings.page_template, context)
