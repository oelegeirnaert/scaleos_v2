from factory import SubFactory
from factory.django import DjangoModelFactory
from faker import Faker

from scaleos.organizations import models as organization_models

faker = Faker()


class EnterpriseFactory(
    DjangoModelFactory[organization_models.Enterprise],
):
    name = faker.company()

    class Meta:
        model = organization_models.Enterprise


class OrganizationFactory(
    DjangoModelFactory[organization_models.Organization],
):
    name = faker.company()

    class Meta:
        model = organization_models.Organization


class OrganizationMemberFactory(
    DjangoModelFactory[organization_models.OrganizationMember],
):
    organization = SubFactory(OrganizationFactory)

    class Meta:
        model = organization_models.OrganizationMember


class OrganizationEmployeeFactory(
    DjangoModelFactory[organization_models.OrganizationEmployee],
):
    class Meta:
        model = organization_models.OrganizationEmployee

class CustomerFactory(
    DjangoModelFactory[organization_models.Customer],
):
    organization = SubFactory(OrganizationFactory)

    class Meta:
        model = organization_models.Customer

class B2BCustomerFactory(
    CustomerFactory,
    DjangoModelFactory[organization_models.B2BCustomer],

):
    b2b = SubFactory(OrganizationFactory)

    class Meta:
        model = organization_models.B2BCustomer


class OrganizationOwnerFactory(
    DjangoModelFactory[organization_models.OrganizationOwner],
):
    class Meta:
        model = organization_models.OrganizationOwner


class B2CCustomerFactory(
        CustomerFactory,
    DjangoModelFactory[organization_models.B2CCustomer],

):
    class Meta:
        model = organization_models.B2CCustomer


class OrganizationStylingFactory(
    DjangoModelFactory[organization_models.OrganizationStyling],
):
    class Meta:
        model = organization_models.OrganizationStyling

