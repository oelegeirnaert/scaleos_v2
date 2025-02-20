from django.urls import resolve
from django.urls import reverse

from scaleos.users.models import User


def test_detail(user: User):
    assert reverse("users:detail", kwargs={"pk": user.pk}) == f"/user/{user.pk}/"
    assert resolve(f"/user/{user.pk}/").view_name == "users:detail"


def test_update():
    assert reverse("users:update") == "/user/~update/"
    assert resolve("/user/~update/").view_name == "users:update"


def test_redirect():
    assert reverse("users:redirect") == "/user/~redirect/"
    assert resolve("/user/~redirect/").view_name == "users:redirect"
