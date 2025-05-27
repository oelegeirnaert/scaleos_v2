import pytest

from scaleos.users.functions import get_user_from_mail
from scaleos.users.tests import model_factories as user_factories

pytestmark = pytest.mark.django_db


def test_get_user_from_mail():
    user = user_factories.UserFactory.create(email="josk@hotmail.com")
    assert get_user_from_mail("josk@hotmail.com") == user
    assert get_user_from_mail("undefined@hotmail.com") is None
