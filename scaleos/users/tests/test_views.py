from http import HTTPStatus
from urllib.parse import urlencode
from uuid import uuid4

import pytest
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.models import AnonymousUser
from django.contrib.messages import get_messages
from django.contrib.messages.middleware import MessageMiddleware
from django.contrib.sessions.middleware import SessionMiddleware
from django.http import HttpRequest
from django.http import HttpResponseRedirect
from django.test import RequestFactory
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from scaleos.users.forms import UserAdminChangeForm
from scaleos.users.models import User
from scaleos.users.tests.model_factories import UserFactory
from scaleos.users.views import UserRedirectView
from scaleos.users.views import UserUpdateView
from scaleos.users.views import user_detail_view

pytestmark = pytest.mark.django_db


class TestUserUpdateView:
    """
    TODO:
        extracting view initialization code as class-scoped fixture
        would be great if only pytest-django supported non-function-scoped
        fixture db access -- this is a work-in-progress for now:
        https://github.com/pytest-dev/pytest-django/pull/258
    """

    def dummy_get_response(self, request: HttpRequest):
        return None

    def test_get_success_url(self, user: User, rf: RequestFactory):
        view = UserUpdateView()
        request = rf.get("/fake-url/")
        request.user = user

        view.request = request
        assert view.get_success_url() == f"/user/{user.pk}/"

    def test_get_object(self, user: User, rf: RequestFactory):
        view = UserUpdateView()
        request = rf.get("/fake-url/")
        request.user = user

        view.request = request

        assert view.get_object() == user

    def test_form_valid(self, user: User, rf: RequestFactory):
        view = UserUpdateView()
        request = rf.get("/fake-url/")

        # Add the session/message middleware to the request
        SessionMiddleware(self.dummy_get_response).process_request(request)
        MessageMiddleware(self.dummy_get_response).process_request(request)
        request.user = user

        view.request = request

        # Initialize the form
        form = UserAdminChangeForm()
        form.cleaned_data = {}
        form.instance = user
        view.form_valid(form)

        messages_sent = [m.message for m in messages.get_messages(request)]
        assert messages_sent == [_("Information successfully updated")]


class TestUserRedirectView:
    def test_get_redirect_url(self, user: User, rf: RequestFactory):
        view = UserRedirectView()
        request = rf.get("/fake-url")
        request.user = user

        view.request = request
        assert view.get_redirect_url() == f"/user/{user.pk}/"


class TestUserDetailView:
    def test_authenticated(self, user: User, rf: RequestFactory):
        request = rf.get("/fake-url/")
        request.user = UserFactory()
        response = user_detail_view(request, pk=user.pk)

        assert response.status_code == HTTPStatus.OK

    def test_not_authenticated(self, user: User, rf: RequestFactory):
        request = rf.get("/fake-url/")
        request.user = AnonymousUser()
        response = user_detail_view(request, pk=user.pk)
        login_url = reverse(settings.LOGIN_URL)

        assert isinstance(response, HttpResponseRedirect)
        assert response.status_code == HTTPStatus.FOUND
        assert response.url == f"{login_url}?next=/fake-url/"


@pytest.mark.django_db
def test_user_can_see_his_reservations(admin_client):
    # inspired by: https://djangostars.com/blog/django-pytest-testing/
    from scaleos.reservations.tests.model_factories import ReservationFactory

    public_key = uuid4()
    ReservationFactory(public_key=public_key)

    url = reverse(
        "users:reservations",
    )
    response = admin_client.get(url)
    assert response.status_code == 200


@pytest.mark.django_db
def test_user_custom_set_password(client, django_user_model):
    email = "joske_vermeulen@hotmail.com"
    user = django_user_model.objects.create_user(email=email, password=None)
    # Use this:

    a_password = "Kls3#$df03a/"  # noqa: S105
    url = reverse(
        "custom_account_password_set",
    )

    data = urlencode({"new_password1": a_password, "new_password2": a_password})
    client.force_login(user)

    get_response = client.get(
        url,
    )
    assert "set your password" in str(get_response.content).lower()

    response = client.post(
        url,
        data,
        content_type="application/x-www-form-urlencoded",
    )

    assert response.status_code == 302
    assert response.url == "/"
    # Check success message
    messages = list(get_messages(response.wsgi_request))
    assert any("Your password has been set successfully!" in str(m) for m in messages)

    user.refresh_from_db()
    assert user.check_password(a_password) is True
