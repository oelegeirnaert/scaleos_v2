from factory import SubFactory
from factory.django import DjangoModelFactory
from moneyed import EUR
from moneyed import Money

from scaleos.organizations.tests.model_factories import OrganizationFactory
from scaleos.payments import models as payment_models


class PriceMatrixFactory(DjangoModelFactory[payment_models.PriceMatrix]):
    class Meta:
        model = payment_models.PriceMatrix


class AgePriceMatrixItemFactory(DjangoModelFactory[payment_models.AgePriceMatrixItem]):
    class Meta:
        model = payment_models.AgePriceMatrixItem


class AgePriceMatrixFactory(DjangoModelFactory[payment_models.AgePriceMatrix]):
    class Meta:
        model = payment_models.AgePriceMatrix


class PriceFactory(DjangoModelFactory[payment_models.Price]):
    vat_included = Money(121, EUR)
    vat_excluded = Money(100, EUR)
    vat = Money(121, EUR)

    class Meta:
        model = payment_models.Price


class BulkPriceMatrixFactory(DjangoModelFactory[payment_models.BulkPriceMatrix]):
    class Meta:
        model = payment_models.BulkPriceMatrix


class BulkPriceMatrixItemFactory(
    DjangoModelFactory[payment_models.BulkPriceMatrixItem],
):
    class Meta:
        model = payment_models.BulkPriceMatrixItem


class PaymentRequestFactory(
    DjangoModelFactory[payment_models.PaymentRequest],
):
    class Meta:
        model = payment_models.PaymentRequest


class PaymentFactory(
    DjangoModelFactory[payment_models.Payment],
):
    class Meta:
        model = payment_models.Payment


class EPCMoneyTransferPaymentFactory(
    DjangoModelFactory[payment_models.EPCMoneyTransferPayment],
):
    class Meta:
        model = payment_models.EPCMoneyTransferPayment


class PriceMatrixItemFactory(
    DjangoModelFactory[payment_models.PriceMatrixItem],
):
    class Meta:
        model = payment_models.PriceMatrixItem


class PaymentConditionFactory(DjangoModelFactory[payment_models.PaymentCondition]):
    class Meta:
        model = payment_models.PaymentCondition


class EventReservationPaymentConditionFactory(
    PaymentConditionFactory,
    DjangoModelFactory[payment_models.EventReservationPaymentCondition],
):
    class Meta:
        model = payment_models.EventReservationPaymentCondition


class EventReservationPaymentSettingsFactory(
    DjangoModelFactory[payment_models.EventReservationPaymentSettings],
):
    class Meta:
        model = payment_models.EventReservationPaymentSettings


class PaymentSettingsFactory(DjangoModelFactory[payment_models.PaymentSettings]):
    class Meta:
        model = payment_models.PaymentSettings


class PaymentMethodFactory(DjangoModelFactory[payment_models.PaymentMethod]):
    organization = SubFactory(OrganizationFactory)
    class Meta:
        model = payment_models.PaymentMethod


class EPCMoneyTransferPaymentMethodFactory(
    DjangoModelFactory[payment_models.EPCMoneyTransferPaymentMethod],
):
    class Meta:
        model = payment_models.EPCMoneyTransferPaymentMethod


class CashPaymentMethodFactory(DjangoModelFactory[payment_models.CashPaymentMethod]):
    class Meta:
        model = payment_models.CashPaymentMethod


class VoucherPaymentMethodFactory(
    DjangoModelFactory[payment_models.VoucherPaymentMethod],
):
    class Meta:
        model = payment_models.VoucherPaymentMethod

class MolliePaymentMethodFactory(
    DjangoModelFactory[payment_models.MolliePaymentMethod]):
    class Meta:
        model = payment_models.MolliePaymentMethod




class PaymentProposalFactory(DjangoModelFactory[payment_models.PaymentProposal]):
    class Meta:
        model = payment_models.PaymentProposal


class VATPriceLineFactory(DjangoModelFactory[payment_models.VATPriceLine]):
    class Meta:
        model = payment_models.VATPriceLine
