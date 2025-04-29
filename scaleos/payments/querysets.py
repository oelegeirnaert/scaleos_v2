from django.db import models
from django.db.models import Sum
from moneyed import Money


class PaymentRequestQuerySet(models.QuerySet):
    def total_by_currency(
        self,
        expected_currencies=None,
        payment_status=None,
        date_from=None,
        date_to=None,
    ):
        qs = self

        if payment_status:
            if isinstance(payment_status, (list, tuple)):
                qs = qs.filter(payment__status__in=payment_status)
            else:
                qs = qs.filter(payment__status=payment_status)

        if date_from:
            qs = qs.filter(created_at__gte=date_from)

        if date_to:
            qs = qs.filter(created_at__lte=date_to)

        grouped = qs.values("paid_amount_currency").annotate(
            total_amount=Sum("paid_amount"),
        )

        result = {
            item["paid_amount_currency"]: Money(
                item["total_amount"],
                item["paid_amount_currency"],
            )
            for item in grouped
        }

        if expected_currencies:
            for currency_code in expected_currencies:
                if currency_code not in result:
                    result[currency_code] = Money(0, currency_code)

        return result


class PaymentRequestManager(models.Manager):
    def get_queryset(self):
        return PaymentRequestQuerySet(self.model, using=self._db)

    def total_by_currency(self, *args, **kwargs):
        return self.get_queryset().total_by_currency(*args, **kwargs)
