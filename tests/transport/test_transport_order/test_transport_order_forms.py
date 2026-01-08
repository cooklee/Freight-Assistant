from decimal import Decimal

import pytest

from apps.transport.forms import TransportOrderForm, TransportOrderUpdateForm


@pytest.mark.django_db
def test_transport_order_form_calculates_carrier_cost_and_profit(customer, carrier, driver_list):
    driver_1 = driver_list.filter(carrier=carrier).first()

    data = {
        "customer": customer.id,
        "carrier": carrier.id,
        "driver_1": driver_1.id,
        "driver_2": "",
        "loading_place": 'A',
        "unloading_place": 'B',
        "distance_km": "100",
        "price_for_customer": "2000.00",
        "rate_per_km": "2.00",
    }

    form = TransportOrderForm(data=data)
    assert form.is_valid(), form.errors

    order = form.save(commit=False)

    assert order.carrier_cost == Decimal("200.00")
    assert order.profit == Decimal("1800.00")


@pytest.mark.django_db
def test_transport_order_update_form_calculates_profit(customer, carrier, driver_list):
    driver_1 = driver_list.filter(carrier=carrier).first()

    data = {
        "customer": customer.id,
        "carrier": carrier.id,
        "driver_1": driver_1.id,
        "driver_2": "",
        "loading_place": 'A',
        "unloading_place": 'B',
        "distance_km": "100",
        "price_for_customer": "2000.00",
        "rate_per_km": "2.00",
        "carrier_cost": "300.00",
        "profit": "0.00",
    }

    form = TransportOrderUpdateForm(data=data)
    assert form.is_valid(), form.errors

    order = form.save(commit=False)
    assert order.profit == Decimal("1700.00")
