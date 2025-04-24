import logging

from django.conf import settings
from django.core.cache import cache

from scaleos.organizations.models import Enterprise

logger = logging.getLogger(__name__)


def get_software_owner():
    logger.debug("Getting software owner")
    registered_id = settings.SOFTWARE_OWNING_COMPANY_REGISTERED_ID
    registered_country = settings.SOFTWARE_OWNING_COMPANY_REGISTERED_COUNTRY

    software_owning_company = cache.get("software_owner", None)
    if software_owning_company:
        logger.debug("loaded company from cache")
        return software_owning_company

    if registered_id and registered_country:
        logger.debug("loaded company from db")
        # Assuming only one organization exists for your site
        organization, organization_created = Enterprise.objects.get_or_create(
            registered_country=registered_country,
            registration_id=registered_id,
        )
        if organization_created:
            logger.info("A new company has been created")
        else:
            logger.debug("Company already exists")

        logger.debug("Software owner is %s", organization)
        # Cache the organization details
        cache.set(
            "software_owner",
            organization,
            timeout=None,
        )  # Timeout=None for persistent cache
        return organization

    logger.warning("We cannot get the software owner")
    return None
