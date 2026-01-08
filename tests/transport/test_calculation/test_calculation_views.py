from unittest.mock import patch

import pytest
from django.urls import reverse

from apps.transport.models import Stop, Calculation


@pytest.mark.django_db
def test_calculation_list_view_only_user_records(client, user, user_2, calculation):
    client.force_login(user)

    Calculation.objects.create(
        user=user_2,
        route=calculation.route,
        carrier=calculation.carrier,
        driver_1=calculation.driver_1,
        date="2026-01-13",
    )

    response = client.get(reverse("calculation-list"))
    assert response.status_code == 200
    calculations = response.context["calculations"]
    assert all(c.user_id == user.id for c in calculations)


@pytest.mark.django_db
def test_calculation_create_get(client, user):
    client.force_login(user)

    response = client.get(reverse("calculation-create"))
    assert response.status_code == 200
    assert "form" in response.context


@pytest.mark.django_db
def test_calculation_create_post(client, user, route, carrier, driver_list):
    client.force_login(user)

    Stop.objects.create(
        route=route,
        stop_number=1,
        stop_type="START_FROM_BASE",
        location="A",
        driver_participates=False,
    )
    Stop.objects.create(
        route=route,
        stop_number=2,
        stop_type="LOADING",
        location="B",
        driver_participates=False,
    )
    Stop.objects.create(
        route=route,
        stop_number=3,
        stop_type="UNLOADING",
        location="C",
        driver_participates=False,
    )

    driver_1 = driver_list.filter(carrier=carrier).first()

    data = {
        "route": route.id,
        "carrier": carrier.id,
        "driver_1": driver_1.id,
        "driver_2": "",
        "date": "2026-01-12",
    }

    distances = [(300, 216), (200, 149)]

    def fake_get_distance_duration(origin, destination):
        km, minutes = distances.pop(0)
        return km, minutes

    with patch(
            "apps.transport.services.schedule_builder.get_distance_duration",
            side_effect=fake_get_distance_duration
    ):
        response = client.post(reverse("calculation-create"), data=data)

    assert response.status_code == 302
    calc = Calculation.objects.latest("id")
    assert calc.user_id == user.id
    assert calc.schedule
    assert (calc.total_break_time_minutes or 0) >= 45
    assert response.url == reverse("calculation-detail", args=[calc.id])


@pytest.mark.django_db
def test_calculation_create_post_invalid_data(client, user):
    client.force_login(user)

    response = client.post(reverse("calculation-create"), data={})
    assert response.status_code == 200
    assert "form" in response.context
    assert response.context["form"].errors


@pytest.mark.django_db
def test_calculation_detail_view_owner_can_access(client, user, calculation):
    client.force_login(user)

    response = client.get(reverse("calculation-detail", args=[calculation.id]))
    assert response.status_code == 200
    assert response.context["calculation"].id == calculation.id


@pytest.mark.django_db
def test_calculation_detail_view_non_owner_gets_404(client, user_2, calculation):
    client.force_login(user_2)

    response = client.get(reverse("calculation-detail", args=[calculation.id]))
    assert response.status_code == 404


@pytest.mark.django_db
def test_calculation_update_get(client, user, calculation):
    client.force_login(user)

    response = client.get(reverse("calculation-update", args=[calculation.id]))
    assert response.status_code == 200
    assert "form" in response.context
    assert response.context.get("update") is True


@pytest.mark.django_db
def test_calculation_update_post(client, user, calculation):
    client.force_login(user)

    route = calculation.route
    if route.stops.count() < 2:
        Stop.objects.create(
            route=route,
            stop_number=1,
            stop_type="START_FROM_BASE",
            location="A",
            driver_participates=False,
        )
        Stop.objects.create(
            route=route,
            stop_number=2,
            stop_type="UNLOADING",
            location="B",
            driver_participates=False,
        )

    data = {
        "route": calculation.route.id,
        "carrier": calculation.carrier.id,
        "driver_1": calculation.driver_1.id,
        "driver_2": "",
        "date": "2026-01-21",
    }

    legs = calculation.route.stops.count() - 1
    distances = [(100, 60)] * legs

    def fake_get_distance_duration(origin, destination):
        km, minutes = distances.pop(0)
        return km, minutes

    with patch(
            "apps.transport.services.schedule_builder.get_distance_duration",
            side_effect=fake_get_distance_duration
    ):
        response = client.post(reverse("calculation-update", args=[calculation.id]), data=data)

    assert response.status_code == 302
    calculation.refresh_from_db()
    assert str(calculation.date) == "2026-01-21"
    assert calculation.schedule
    assert response.url == reverse("calculation-detail", args=[calculation.id])


@pytest.mark.django_db
def test_calculation_update_post_invalid_data(client, user, calculation):
    client.force_login(user)

    response = client.post(reverse("calculation-update", args=[calculation.id]), data={})
    assert response.status_code == 200
    assert "form" in response.context
    assert response.context["form"].errors
    assert response.context.get("update") is True


@pytest.mark.django_db
def test_calculation_delete_get_renders_confirm_page(client, user, calculation):
    client.force_login(user)

    response = client.get(reverse("calculation-delete", args=[calculation.id]))
    assert response.status_code == 200
    assert "calculation" in response.context
    assert response.context["calculation"].id == calculation.id


@pytest.mark.django_db
def test_calculation_delete_view_owner_deletes(client, user, calculation):
    client.force_login(user)

    response = client.post(reverse("calculation-delete", args=[calculation.id]))
    assert response.status_code == 302
    assert not Calculation.objects.filter(id=calculation.id).exists()


@pytest.mark.django_db
def test_calculation_delete_view_non_owner_gets_404(client, user_2, calculation):
    client.force_login(user_2)

    response = client.post(reverse("calculation-delete", args=[calculation.id]))
    assert response.status_code == 404
