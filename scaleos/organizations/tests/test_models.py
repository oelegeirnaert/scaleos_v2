import logging

import pytest
from django.forms import ValidationError

from scaleos.hr.tests import model_factories as hr_factories
from scaleos.organizations.tests import model_factories as organization_factories
from scaleos.users.tests.model_factories import UserFactory

logger = logging.getLogger(__name__)


@pytest.mark.django_db
class TestOrganization:
    def test_add_b2c(self):
        user = UserFactory.create()
        organization = organization_factories.OrganizationFactory.create()
        organization.add_b2c(user)
        assert organization.customers.filter(b2ccustomer__person=user.person).exists()

    def test_organization_cannot_add_himself_as_a_b2b(self, faker):
        organization = organization_factories.OrganizationFactory()
        organization_b2bcustomer = organization_factories.B2BCustomerFactory(
            organization=organization,
            b2b=organization,
        )

        with pytest.raises(ValidationError) as excinfo:
            organization_b2bcustomer.clean()

        assert "you cannot add yourself as a customer" in str(excinfo.value)

    def test_customer_from_organization_can_exist_only_once(self, faker):
        organization = organization_factories.OrganizationFactory()
        person = hr_factories.PersonFactory()


        organization_customer = organization_factories.B2CCustomerFactory(
            person=person,
            organization=organization,
        )

        assert organization_customer

        duplicate_customer = organization_factories.B2CCustomerFactory(
            person=person,
            organization=organization,
        )
        with pytest.raises(ValidationError):
            duplicate_customer.clean()
