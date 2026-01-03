from django import forms

from apps.company.models import Carrier
from apps.drivers.models import Driver
from ..models import Calculation, Route


class CalculationForm(forms.ModelForm):
    class Meta:
        model = Calculation
        fields = [
            "route",
            "carrier",
            "driver_1",
            "driver_2",
            "date",
        ]
        widgets = {
            "date": forms.DateInput(
                attrs={"type": "date", "class": "input input-bordered w-full"}
            ),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)

        for field in self.fields.values():
            existing = field.widget.attrs
            field.widget.attrs = {
                **existing,
                "class": (existing.get("class", "") + " input input-bordered w-full").strip(),
            }
        self.fields["route"].empty_label = None
        self.fields["carrier"].empty_label = "Select carrier"
        self.fields["driver_1"].empty_label = None
        self.fields["driver_2"].empty_label = None
        if self.user:
            self.fields["route"].queryset = Route.objects.filter(user=self.user).order_by("name")
        else:
            self.fields["route"].queryset = Route.objects.none()
        self.fields["carrier"].queryset = Carrier.objects.order_by("name")

        carrier_id = None

        if "carrier" in self.data:
            carrier_id = self.data.get("carrier")


        elif self.instance and self.instance.carrier_id:
            carrier_id = self.instance.carrier_id

        if carrier_id:
            qs = Driver.objects.filter(carrier_id=carrier_id)
            self.fields["driver_1"].queryset = qs
            self.fields["driver_2"].queryset = qs
        else:
            self.fields["driver_1"].queryset = Driver.objects.none()
            self.fields["driver_2"].queryset = Driver.objects.none()

    def clean_route(self):
        route = self.cleaned_data["route"]
        if self.user and route.user_id != self.user.id:
            raise forms.ValidationError("Invalid route.")
        return route
