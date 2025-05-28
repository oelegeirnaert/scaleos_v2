import datetime

import pytest

from scaleos.hr.tests import model_factories


class Person:
    def test_user_is_not_created_automatically_on_person_creation(self, faker):
        person = model_factories.PersonFactory.create()
        assert person.user is None


@pytest.mark.django_db
def test_age(faker):
    birthday = datetime.date(year=1987, month=5, day=11)
    person = model_factories.PersonFactory.create(birthday=birthday)

    today = datetime.date(year=2024, month=12, day=31)
    assert person.get_age(today) == 37

    today = datetime.date(year=2025, month=1, day=1)
    assert person.get_age(today) == 37

    today = datetime.date(year=2025, month=2, day=7)
    assert person.get_age(today) == 37

    today = datetime.date(year=2025, month=5, day=11)
    assert person.get_age(today) == 38

    today = datetime.date(year=2025, month=8, day=5)
    assert person.get_age(today) == 38

    today = None
    age = person.get_age(today)
    assert age is not None
    assert isinstance(age, int)

    person_without_birthday = model_factories.PersonFactory.create(birthday=None)
    assert person_without_birthday.age is None


@pytest.mark.django_db
def test_person_to_string(faker):
    person = model_factories.PersonFactory.create(
        first_name="Oele",
        family_name="Geirnaert",
    )
    assert str(person) == "Oele Geirnaert"

    person_without_name = model_factories.PersonFactory.create(
        first_name="",
        family_name="",
    )
    assert str(person_without_name) != ""
