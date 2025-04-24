from django.urls import resolve
from django.urls import reverse

from scaleos.users.models import User


def test_detail(user: User):
    assert reverse("users:detail", kwargs={"pk": user.pk}) == f"/my/{user.pk}/"
    assert resolve(f"/my/{user.pk}/").view_name == "users:detail"


def test_update():
    assert reverse("users:update") == "/my/~update/"
    assert resolve("/my/~update/").view_name == "users:update"


def test_redirect():
    assert reverse("users:redirect") == "/my/~redirect/"
    assert resolve("/my/~redirect/").view_name == "users:redirect"
