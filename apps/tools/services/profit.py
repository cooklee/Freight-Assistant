from typing import Dict, Any


def calculate_profit(cleaned_data: Dict[str, Any]) -> Dict[str, float]:
    tonne_kilometer_price = cleaned_data["tonne_kilometer_price"]
    number_of_vehicles = cleaned_data["number_of_vehicles"]
    vehicle_efficiency = cleaned_data["vehicle_efficiency"]
    year_work_days = cleaned_data["year_work_days"]

    leasing = cleaned_data.get("leasing") or 0
    fuel = cleaned_data.get("fuel") or 0
    salaries = cleaned_data["salaries"]
    taxes = cleaned_data.get("taxes") or 0
    invoices = cleaned_data.get("invoices") or 0
    other_expenses = cleaned_data.get("other_expenses") or 0
    # TODO tak jak w poprzednim przypadku uważaj na float i czemu to 0 nie używasz  .get("leasing", Decimal("0"))

    revenue = round(
        (vehicle_efficiency * number_of_vehicles)
        * tonne_kilometer_price
        * year_work_days,
        2
    )
    # TODO (finance): piniążki liczymy na decimal

    costs = round(
        leasing
        + fuel
        + salaries
        + taxes
        + invoices
        + other_expenses,
        2
    )
    # TODO (finance): Jak wyżej — preferuj Decimal zamiast float + round.

    profit = round(revenue - costs, 2)
    profit_perc = round((profit / revenue) * 100, 1) if revenue else 0.0

    return {
        "revenue": revenue,
        "costs": costs,
        "profit": profit,
        "profit_perc": profit_perc,
    }
    # TODO (typing): Jeśli zostajesz przy Decimal, zmień adnotację zwrotu na Dict[str, Decimal] (lub Union dla profit_perc).
    # TODO (maint): Rozważ wydzielenie "sanity checks" w formie: min_value=0 dla kosztów/cen/dni pracy itd.
