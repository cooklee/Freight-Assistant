from typing import Dict, Any


def calculate_salary(cleaned_data: Dict[str, Any]) -> Dict[str, float]:
    brutto_salary = float(cleaned_data["brutto_salary"])

    pension_contribution_employer = round(brutto_salary * (9.76 / 100), 2)
    accident_contribution = round(brutto_salary * (2 / 100), 2)
    labour_fund_contribution = round(brutto_salary * (2.45 / 100), 2)
    disability_contribution_employer = round(brutto_salary * (6 / 100), 2)

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

    income_tax_base = round(
        brutto_salary
        - total_social_contribution
        - 250
        - health_insurance,
        2
    )

    income_tax_before_relief = round(income_tax_base * 0.17, 2)
    income_tax = max(round(income_tax_before_relief - 425, 0), 0)

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

    return {
        "employer_netto_cost": round(employer_netto_cost, 2),
        "employee_netto_salary": round(employee_netto_salary, 2),
    }
