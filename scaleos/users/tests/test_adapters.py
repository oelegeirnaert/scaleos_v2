import re

import pytest
from allauth.account.models import EmailAddress
from allauth.account.models import EmailConfirmation
from django.core import mail
from django.urls import reverse

from scaleos.notifications.models import UserNotification
from scaleos.notifications.models import WebPushNotification
from scaleos.users.adapters import AccountAdapter  # adjust path if needed
from scaleos.users.tests import model_factories as user_factories


@pytest.mark.django_db
def test_send_email_confirmation_creates_notifications(rf, clear_redis_cache):
    assert len(mail.outbox) == 0
    user = user_factories.UserFactory.create(email="john@example.com")
    email_address = EmailAddress.objects.create(
        user=user,
        email=user.email,
        verified=False,
        primary=True,
    )
    email_confirmation = EmailConfirmation.create(email_address)
    email_confirmation.save()

    request = rf.get("/some-url/")  # simulate a request
    adapter = AccountAdapter()
    adapter.send_email_confirmation(request, email_confirmation, signup=True)

    user_notification = UserNotification.objects.get(to_user=user)
    push_notification = WebPushNotification.objects.filter(
        notification=user_notification,
    ).exists()

    assert push_notification is False, (
        "when we need to confirm an email adress, we may not do it via a push"
    )

    user_notification.mail_notification.refresh_from_db()

    assert user_notification.mail_notification.to_email_addresses == user.email

    assert (
        len(user_notification.mail_notification.to_email_addresses.split(",")) == 1
    ), (
        "only one email address should be in the list, \
              otherwise another email can confirm the link"
    )
    assert hasattr(user_notification, "webpush_notification") is False, (
        "it may not be send via webpush, \
            otherwise we cannot check if it is a valid email"
    )
    assert len(mail.outbox) == 1


@pytest.mark.django_db
def test_full_password_reset_flow(client, clear_redis_cache):
    email = "testuser@example.com"
    old_password = "oldpassword123"  # noqa: S105
    new_password = "newsecurepassword456"  # noqa: S105

    user_factories.UserFactory.create(email=email, password=old_password)

    # Step 1: Request password reset
    reset_url = reverse("account_reset_password")
    response = client.post(reset_url, {"email": email})
    assert response.status_code == 302
    assert response.url == reverse("account_reset_password_done")
    assert len(mail.outbox) == 1

    # Step 2: Extract reset link from email
    email_body = mail.outbox[0].body
    match = re.search(r"https?://[^/]+(/[^ \n]+)", email_body)
    assert match, "No password reset link found in email"
    reset_link_path = match.group(1)

    # Step 3: Access password reset confirmation form
    response = client.get(reset_link_path)
    assert response.status_code == 302
    assert UserNotification.objects.filter(
        button_link__icontains=reset_link_path,
    ).exists()

    # Step 4: Post new password
    response = client.post(
        reset_link_path,
        {
            "password1": new_password,
            "password2": new_password,
        },
    )
    assert response.status_code == 302

    # Step 5: Log in with the new password to confirm it worked
    login_url = reverse("account_login")
    response = client.post(
        login_url,
        {
            "login": email,
            "password": new_password,
        },
    )
    assert response.status_code == 200  # login should be ok
