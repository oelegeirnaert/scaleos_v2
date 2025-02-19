import pytest
from django.urls import reverse


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
