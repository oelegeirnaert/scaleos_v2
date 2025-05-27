# signals.py

import logging

from django.db.models.signals import post_save
from django.dispatch import receiver

from scaleos.hr.models import Person
from scaleos.users.models import User

logger = logging.getLogger(__name__)


@receiver(post_save, sender=User)
def create_person_for_user(sender, instance, created, **kwargs):
    logger.debug("Creating a new person for user %s", instance.pk)
    if created:
        logger.debug("New person created")
        Person.objects.get_or_create(user=instance)
