
from scaleos.hr import models as hr_models
from scaleos.hr.tests import model_factories
import pytest

import logging
import datetime

@pytest.mark.django_db
def test_age(faker):
    birthday = datetime.date(year=1987, month=5, day=11)
    person = model_factories.PersonFactory.create(birthday=birthday) 

    today = datetime.date(year=2024, month=12, day=31) 
    assert 37 == person.get_age(today)

    today = datetime.date(year=2025, month=1, day=1) 
    assert 37 == person.get_age(today)

    today = datetime.date(year=2025, month=2, day=7)
    assert 37 == person.get_age(today)

    today = datetime.date(year=2025, month=5, day=11)  
    assert 38 == person.get_age(today)

    today = datetime.date(year=2025, month=8, day=5) 
    assert 38 == person.get_age(today)

    today = None
    assert 37 >= person.get_age(today)

    person_without_birthday = model_factories.PersonFactory.create(birthday=None) 
    assert person_without_birthday.age is None

@pytest.mark.django_db
def test_person_to_string(faker):
    person = model_factories.PersonFactory.create(name="Oele", family_name="Geirnaert") 
    assert "Oele Geirnaert" == str(person)

    person_without_name = model_factories.PersonFactory.create(name=None, family_name=None)
    assert "" != str(person_without_name)