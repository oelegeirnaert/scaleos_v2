import logging

from django.db.models import Max
from django.db.models import Min
from django.db.models.signals import post_save

from .models import EventMix
from .models import SingleEvent

logger = logging.getLogger(__name__)


def register_signals_for_all_event_subclasses():
    for subclass in SingleEvent.__subclasses__():
        post_save.connect(update_eventmix_dates, sender=subclass, weak=False)


def update_eventmix_dates(sender, instance, **kwargs):
    logger.setLevel(logging.DEBUG)
    logger.debug("Updating datetimes for event mix")
    if isinstance(instance, EventMix):
        logger.debug("It is an event mix, so no need to update")
        return

    if instance.parent is None:
        logger.debug("No parent, thus no need to update")
        return

    children = instance.parent.children.all()
    if children.exists():
        logger.debug("Yes, children exist %s", children.count())
        starting_at = children.aggregate(Min("starting_at"))["starting_at__min"]
        logger.debug("Starting at %s", starting_at)
        ending_on = children.aggregate(Max("ending_on"))["ending_on__max"]
        logger.debug("Ending on %s", ending_on)
    else:
        starting_at = None
        ending_on = None
    EventMix.objects.filter(pk=instance.parent.pk).update(
        starting_at=starting_at,
        ending_on=ending_on,
    )
