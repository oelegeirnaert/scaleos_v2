from factory.django import DjangoModelFactory

from scaleos.organizations import models as organization_models


class OrganizationFactory(
    DjangoModelFactory[organization_models.Organization],
):
    class Meta:
        model = organization_models.Organization
