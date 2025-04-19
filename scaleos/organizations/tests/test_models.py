import logging

import pytest

from scaleos.organizations.tests.model_factories import OrganizationFactory
from scaleos.users.tests.model_factories import UserFactory

logger = logging.getLogger(__name__)


@pytest.mark.django_db
class TestOrganization:
    def test_add_b2c(self):
        user = UserFactory.create()
        organization = OrganizationFactory.create()
        organization.add_b2c(user)
        assert organization.customers.filter(b2c=user.person).exists()
