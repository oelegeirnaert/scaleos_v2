from django import forms


class ResengoExcelUploadForm(forms.Form):
    excel_file = forms.FileField(
        label="Select an Excel file",
        help_text="Only .xlsx files are allowed.",
        widget=forms.FileInput(attrs={"accept": ".xlsx"}),
    )

    overwrite_existing_data = forms.BooleanField(
        label="Overwrite existing data",
        help_text="Check this box to overwrite existing users with the same email.",
        required=False,  # Make the checkbox optional
        initial=False,  # Default to unchecked
    )

    def clean_excel_file(self):
        excel_file = self.cleaned_data["excel_file"]
        if not excel_file.name.endswith(".xlsx"):
            msg = "Invalid file type. Only .xlsx files are allowed."
            raise forms.ValidationError(
                msg,
            )
        return excel_file
