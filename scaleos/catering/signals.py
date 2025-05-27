import logging

from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Dish
from .models import Product
from .tasks import import_mealdb_dishes
from .tasks import sync_product_from_openfoodfacts

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


@receiver(post_save, sender=Product)
def trigger_openfoodfacts_sync(sender, instance, created, **kwargs):
    logger.debug("Triggering sync for product %s", instance)
    if created or not instance.last_synced:
        sync_product_from_openfoodfacts.delay(instance.id)
    else:
        logger.debug(
            "It is not necessary to sync product, already did on: %s",
            instance.last_synced,
        )


@receiver(post_save, sender=Dish)
def fetch_recipe_on_dish_creation(sender, instance, created, **kwargs):
    logger.debug("Trying to fetch the dish from mealdb")
    if not created:
        return

    # Only trigger the task if the dish has a name
    if instance.name:
        import_mealdb_dishes.delay(search_query=instance.name)
