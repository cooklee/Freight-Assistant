from django import forms
from apps.company.models import Carrier


class CarrierAddForm(forms.ModelForm):

    class Meta:
        model = Carrier
        fields = ["name", "nip", "address", "email", "phone"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({"class": "input input-bordered w-full"})

    def clean_nip(self):
        nip = self.cleaned_data["nip"]
        if not nip.isdigit():
            raise forms.ValidationError("NIP must contain digits only")
        if len(nip) != 10:
            raise forms.ValidationError("NIP must be exactly 10 digits")
        return nip

    def clean_phone(self):
        phone = self.cleaned_data["phone"]
        if not phone.isdigit():
            raise forms.ValidationError("Phone must contain digits only")
        return phone
