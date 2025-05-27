# utils/limits.py

import hashlib
from functools import wraps

from django.core.cache import cache
from django.http import HttpResponseForbidden

from scaleos.shared.functions import get_client_ip


def get_cache_key(ip, form_id):
    hashed = hashlib.sha256(f"{ip}:{form_id}".encode()).hexdigest()
    return f"form_limit:{hashed}"


def limit_unauthenticated_submissions(form_id, limit=5, timeout=3600):
    """
    Decorator to limit unauthenticated POST submissions per IP per form.

    Args:
        form_id (str): A unique identifier for the form (e.g., "contact_form").
        limit (int): Max allowed submissions per IP before blocking.
        timeout (int): Time window in seconds for which the limit applies.

    Returns:
        Function decorator.
    """

    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if request.user.is_authenticated:
                return view_func(request, *args, **kwargs)

            if request.method == "POST":
                ip = get_client_ip(request)
                cache_key = get_cache_key(ip, form_id)
                current_count = cache.get(cache_key)

                if current_count is None:
                    cache.set(cache_key, 1, timeout)
                else:
                    if current_count >= limit:
                        return HttpResponseForbidden(
                            "Too many submissions. Please try again later.",
                        )
                    cache.incr(cache_key)

            return view_func(request, *args, **kwargs)

        return _wrapped_view

    return decorator
