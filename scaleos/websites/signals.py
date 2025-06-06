import logging



from django.db.models.signals import post_save, post_delete, post_migrate
from django.dispatch import receiver
from scaleos.websites.models import WebsiteDomain, Website
from django.core.cache import cache

import asyncio
import redis.asyncio as aioredis
from django.conf import settings

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)




@receiver(post_migrate)
def ensure_domain_names(sender, **kwargs):
    logger.info("Ensuring domain names")
    from scaleos.websites.models import WebsiteDomain
    WebsiteDomain.objects.get_or_create(domain_name='localhost')
    WebsiteDomain.objects.get_or_create(domain_name='dev.waerboom.com')
    WebsiteDomain.objects.get_or_create(domain_name='scaleos.net')
    WebsiteDomain.objects.get_or_create(domain_name='eenspringkasteel.be')
    WebsiteDomain.objects.get_or_create(domain_name='*.eenphotobooth.be')





@receiver([post_save, post_delete], sender=WebsiteDomain)
def clear_website_cache(sender, instance, **kwargs):
    cache_key = f"website_for_{instance.domain_name}"
    logger.debug("Clearing cache key: %s", cache_key)
    cache.delete(cache_key)



@receiver(post_save, sender=WebsiteDomain)
def assign_primary_domain_if_none(sender, instance, created, **kwargs):
    if instance.website:
        org = instance.website.organization
        if created and org.primary_domain is None:
            org.primary_domain = instance
            org.save()

