from django.urls import path

from scaleos.payments import views_htmx as vw_htmx

app_name = "payments_htmx"

urlpatterns = [
    path(
        "request",
        vw_htmx.paymentrequest,
        name="paymentrequest",
    ),
    path(
        "request/<str:paymentrequest_public_key>/",
        vw_htmx.paymentrequest,
    name="paymentrequest",
    ),
]
