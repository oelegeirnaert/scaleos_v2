from pathlib import Path

import openpyxl
import pytest
from django.core.exceptions import ValidationError

from scaleos.organizations.tasks import import_resengo_excel
from scaleos.organizations.tests import model_factories as organization_factories
from scaleos.users import models as user_models


@pytest.mark.django_db
def test_import_resengo_excel_task(faker, settings):
    # Create a dummy excel file
    test_excel_file_path = Path(settings.MEDIA_ROOT / "test.xlsx")
    try:
        # Create a dummy excel file
        workbook = openpyxl.Workbook()
        sheet = workbook.active
        sheet.append(
            [
                "First_Name",
                "Last_Name",
                "Email",
                "EmailCount",
                "EmailError",
                "NOEmailErrors",
                "Gender",
                "SiteLanguage",
                "BirthDay",
                "Address",
                "PostalCode",
                "City",
                "Country",
                "Telephone",
                "Mobile",
                "Company",
                "Company_Address",
                "LastActivityDate",
                "Company_PostalCode",
                "Company_City",
                "Company_Country",
                "Company_Email",
                "Company_VAT",
                "LogonTimes",
                "NOVisits",
            ],
        )
        sheet.append(
            [
                "Oele",
                "Geirnaert",
                "oelegeirnaert@hotmail.com",
                "EmailCount",
                "EmailError",
                "NOEmailErrors",
                "Gender",
                "NL",
                "2/26/1974",
                "Fossebaan 174",
                "1741",
                "Wambeek",
                "BE",
                "Telephone",
                "+32-0485517786",
                "Company",
                "Company_Address",
                "12/25/24 12:00",
                "Company_PostalCode",
                "Company_City",
                "Company_Country",
                "Company_Email",
                "Company_VAT",
                "LogonTimes",
                "NOVisits",
            ],
        )
        workbook.save(test_excel_file_path)

        organization = organization_factories.OrganizationFactory.create()
        # Call the celery task
        result = import_resengo_excel(
            test_excel_file_path,
            organization_id=organization.pk,
        )

        # Assert
        assert "Excel file imported successfully!" in result

        # Check if the data has been imported
        assert user_models.User.objects.count() == 1
        user = user_models.User.objects.first()
        assert user.email == "oelegeirnaert@hotmail.com"

    except ValidationError as e:
        pytest.fail(f"Test failed with exception: {e}")
    finally:
        # Clean up
        if Path.exists(test_excel_file_path):
            Path.unlink(test_excel_file_path)
