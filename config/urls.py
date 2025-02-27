# ruff: noqa
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.urls import include
from django.urls import path
from django.views import defaults as default_views
from django.views.generic import TemplateView
from drf_spectacular.views import SpectacularAPIView
from drf_spectacular.views import SpectacularSwaggerView
from rest_framework.authtoken.views import obtain_auth_token
from scaleos.users.views import custom_set_password

urlpatterns = [
    path("", TemplateView.as_view(template_name="pages/home.html"), name="home"),
    path(
        "about/",
        TemplateView.as_view(template_name="pages/about.html"),
        name="about",
    ),
    # Django Admin, use {% url 'admin:index' %}
    path(settings.ADMIN_URL, admin.site.urls),
    # User management
    path("user/", include("scaleos.users.urls", namespace="users")),
    path(
        "account/email/password/set/",
        custom_set_password,
        name="custom_account_password_set",
    ),
    path("account/", include("allauth.urls")),
    # Your stuff: custom urls includes go here
    # Oele
    path(
        "organization/",
        include("scaleos.organizations.urls", namespace="organizations"),
    ),
    path(
        "htmx/event/",
        include("scaleos.events.urls_htmx", namespace="events_htmx"),
    ),
    path(
        "event/",
        include("scaleos.events.urls", namespace="events"),
    ),
    path(
        "reservation/",
        include("scaleos.reservations.urls", namespace="reservations"),
    ),
    path(
        "htmx/reservation/",
        include("scaleos.reservations.urls_htmx", namespace="reservations_htmx"),
    ),
    # Media files
    path("system/health/", include("health_check.urls")),
    *static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT),
]
if settings.DEBUG:
    # Static file serving when using Gunicorn + Uvicorn for local web socket development
    urlpatterns += staticfiles_urlpatterns()

# API URLS
urlpatterns += [
    # API base url
    path("api/", include("config.api_router")),
    # DRF auth token
    path("api/auth-token/", obtain_auth_token),
    path("api/schema/", SpectacularAPIView.as_view(), name="api-schema"),
    path(
        "api/docs/",
        SpectacularSwaggerView.as_view(url_name="api-schema"),
        name="api-docs",
    ),
]

if settings.DEBUG:
    # This allows the error pages to be debugged during development, just visit
    # these url in browser to see how these error pages look like.
    urlpatterns += [
        path(
            "400/",
            default_views.bad_request,
            kwargs={"exception": Exception("Bad Request!")},
        ),
        path(
            "403/",
            default_views.permission_denied,
            kwargs={"exception": Exception("Permission Denied")},
        ),
        path(
            "404/",
            default_views.page_not_found,
            kwargs={"exception": Exception("Page not Found")},
        ),
        path("500/", default_views.server_error),
    ]
    if "debug_toolbar" in settings.INSTALLED_APPS:
        import debug_toolbar

        urlpatterns = [
            path("__debug__/", include(debug_toolbar.urls)),
            path("utils/", include("scaleos.utils.urls", namespace="utils")),
        ] + urlpatterns
