import importlib
import logging
from unittest.mock import patch

import pytest
from django.contrib import admin
from django.urls import reverse

logger = logging.getLogger(__name__)


@pytest.mark.django_db
@patch("webpush.utils.get_templatetag_context", return_value={})
def test_every_single_admin_view(mock_context, admin_client):
    excluded_models = [
        # "PaymentSettings",
        # "PaymentMethod",
        "WebsiteImage",
    ]

    for model in admin.site._registry:  # noqa: SLF001
        if "scaleos" in str(model):
            the_module_name = str(model).split(".")[1]  # scaleos.payments.models.
            full_module_name = f"scaleos.{the_module_name}.tests.model_factories"

            model_name = model.__name__
            if model_name in excluded_models:
                continue

            model_factory_name = f"{model_name}Factory"
            full_module_name = f"{full_module_name}"

            module = importlib.import_module(full_module_name)
            logger.info("Testing %s from %s", model_factory_name, full_module_name)
            class_ = getattr(module, model_factory_name)
            instance = class_()

            url = reverse(
                f"admin:{the_module_name.lower()}_{model_name.lower()}_change",
                kwargs={"object_id": instance.pk},
            )
            logger.info("Testing %s", url)
            response = admin_client.get(url)
            status_code = response.status_code
            logger.info("Status code: %s", status_code)
            assert status_code == 200, (
                "probably a field does no longer exist in the corresponding view"
            )
