from django.db.models.signals import post_delete
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import VATPriceLine


@receiver(post_save, sender=VATPriceLine)
def recalculate_price_on_save(sender, instance, **kwargs):
    if instance.price:
        instance.price.recalculate_vat_totals()


@receiver(post_delete, sender=VATPriceLine)
def recalculate_price_on_delete(sender, instance, **kwargs):
    if instance.price:
        instance.price.recalculate_vat_totals()
