import pytest
from django.urls import reverse

from apps.transport.models import TransportOrder


@pytest.mark.django_db
def test_order_list_only_user_records(client, user, user_2, transport_order, customer, carrier, driver_list):
    client.force_login(user)

    driver_1 = driver_list.filter(carrier=carrier).first()
    TransportOrder.objects.create(
        user=user_2,
        customer=customer,
        carrier=carrier,
        driver_1=driver_1,
        distance_km=50,
        price_for_customer="1000.00",
        rate_per_km="2.00",
        carrier_cost="100.00",
        profit="900.00",
    )

    response = client.get(reverse("order-list"))
    assert response.status_code == 200
    orders = response.context["orders"]
    assert all(o.user_id == user.id for o in orders)


@pytest.mark.django_db
def test_order_create_get(client, user):
    client.force_login(user)
    response = client.get(reverse("order-create"))
    assert response.status_code == 200
    assert "form" in response.context


@pytest.mark.django_db
def test_order_create_post(client, user, customer, carrier, driver_list):
    client.force_login(user)
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

    response = client.post(reverse("order-create"), data=data)
    assert response.status_code == 302
    order = TransportOrder.objects.latest("id")
    assert order.user_id == user.id
    assert response.url == reverse("order-list")


@pytest.mark.django_db
def test_order_create_post_bad_data(client, user):
    client.force_login(user)
    response = client.post(reverse("order-create"), data={})
    assert response.status_code == 200
    assert "form" in response.context
    assert response.context["form"].errors


@pytest.mark.django_db
def test_order_detail_owner_can_access(client, user, transport_order):
    client.force_login(user)
    response = client.get(reverse("order-detail", args=[transport_order.id]))
    assert response.status_code == 200
    assert response.context["order"].id == transport_order.id


@pytest.mark.django_db
def test_order_detail_non_owner_gets_404(client, user_2, transport_order):
    client.force_login(user_2)
    response = client.get(reverse("order-detail", args=[transport_order.id]))
    assert response.status_code == 404


@pytest.mark.django_db
def test_order_update_get(client, user, transport_order):
    client.force_login(user)
    response = client.get(reverse("order-update", args=[transport_order.id]))
    assert response.status_code == 200
    assert "form" in response.context


@pytest.mark.django_db
def test_order_update_post(client, user, transport_order, customer, carrier, driver_list):
    client.force_login(user)
    driver_1 = driver_list.filter(carrier=carrier).first()

    data = {
        "customer": customer.id,
        "carrier": carrier.id,
        "driver_1": driver_1.id,
        "loading_place": 'A',
        "unloading_place": 'B',
        "distance_km": "120",
        "price_for_customer": "2500.00",
        "carrier_cost": "300.00",
        "profit": "2200.00",
        "rate_per_km": "2.00",
    }

    response = client.post(reverse("order-update", args=[transport_order.id]), data=data)
    assert response.status_code == 302
    transport_order.refresh_from_db()
    assert response.url == reverse("order-detail", args=[transport_order.id])
    for key, value in data.items():
        if key in ("customer", "carrier", "driver_1"):
            assert getattr(transport_order, key).id == int(value or 0)
        else:
            assert str(getattr(transport_order, key)) == str(value)


@pytest.mark.django_db
def test_order_update_post_bad_data(client, user, transport_order):
    client.force_login(user)
    response = client.post(reverse("order-update", args=[transport_order.id]), data={})
    assert response.status_code == 200
    assert "form" in response.context
    assert response.context["form"].errors


@pytest.mark.django_db
def test_order_update_non_owner_gets_404(client, user_2, transport_order):
    client.force_login(user_2)
    response = client.get(reverse("order-update", args=[transport_order.id]))
    assert response.status_code == 404


@pytest.mark.django_db
def test_order_delete_get(client, user, transport_order):
    client.force_login(user)
    response = client.get(reverse("order-delete", args=[transport_order.id]))
    assert response.status_code == 200
    assert "order" in response.context


@pytest.mark.django_db
def test_order_delete_post(client, user, transport_order):
    client.force_login(user)
    response = client.post(reverse("order-delete", args=[transport_order.id]))
    assert response.status_code == 302
    assert not TransportOrder.objects.filter(id=transport_order.id).exists()
    assert response.url == reverse("order-list")


@pytest.mark.django_db
def test_order_delete_post_non_owner_gets_404(client, user_2, transport_order):
    client.force_login(user_2)
    response = client.post(reverse("order-delete", args=[transport_order.id]))
    assert response.status_code == 404
