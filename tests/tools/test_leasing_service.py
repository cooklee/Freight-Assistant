import pytest
from decimal import Decimal

from apps.tools.services.leasing import calculate_leasing


@pytest.mark.parametrize("cleaned_data, expected_initial, expected_monthly", [
    (
        {
            "vehicle_price": 350000,
            "initial_fee": 10,
            "vehicle_registration_fee": 250,
            "domestic_transport_license": 880,
            "leasing_installment": 6500,
            "insurance": 1200,
            "leasing_administration_fee": 500,
            "eu_community_license": 8000,
            "gap_insurance": 200,
            "security_installment": 300,
        },
        # initial_cost_base = 350000*0.10 + 250 + 880 + 500 + 8000 = 44630
        # monthly_cost_base = 6500 + 1200 + 200 + 300 = 8200
        # total_initial_payment = 44630 + 8200 = 52830
        Decimal("52830"),
        Decimal("8200"),
    ),
])
def test_calculate_leasing(cleaned_data, expected_initial, expected_monthly):
    result = calculate_leasing(cleaned_data)

    assert result["total_initial_payment"] == expected_initial
    assert result["monthly_cost"] == expected_monthly


def test_calculate_leasing_optional_fields_default_to_zero():
    cleaned_data = {
        "vehicle_price": 100000,
        "initial_fee": 10,
        "vehicle_registration_fee": 0,
        "domestic_transport_license": 0,
        "leasing_installment": 1000,
        "insurance": 200,
    }

    result = calculate_leasing(cleaned_data)
    assert "total_initial_payment" in result
    assert "monthly_cost" in result
