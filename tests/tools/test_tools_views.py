import pytest
from django.urls import reverse


@pytest.mark.django_db
@pytest.mark.parametrize("url_name", ["leasing", "salary", "profit"])
def test_tools_views_require_login(client, url_name):
    response = client.get(reverse(url_name))
    assert response.status_code == 302
    assert "/login" in response.url


@pytest.mark.django_db
@pytest.mark.parametrize("url_name", ["leasing", "salary", "profit"])
def test_tools_views_get(client, user, url_name):
    client.force_login(user)
    response = client.get(reverse(url_name))
    assert response.status_code == 200
    assert "form" in response.context


@pytest.mark.django_db
def test_leasing_post_invalid_data(client, user):
    client.force_login(user)
    response = client.post(reverse("leasing"), data={})
    assert response.status_code == 200
    assert response.context["form"].errors


@pytest.mark.django_db
def test_leasing_post(client, user):
    client.force_login(user)

    data = {
        "vehicle_price": "350000",
        "initial_fee": "10",
        "leasing_administration_fee": "500",
        "vehicle_registration_fee": "250",
        "domestic_transport_license": "880",
        "eu_community_license": "8000",
        "leasing_installment": "6500",
        "insurance": "1200",
        "gap_insurance": "200",
        "security_installment": "300",
    }

    response = client.post(reverse("leasing"), data=data)
    assert response.status_code == 200
    assert "result" in response.context
    assert "total_initial_payment" in response.context["result"]
    assert "monthly_cost" in response.context["result"]


@pytest.mark.django_db
def test_salary_post_invalid_data(client, user):
    client.force_login(user)
    response = client.post(reverse("salary"), data={})
    assert response.status_code == 200
    assert response.context["form"].errors


@pytest.mark.django_db
def test_salary_post(client, user):
    client.force_login(user)
    response = client.post(reverse("salary"), data={"brutto_salary": "7000.00"})
    assert response.status_code == 200
    assert "result" in response.context
    assert "employer_netto_cost" in response.context["result"]
    assert "employee_netto_salary" in response.context["result"]


@pytest.mark.django_db
def test_profit_post_invalid_data(client, user):
    client.force_login(user)
    response = client.post(reverse("profit"), data={})
    assert response.status_code == 200
    assert response.context["form"].errors


@pytest.mark.django_db
def test_profit_post(client, user):
    client.force_login(user)

    data = {
        "tonne_kilometer_price": "0.50",
        "number_of_vehicles": "2",
        "vehicle_efficiency": "2000",
        "year_work_days": "250",
        "leasing": "0",
        "fuel": "0",
        "salaries": "100000",
        "taxes": "0",
        "invoices": "0",
        "other_expenses": "0",
    }

    response = client.post(reverse("profit"), data=data)
    assert response.status_code == 200
    assert "result" in response.context
    assert "revenue" in response.context["result"]
    assert "profit" in response.context["result"]
