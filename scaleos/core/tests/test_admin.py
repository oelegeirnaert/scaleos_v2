import importlib

import pytest
from django.contrib import admin
from django.urls import reverse


@pytest.mark.django_db
def test_every_single_admin_view(admin_client):
    for model in admin.site._registry:  # noqa: SLF001
        if "scaleos" in str(model):
            the_module_name = str(model).split(".")[1]  # scaleos.payments.models.
            full_module_name = f"scaleos.{the_module_name}.tests.model_factories"

            model_name = model.__name__
            model_factory_name = f"{model_name}Factory"
            full_module_name = f"{full_module_name}"

            module = importlib.import_module(full_module_name)
            class_ = getattr(module, model_factory_name)
            instance = class_()

            url = reverse(
                f"admin:{the_module_name.lower()}_{model_name.lower()}_change",
                kwargs={"object_id": instance.pk},
            )
            response = admin_client.get(url)
            assert response.status_code == 200
