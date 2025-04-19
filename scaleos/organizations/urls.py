from django.urls import path

from scaleos.organizations import views as organization_views

app_name = "organizations"
urlpatterns = [
    path(
        "",
        view=organization_views.organization,
        name="organization",
    ),
    path(
        "deactivate/",
        view=organization_views.deactivate_organization,
        name="deactivate_organization",
    ),
    path(
        "<str:organization_slug>/",
        view=organization_views.organization,
        name="organization",
    ),
    path(
        "<str:organization_slug>/activate/",
        view=organization_views.activate_organization,
        name="activate_organization",
    ),
    path(
        "enterprise/<str:enterprise_slug>/",
        view=organization_views.enterprise,
        name="enterprise",
    ),
    path(
        "<str:organization_slug>/customer/",
        view=organization_views.customers,
        name="customers",
    ),
    path(
        "<str:organization_slug>/concept/",
        view=organization_views.concepts,
        name="concepts",
    ),
    path(
        "<str:organization_slug>/event/",
        view=organization_views.events,
        name="events",
    ),
    path(
        "<str:organization_slug>/import/resengo/",
        organization_views.import_resengo_excel,
        name="import_resengo_excel",
    ),
]
