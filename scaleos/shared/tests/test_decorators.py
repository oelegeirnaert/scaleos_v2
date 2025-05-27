import pytest
from django.contrib.auth.models import AnonymousUser
from django.core.cache import cache
from django.http import HttpResponse
from django.http import HttpResponseForbidden
from django.test import RequestFactory

from scaleos.shared.decorators import limit_unauthenticated_submissions
from scaleos.users.models import User


@pytest.fixture
def factory():
    return RequestFactory()


@pytest.fixture
def user(db):
    return User.objects.create_user(email="testuser@hotmail.com", password="12345")  # noqa: S106


@pytest.fixture(autouse=True)
def clear_cache():
    cache.clear()
    yield
    cache.clear()


def dummy_view(request):
    return HttpResponse("OK")


def test_authenticated_user_not_limited(factory, user):
    request = factory.post("/")
    request.user = user
    view = limit_unauthenticated_submissions("form_a", limit=3)(dummy_view)
    response = view(request)
    assert response.status_code == 200


def test_unauthenticated_user_within_limit(factory):
    view = limit_unauthenticated_submissions("form_a", limit=3)(dummy_view)

    for _ in range(3):
        request = factory.post("/")
        request.user = AnonymousUser()
        request.META["REMOTE_ADDR"] = "1.2.3.4"
        response = view(request)
        assert response.status_code == 200


def test_unauthenticated_user_exceeds_limit(factory):
    view = limit_unauthenticated_submissions("form_b", limit=2)(dummy_view)

    for _ in range(2):
        request = factory.post("/")
        request.user = AnonymousUser()
        request.META["REMOTE_ADDR"] = "5.6.7.8"
        response = view(request)
        assert response.status_code == 200

    # 3rd submission should be blocked
    request = factory.post("/")
    request.user = AnonymousUser()
    request.META["REMOTE_ADDR"] = "5.6.7.8"
    response = view(request)
    assert isinstance(response, HttpResponseForbidden)
    assert response.status_code == 403


def test_different_form_ids_are_tracked_separately(factory):
    view1 = limit_unauthenticated_submissions("form_x", limit=1)(dummy_view)
    view2 = limit_unauthenticated_submissions("form_y", limit=1)(dummy_view)

    request = factory.post("/")
    request.user = AnonymousUser()
    request.META["REMOTE_ADDR"] = "9.9.9.9"

    assert view1(request).status_code == 200
    assert (
        view2(request).status_code == 200
    )  # Should still work despite form_x being hit


def test_get_request_does_not_increment(factory):
    view = limit_unauthenticated_submissions("form_get", limit=1)(dummy_view)

    request = factory.get("/")
    request.user = AnonymousUser()
    request.META["REMOTE_ADDR"] = "10.0.0.1"

    response = view(request)
    assert response.status_code == 200

    # Should still allow POST after GET
    request = factory.post("/")
    request.user = AnonymousUser()
    request.META["REMOTE_ADDR"] = "10.0.0.1"
    response = view(request)
    assert response.status_code == 200
