from django import forms

from .models import Driver


class DriverForm(forms.ModelForm):
    class Meta:
        model = Driver
        exclude = ('carrier',)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field in self.fields.values():
            field.widget.attrs.update({'class': 'input input-bordered w-full'})

    def clean_phone(self):
        phone = self.cleaned_data["phone"]
        # TODO (bug): self.cleaned_data["phone"] rzuci KeyError, jeśli pole nie przeszło walidacji podstawowej
        # TODO (bug): albo jest opcjonalne. Bezpieczniej użyć self.cleaned_data.get("phone").


        if not phone.isdigit():
            raise forms.ValidationError("Phone must contain digits only.")
        return phone
        # TODO (data): Warto by było znormalizować wartość phone tak by zawsze miała ten sam schemat
        # TODO (data): biblioteka phonenumbers albo RegexValidator.
