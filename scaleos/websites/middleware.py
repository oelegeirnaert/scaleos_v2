# scaleos/websites/middleware.py
import logging
from asgiref.sync import sync_to_async

from starlette.datastructures import Headers
from starlette.types import ASGIApp, Receive, Scope, Send
from scaleos.websites.host_cache import get_cached_domains, domain_matches
from django.utils.deprecation import MiddlewareMixin
from scaleos.websites.context_processors import get_website_by_host 

logger = logging.getLogger(__name__)


class AsyncHostValidationMiddleware:
    def __init__(self, app: ASGIApp):
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        headers = Headers(scope=scope)
        host = headers.get("host", "").split(":")[0]

        valid_domains = await get_cached_domains()
        logger.debug("Valid domains: %s", valid_domains)
        logger.debug("Host: %s", host)
        if not domain_matches(host, valid_domains):
            from starlette.responses import PlainTextResponse
            response = PlainTextResponse(
                f"Invalid host: {host}", status_code=400
            )
            await response(scope, receive, send)
            return

        await self.app(scope, receive, send)



class WebsiteMiddleware(MiddlewareMixin):
    def process_request(self, request):
        host = request.get_host().split(':')[0]
        request.website = get_website_by_host(host)