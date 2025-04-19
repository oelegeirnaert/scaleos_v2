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


class OrganizationCustomerFactory(
    DjangoModelFactory[organization_models.OrganizationCustomer],
):
    class Meta:
        model = organization_models.OrganizationCustomer


class OrganizationStylingFactory(
    DjangoModelFactory[organization_models.OrganizationStyling],
):
    class Meta:
        model = organization_models.OrganizationStyling


class OrganizationPaymentMethodFactory(
    DjangoModelFactory[organization_models.OrganizationPaymentMethod],
):
    class Meta:
        model = organization_models.OrganizationPaymentMethod
