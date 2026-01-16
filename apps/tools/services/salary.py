from typing import Dict, Any


def calculate_salary(cleaned_data: Dict[str, Any]) -> Dict[str, float]:
    brutto_salary = float(cleaned_data["brutto_salary"])
    # TODO (finance/bug): Konwersja Decimal -> float
    # TODO (finance): Jeśli to kalkulator wynagrodzeń/finansów, trzymaj obliczenia w Decimal end-to-end.
    # TODO (finance): Zwracaj kwoty jako Decimal lub jako stringi sformatowane do 2 miejsc.

    pension_contribution_employer = round(brutto_salary * (9.76 / 100), 2)
    accident_contribution = round(brutto_salary * (2 / 100), 2)
    labour_fund_contribution = round(brutto_salary * (2.45 / 100), 2)
    disability_contribution_employer = round(brutto_salary * (6 / 100), 2)
    # TODO (maint): Te stawki są "magic numbers" i mogą się zmieniać (prawo/parametry).
    # TODO (maint): Wyciągnij je do stałych lub konfiguracji (np. dict RATES = {...}) z komentarzem źródła i datą.

    pension_contribution_employee = round(brutto_salary * (9.76 / 100), 2)
    disability_contribution_employee = round(brutto_salary * (1.5 / 100), 2)
    sickness_contribution = round(brutto_salary * (2.45 / 100), 2)

    total_social_contribution = (
        pension_contribution_employee
        + disability_contribution_employee
        + sickness_contribution
    )

    health_insurance_base = brutto_salary - total_social_contribution
    health_insurance = round(health_insurance_base * (9 / 100), 2)
    # TODO (finance): Upewnij się, że baza nie schodzi poniżej 0 przy skrajnych danych (walidacja inputu).

    income_tax_base = round(
        brutto_salary
        - total_social_contribution
        - 250
        - health_insurance,
        2
    )
    # TODO (finance/maint): "250" wygląda jak ryczałt kosztów uzyskania przychodu (KUP) — to się zmienia i zależy od warunków.
    # TODO (finance/maint): "425" wygląda jak ulga/kwota zmniejszająca podatek w uproszczonym modelu — też zależna od przepisów.
    # TODO (finance): Rozważ parametryzację (np. cleaned_data zawiera KUP/ulgę) albo stałe z opisem.

    income_tax_before_relief = round(income_tax_base * 0.17, 2)
    income_tax = max(round(income_tax_before_relief - 425, 0), 0)
    # TODO (finance/bug): Zaokrąglanie podatku do 0 miejsc (round(..., 0)) zwraca float typu 123.0.
    # TODO (finance): Jeśli to ma być "pełne złote", rozważ int() po round lub użyj Decimal i quantize do "1".
    # TODO (finance): Upewnij się, czy najpierw odejmujesz ulgę, a potem zaokrąglasz — kolejność ma znaczenie w podatkach.

    employer_netto_cost = (
        brutto_salary
        + pension_contribution_employer
        + accident_contribution
        + labour_fund_contribution
        + disability_contribution_employer
    )

    employee_netto_salary = (
        brutto_salary
        - health_insurance
        - income_tax
        - round(
            pension_contribution_employee
            + disability_contribution_employee
            + sickness_contribution,
            2
        )
    )
    # TODO (style): round(...) na sumie składek jest zbędny, bo składki już są roundowane do 2 miejsc.
    # TODO (finance): Jeśli przejdziesz na Decimal, wykonuj zaokrąglenie na końcu i konsekwentnie w jednym miejscu.

    return {
        "employer_netto_cost": round(employer_netto_cost, 2),
        "employee_netto_salary": round(employee_netto_salary, 2),
    }
    # TODO (maint): Ten kalkulator jest uproszczony i zależny od przepisów. Dodaj docstring/komentarz:
    # TODO (maint): - dla jakiego typu umowy (UoP? zlecenie?) i roku obowiązuje
    # TODO (maint): - jakie przyjęto założenia (np. brak PPK, brak progów podatkowych, brak 2. progu itp.)

