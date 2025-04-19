from factory import SubFactory
from factory.django import DjangoModelFactory

from scaleos.events.tests import model_factories as event_factories
from scaleos.organizations.tests import model_factories as organization_factories
from scaleos.payments.tests.model_factories import PriceMatrixItemFactory
from scaleos.reservations import models as reservation_models
from scaleos.users.tests import model_factories as user_factories


class EventReservationFactory(
    DjangoModelFactory[reservation_models.EventReservation],
):
    organization = SubFactory(organization_factories.OrganizationFactory)
    user = SubFactory(user_factories.UserFactory)
    event = SubFactory(event_factories.EventFactory)

    class Meta:
        model = reservation_models.EventReservation


class BrunchReservationFactory(
    DjangoModelFactory[reservation_models.EventReservation],
):
    class Meta:
        model = reservation_models.EventReservation


class ReservationFactory(
    DjangoModelFactory[reservation_models.Reservation],
):
    organization = SubFactory(organization_factories.OrganizationFactory)
    user = SubFactory(user_factories.UserFactory)

    class Meta:
        model = reservation_models.Reservation


class ReservationLineFactory(
    DjangoModelFactory[reservation_models.ReservationLine],
):
    reservation = SubFactory(ReservationFactory)
    price_matrix_item = SubFactory(PriceMatrixItemFactory)

    class Meta:
        model = reservation_models.ReservationLine


class EventReservationSettingsFactory(
    DjangoModelFactory[reservation_models.EventReservationSettings],
):
    class Meta:
        model = reservation_models.EventReservationSettings


class ReservationUpdateFactory(
    DjangoModelFactory[reservation_models.ReservationUpdate],
):
    reservation = SubFactory(ReservationFactory)

    class Meta:
        model = reservation_models.ReservationUpdate


class OrganizationConfirmFactory(
    ReservationUpdateFactory,
    DjangoModelFactory[reservation_models.OrganizationConfirm],
):
    class Meta:
        model = reservation_models.OrganizationConfirm


class OrganizationCancelFactory(
    ReservationUpdateFactory,
    DjangoModelFactory[reservation_models.OrganizationCancel],
):
    class Meta:
        model = reservation_models.OrganizationCancel


class OrganizationRefuseFactory(
    ReservationUpdateFactory,
    DjangoModelFactory[reservation_models.OrganizationRefuse],
):
    class Meta:
        model = reservation_models.OrganizationRefuse


class RequesterConfirmFactory(
    ReservationUpdateFactory,
    DjangoModelFactory[reservation_models.RequesterConfirm],
):
    class Meta:
        model = reservation_models.RequesterConfirm


class RequesterCancelFactory(
    ReservationUpdateFactory,
    DjangoModelFactory[reservation_models.RequesterCancel],
):
    class Meta:
        model = reservation_models.RequesterCancel


class WaitingUserEmailConfirmationFactory(
    ReservationUpdateFactory,
    DjangoModelFactory[reservation_models.WaitingUserEmailConfirmation],
):
    class Meta:
        model = reservation_models.WaitingUserEmailConfirmation


class InvalidReservationFactory(
    ReservationUpdateFactory,
    DjangoModelFactory[reservation_models.InvalidReservation],
):
    class Meta:
        model = reservation_models.InvalidReservation
