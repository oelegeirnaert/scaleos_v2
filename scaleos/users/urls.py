from django.urls import path

from scaleos.notifications import views as notification_views
from scaleos.reservations import views as reservation_views
from scaleos.users import views as user_views

from .views import user_detail_view
from .views import user_redirect_view
from .views import user_update_view

app_name = "users"
urlpatterns = [
    path("~redirect/", view=user_redirect_view, name="redirect"),
    path("~update/", view=user_update_view, name="update"),
    path("<int:pk>/", view=user_detail_view, name="detail"),
    path("account/", view=user_views.account, name="account"),
    path("organization/", view=user_views.organization, name="organization"),
    path(
        "organization/<uuid:organization_public_key>/",
        view=user_views.organization,
        name="organization",
    ),
    path("notification/", view=notification_views.notification, name="notification"),
    path(
        "notification/<uuid:notification_public_key>/",
        view=notification_views.notification,
        name="notification",
    ),
    path("guest/invite/", view=reservation_views.guestinvite, name="guestinvite"),
    path("reservation/", view=reservation_views.reservation, name="reservation"),
    path(
        "reservation/<uuid:reservation_public_key>/",
        view=reservation_views.reservation,
        name="reservation",
    ),
]
