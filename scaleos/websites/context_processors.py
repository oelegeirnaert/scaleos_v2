import logging
from django.core.cache import cache
from scaleos.websites.models import Website, WebsiteDomain

from django.core.cache import cache
from scaleos.websites.models import Website, WebsiteDomain

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

def get_website_by_host(host: str):
    """
    Resolves a domain name to a Website, supporting wildcard domains.
    Caches results in Redis.
    """
    cache_key = f"website_for_{host}"
    website = cache.get(cache_key)
    logger.debug("Cache key: %s", cache_key)
    logger.debug("Cache value: %s", website)

    # Return cached result (even if it's None)
    if cache_key in cache:
        return website

    try:
        # Try exact match
        logger.debug("Trying exact match for host: %s", host)
        domain = WebsiteDomain.objects.select_related("website").get(domain_name=host)
        website = domain.website
    except WebsiteDomain.DoesNotExist:
        # Try wildcard match
        logger.debug("Trying wildcard match for host: %s", host)
        website = None
        parts = host.split(".")
        for i in range(1, len(parts)):
            wildcard = "*." + ".".join(parts[i:])
            try:
                domain = WebsiteDomain.objects.select_related("website").get(domain_name=wildcard)
                website = domain.website
                break
            except WebsiteDomain.DoesNotExist:
                logger.debug("No match found for wildcard: %s", wildcard)
                continue

    # Cache result (including None for negative cache)
    timeout = 60 * 10 if website else 60 * 2
    cache.set(cache_key, website, timeout=timeout)
    logger.debug("Caching result for %s with timeout %s", host, timeout)

    return website

def website_context(request):
    logger.debug("Getting website context")
    host = request.get_host().split(":")[0]
    logger.debug("Host: %s", host)
    website = get_website_by_host(host)
    logger.debug("Website: %s", website)
    return {"website": website}
