from decimal import Decimal

from django import forms

from apps.company.models import Customer, Carrier
from apps.drivers.models import Driver
from apps.transport.models import TransportOrder


class TransportOrderBaseForm(forms.ModelForm):
    numeric_fields = [
        'distance_km',
        'price_for_customer',
        'rate_per_km',
        'carrier_cost',
        'profit',
    ]
    # TODO (style): Zamiast listy stringów rozważ ustawianie widgetów przez Meta.widgets dla konkretnych pól,
    # TODO (style): albo pętlę po self.fields z isinstance(field, forms.DecimalField/IntegerField) jeśli to zawsze numeryczne.

    class Meta:
        model = TransportOrder
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field in self.fields.values():
            field.widget.attrs.update({'class': 'input input-bordered w-full'})

        for name in self.numeric_fields:
            if name in self.fields:
                self.fields[name].widget = forms.TextInput(
                    attrs={
                        'class': 'input input-bordered w-full',
                        'inputmode': 'decimal',
                        'placeholder': self.fields[name].label,
                    }
                )
                # TODO (ux): Jeśli to pola Decimal/Integer, rozważ NumberInput z step (np. step="0.01") zamiast TextInput.
                # TODO (validation): inputmode to tylko podpowiedź dla klawiatury — walidację i tak musi robić Django.

        if not self.instance.pk:
            self.fields["distance_km"].initial = ""
            # TODO (ux): Jeśli distance_km jest DecimalField/IntegerField, ustawianie initial="" bywa dziwne.
            # TODO (ux): Lepiej zostawić None/brak initial i pozwolić formom ogarnąć pustą wartość.

        self.fields["customer"].empty_label = "Select customer"
        self.fields["carrier"].empty_label = "Select carrier"
        self.fields["driver_1"].empty_label = "Select driver"
        self.fields["driver_2"].empty_label = "Select co-driver"

        self.fields["driver_1"].label = "Driver"
        self.fields["driver_2"].label = "Co-Driver"

        self.fields["customer"].queryset = Customer.objects.order_by("name")
        self.fields["carrier"].queryset = Carrier.objects.order_by("name")

        if "carrier" in self.data:
            carrier_id = self.data.get("carrier")
            qs = Driver.objects.filter(carrier_id=carrier_id)
            # TODO (bug): carrier_id z self.data jest stringiem. Rozważ cast do int (try/except) albo walidację.

            self.fields["driver_1"].queryset = qs
            self.fields["driver_2"].queryset = qs

        elif self.instance and self.instance.carrier_id:
            carrier_id = self.instance.carrier_id
            qs = Driver.objects.filter(carrier_id=carrier_id)

            self.fields["driver_1"].queryset = qs
            self.fields["driver_2"].queryset = qs

            self.fields["driver_1"].initial = self.instance.driver_1
            self.fields["driver_2"].initial = self.instance.driver_2

        else:
            self.fields["driver_1"].queryset = Driver.objects.none()
            self.fields["driver_2"].queryset = Driver.objects.none()

        # TODO (data/security): Brakuje walidacji spójności:
        # TODO (data/security): - driver_1 / driver_2 muszą należeć do wybranego carrier
        # TODO (data/security): - driver_1 != driver_2 (jeśli nie chcesz duplikatu)
        # TODO (data/security): To najlepiej zrobić w clean() bazowej formy (zależności między polami).


class TransportOrderUpdateForm(TransportOrderBaseForm):
    class Meta:
        model = TransportOrder
        exclude = ["user", ]
        # TODO (style): Zbędny przecinek/spacja w liście: ["user"] wystarczy.

    def save(self, commit=True):
        instance = super().save(commit=False)

        carrier_cost = self.cleaned_data.get("carrier_cost")
        customer_price = self.cleaned_data.get("price_for_customer")

        if carrier_cost and customer_price:
            instance.profit = Decimal(customer_price) - Decimal(carrier_cost)
            # TODO (finance): Jeśli to już Decimal w cleaned_data, Decimal(...) jest zbędne.
            # TODO (finance): Upewnij się, że wartości są Decimal, a nie float/str (precyzja!).

        if commit:
            instance.save()

        return instance


class TransportOrderForm(TransportOrderBaseForm):
    class Meta:
        model = TransportOrder
        exclude = ["carrier_cost", "profit", 'user', 'created_at']
        # TODO (maint/security): exclude + base fields="__all__" = ryzyko, że nowe pola "magicznie" trafią do formularza.
        # TODO (maint/security): Rozważ jawne fields dla create/update.

    def save(self, commit=True):
        instance = super().save(commit=False)

        km = self.cleaned_data.get("distance_km")
        rate = self.cleaned_data.get("rate_per_km")
        customer_price = self.cleaned_data.get("price_for_customer")

        if km and rate:
            instance.carrier_cost = Decimal(km) * Decimal(rate)
            # TODO (finance): Jeśli km/rate są Decimal, to Decimal(...) niepotrzebne. Trzymaj typy spójnie.

        if km and customer_price:
            instance.profit = Decimal(customer_price) - (Decimal(km) * Decimal(rate))
            # TODO (bug): Tu sprawdzasz km i customer_price, ale używasz też rate.
            # TODO (bug): Jeśli rate jest None/0, dostaniesz błąd lub zły wynik. Powinno być: if km and rate and customer_price:
            #  Dodatkowo: (customer_price - carrier_cost) jest czytelniejsze niż powtarzanie km*rate.
            #  Możesz policzyć carrier_cost raz i użyć.

        if commit:
            instance.save()

        return instance
        # TODO (business): Jeśli carrier_cost/profit są pochodne, rozważ policzenie ich w modelu (save/clean) lub serwisie,
        #  żeby niezależnie od miejsca zapisu (admin, API, import) logika była spójna.
