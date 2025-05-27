import logging

from django.conf import settings

logger = logging.getLogger(__name__)


def body_classes(request):
    """
    Adds CSS classes to the body tag based on the resolved URL.
    Handles cases where request or resolver_match might be None.
    """
    logger.debug("loading body_classes")

    # Check if request object itself is None
    if request is None:
        logger.debug("Request is None, returning empty classes.")
        return {}

    # Check if the URL was successfully resolved (resolver_match will be None otherwise)
    if request.resolver_match is None:
        logger.debug(
            "Request.resolver_match is None (URL not resolved), \
                     returning empty classes.",
        )
        return {}

    # If both request and resolver_match exist, extract the names
    logger.debug(
        "Request and resolver_match found, extracting app_name and view_name.",
    )
    return {
        "app_name": request.resolver_match.app_name,
        "view_name": request.resolver_match.url_name,
    }


def hideable_page_parts(request):
    logger.debug("loading hideable_page_parts")
    if request is None:
        return {}

    show_header = True
    try:
        request.GET["hide-header"]
        show_header = False
    except KeyError:
        pass

    show_footer = True
    try:
        request.GET["hide-footer"]
        show_footer = False
    except KeyError:
        pass

    return {
        "show_header": show_header,
        "show_footer": show_footer,
    }


def theme_colors(request):
    logger.debug("loading theme_colors")
    if request is None:
        return {}

    """
    Adds Tailwind theme colors to the context.
    """
    default_colors = {
        "primary": "lime-500",
        "secondary": "gray-500",
        "accent": "blue-500",
        "danger": "red-500",
    }

    return {
        "TAILWIND_THEME_COLORS": getattr(
            settings,
            "TAILWIND_THEME_COLORS",
            default_colors,
        ),
    }
