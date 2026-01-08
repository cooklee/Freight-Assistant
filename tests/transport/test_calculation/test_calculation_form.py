import pytest

from apps.transport.forms import CalculationForm
from apps.transport.models import Route


@pytest.mark.django_db
def test_calculation_form_limits_route_queryset_to_user(user, user_2):
    Route.objects.create(user=user_2, name="foreign_route")

    form = CalculationForm(user=user)
    assert all(r.user_id == user.id for r in form.fields["route"].queryset)


@pytest.mark.django_db
def test_calculation_form_clean_route_rejects_foreign_route(user, user_2):
    foreign_route = Route.objects.create(user=user_2, name="foreign_route")

    data = {
        "route": foreign_route.id,
        "carrier": "",
        "driver_1": "",
        "driver_2": "",
        "date": "2026-01-12",
    }

    form = CalculationForm(data=data, user=user)
    assert not form.is_valid()
    assert "route" in form.errors
