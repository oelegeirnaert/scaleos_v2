import logging

from django.db.models.signals import post_save
from django.dispatch import receiver

from scaleos.organizations.models import Enterprise
from scaleos.organizations.models import Organization
from scaleos.organizations.models import OrganizationStyling

logger = logging.getLogger(__name__)


@receiver(post_save, sender=Organization)
@receiver(post_save, sender=Enterprise)
def create_styling_for_organization(sender, instance, created, **kwargs):
    logger.debug("Creating a new styling for organization %s", instance.pk)
    if created:
        logger.debug("New styling created")
        OrganizationStyling.objects.get_or_create(organization=instance)
