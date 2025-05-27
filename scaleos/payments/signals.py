from django.db.models.signals import post_delete
from django.db.models.signals import post_save
from django.dispatch import receiver

from scaleos.payments.functions import ReferenceGenerator

from .models import PaymentRequest
from .models import VATPriceLine


@receiver(post_save, sender=VATPriceLine)
def recalculate_price_on_save(sender, instance, **kwargs):
    if instance.price:
        instance.price.recalculate_vat_totals()


@receiver(post_delete, sender=VATPriceLine)
def recalculate_price_on_delete(sender, instance, **kwargs):
    if instance.price:
        instance.price.recalculate_vat_totals()


@receiver(post_save, sender=PaymentRequest)
def generate_structured_references(sender, instance, created, **kwargs):
    updated = False

    if not instance.structured_reference_be:
        instance.structured_reference_be = (
            ReferenceGenerator.generate_structured_reference(
                base_number=instance.pk,
                decorated=True,
            )
        )
        updated = True
    else:
        ReferenceGenerator.validate_structured_reference(
            instance.structured_reference_be,
        )

    if not instance.structured_reference_sepa:
        instance.structured_reference_sepa = (
            ReferenceGenerator.generate_iso11649_reference(
                base_number=instance.pk,
            )
        )
        updated = True

    if updated:
        # Save again only if we updated any fields
        instance.save(
            update_fields=["structured_reference_be", "structured_reference_sepa"],
        )
