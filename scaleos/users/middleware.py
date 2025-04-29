from django.core.cache import cache
from django.utils import timezone


class UserTimezoneMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            cache_key = f"user_timezone:{request.user.pk}"
            user_tz = cache.get(cache_key)

            if not user_tz:
                user_tz = request.user.timezone
                # Cache it for a day (or your desired TTL)
                cache.set(cache_key, user_tz, timeout=86400)

            timezone.activate(user_tz)
        else:
            timezone.deactivate()

        return self.get_response(request)
