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
        #todo (style): warto zachować spojność z innymi formularzami gdzie przekazywałeś usera jawnie
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
            # TODO (bug/maint): Jeśli user nie zostanie przekazany, formularz będzie zawsze nieużywalny (route=None).
            # TODO (maint): Możesz wymusić user jako wymagany (raise w __init__), jeśli to zawsze powinno być podane.

        self.fields["carrier"].queryset = Carrier.objects.order_by("name")

        carrier_id = None

        if "carrier" in self.data:
            carrier_id = self.data.get("carrier")
            # TODO (bug): self.data.get("carrier") zwraca string. Jeśli ktoś wstrzyknie niefajną wartość,
            # TODO (bug): filter(carrier_id=...) to łyknie, ale warto zrobić walidację/cast do int (try/except).

        elif self.instance and self.instance.carrier_id:
            carrier_id = self.instance.carrier_id

        if carrier_id:
            qs = Driver.objects.filter(carrier_id=carrier_id)
            # TODO (data): Jeśli driver_1/driver_2 mają być zawsze z tego samego carrier co w polu carrier,
            #      dopnij walidację w clean() (szczególnie jeśli ktoś podeśle POST ręcznie).
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

    # TODO (data/security): Dodaj walidację spójności między carrier a driver_1/driver_2:
    # TODO (data/security): - driver_1 i driver_2 muszą należeć do wybranego carrier
    # TODO (data/security): - driver_1 != driver_2 (jeśli nie chcesz duplikatu)
    # TODO (data/security): To najlepiej zrobić w clean(), bo to zależności między polami.
