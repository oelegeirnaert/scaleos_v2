import logging

from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import TimeTable

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


@receiver(post_save, sender=TimeTable)
def trigger_holidays_sync(sender, instance, created, **kwargs):
    logger.debug("Triggering holiday sync for timetable %s", instance.pk)
    instance.generate_holidays()
