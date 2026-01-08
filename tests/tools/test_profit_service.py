import pytest

from apps.tools.services.profit import calculate_profit


@pytest.mark.django_db
def test_calculate_profit_basic():
    cleaned_data = {
        "tonne_kilometer_price": 0.50,
        "number_of_vehicles": 2,
        "vehicle_efficiency": 2000,
        "year_work_days": 250,
        "leasing": 0,
        "fuel": 0,
        "salaries": 100000,
        "taxes": 0,
        "invoices": 0,
        "other_expenses": 0,
    }

    result = calculate_profit(cleaned_data)

    assert result["revenue"] == round((2000 * 2) * 0.50 * 250, 2)
    assert result["costs"] == 100000
    assert result["profit"] == round(result["revenue"] - result["costs"], 2)
    assert "profit_perc" in result


@pytest.mark.django_db
def test_calculate_profit_handles_zero_revenue():
    cleaned_data = {
        "tonne_kilometer_price": 0,
        "number_of_vehicles": 0,
        "vehicle_efficiency": 0,
        "year_work_days": 0,
        "leasing": 0,
        "fuel": 0,
        "salaries": 0,
        "taxes": 0,
        "invoices": 0,
        "other_expenses": 0,
    }

    result = calculate_profit(cleaned_data)
    assert result["revenue"] == 0
    assert result["profit_perc"] == 0.0
