import logging
import redis.asyncio as aioredis
import fnmatch
from django.conf import settings
from asgiref.sync import sync_to_async
from scaleos.websites.models import WebsiteDomain

logger = logging.getLogger(__name__)


REDIS_KEY = "valid_domains"
REDIS_TTL = 60  # seconds

@sync_to_async
def _fetch_domains_from_db():
    logger.debug("Fetching domains from DB")
    result = list(WebsiteDomain.objects.values_list("domain_name", flat=True))
    logger.debug("Fetched domains: %s", result)
    return result



async def get_cached_domains():
    logger.debug("Getting cached domains")
    redis = await aioredis.from_url(settings.REDIS_URL)
    domains = await redis.get(REDIS_KEY)
    if domains:
        return set(domains.decode().split(","))
    # Cache miss → fetch from DB
    domain_list = await _fetch_domains_from_db()
    await redis.set(REDIS_KEY, ",".join(domain_list), ex=REDIS_TTL)
    return set(domain_list)

def domain_matches(request_host, domain_list):
    for domain in domain_list:
        if fnmatch.fnmatch(request_host, domain):
            return True
    return False