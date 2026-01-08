import pytest

from apps.tools.services.salary import calculate_salary


@pytest.mark.django_db
def test_calculate_salary_returns_expected_keys():
    result = calculate_salary({"brutto_salary": "7000.00"})

    assert "employer_netto_cost" in result
    assert "employee_netto_salary" in result


@pytest.mark.django_db
def test_calculate_salary_values_are_reasonable():
    result = calculate_salary({"brutto_salary": "7000.00"})
    assert result["employer_netto_cost"] > 8000
    assert 5000 < result["employee_netto_salary"] < 5200
