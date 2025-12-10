from django import forms
from django.forms import inlineformset_factory

from ..models import Route, Stop


class StopForm(forms.ModelForm):
    class Meta:
        model = Stop
        fields = ["stop_number", "stop_type", "location", "driver_participates"]
        widgets = {
            "stop_number": forms.NumberInput(attrs={
                "class": "input input-bordered w-full"
            }),
            "stop_type": forms.Select(attrs={
                "class": "select select-bordered w-full",
            }),
            "location": forms.TextInput(attrs={
                "class": "input input-bordered w-full autocomplete-location"
            }),
            "driver_participates": forms.CheckboxInput(attrs={
                "class": "checkbox"
            }),
        }
        labels = {
            "stop_number": "Stop #",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


        self.fields["stop_type"].required = True
        self.fields["stop_type"].choices = [
            c for c in self.fields["stop_type"].choices if c[0] != ""
        ]




StopFormSet = inlineformset_factory(
    Route,
    Stop,
    form=StopForm,
    extra=1,
    can_delete=True
)
