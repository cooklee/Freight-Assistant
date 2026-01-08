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

        if not self.instance.pk:
            self.fields["distance_km"].initial = ""

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


class TransportOrderUpdateForm(TransportOrderBaseForm):
    class Meta:
        model = TransportOrder
        exclude = ["user", ]

    def save(self, commit=True):
        instance = super().save(commit=False)

        carrier_cost = self.cleaned_data.get("carrier_cost")
        customer_price = self.cleaned_data.get("price_for_customer")

        if carrier_cost and customer_price:
            instance.profit = Decimal(customer_price) - Decimal(carrier_cost)

        if commit:
            instance.save()

        return instance


class TransportOrderForm(TransportOrderBaseForm):
    class Meta:
        model = TransportOrder
        exclude = ["carrier_cost", "profit", 'user', 'created_at']

    def save(self, commit=True):
        instance = super().save(commit=False)

        km = self.cleaned_data.get("distance_km")
        rate = self.cleaned_data.get("rate_per_km")
        customer_price = self.cleaned_data.get("price_for_customer")

        if km and rate:
            instance.carrier_cost = Decimal(km) * Decimal(rate)

        if km and customer_price:
            instance.profit = Decimal(customer_price) - (Decimal(km) * Decimal(rate))

        if commit:
            instance.save()

        return instance
