from factory.django import DjangoModelFactory

from scaleos.organizations import models as organization_models


class EnterpriseFactory(
    DjangoModelFactory[organization_models.Enterprise],
):
    class Meta:
        model = organization_models.Enterprise


class OrganizationFactory(
    DjangoModelFactory[organization_models.Organization],
):
    class Meta:
        model = organization_models.Organization


class OrganizationOwnerFactory(
    DjangoModelFactory[organization_models.OrganizationOwner],
):
    class Meta:
        model = organization_models.OrganizationOwner
