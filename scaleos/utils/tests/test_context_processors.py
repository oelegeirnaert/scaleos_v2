import pytest
from django.conf import settings
from django.test import RequestFactory
from django.urls import reverse

from scaleos.utils.context_processors import theme_colors


@pytest.mark.django_db
def test_body_classes(client):
    url = reverse("home")
    res = client.get(url)
    assert "<header" in str(res.content)


@pytest.mark.django_db
def test_hideable_page_parts(client):
    url = reverse("home")
    res = client.get(url)
    assert "<header" in str(res.content)

    url = reverse("home")
    res = client.get(f"{url}/?hide-header")
    assert "<header" not in str(res.content)

    url = reverse("home")
    res = client.get(f"{url}/?hide-footer")
    assert "<footer" not in str(res.content)

    url = reverse("home")
    res = client.get(f"{url}/?hide-header")
    assert "<header" not in str(res.content)

    url = reverse("home")
    res = client.get(f"{url}/?hide-header&hide-footer")
    assert "<footer" not in str(res.content)
    assert "<header" not in str(res.content)


@pytest.fixture
def factory():
    return RequestFactory()


@pytest.fixture
def default_colors():
    return {
        "primary": "lime-500",
        "secondary": "gray-500",
        "accent": "blue-500",
        "danger": "red-500",
    }


def test_theme_colors_in_context(factory, default_colors):
    """Test that theme colors are correctly added to the context"""
    request = factory.get("/")
    context = theme_colors(request)

    assert "TAILWIND_THEME_COLORS" in context
    assert context["TAILWIND_THEME_COLORS"] == getattr(
        settings,
        "TAILWIND_THEME_COLORS",
        default_colors,
    )


@pytest.mark.django_db
def test_theme_colors_override(factory):
    """Test that custom theme colors from settings are applied"""
    custom_colors = {
        "primary": "red-600",
        "secondary": "gray-700",
        "accent": "green-500",
        "danger": "yellow-500",
    }

    settings.TAILWIND_THEME_COLORS = custom_colors
    request = factory.get("/")
    context = theme_colors(request)

    assert context["TAILWIND_THEME_COLORS"] == custom_colors
