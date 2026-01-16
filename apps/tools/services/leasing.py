from decimal import Decimal
from typing import Dict, Any


def calculate_leasing(cleaned_data: Dict[str, Any]) -> Dict[str, Decimal]:
    vehicle_price = cleaned_data["vehicle_price"]
    # TODO (bug): Jeśli cleaned_data pochodzi z forms, upewnij się, że to Decimal (a nie float/int/str).
    #   Mieszanie floatów z Decimal daje problemy z precyzją. Najlepiej trzymaj wszystko jako Decimal.

    initial_fee = cleaned_data["initial_fee"]
    # TODO (clarity): initial_fee wygląda na % (0-100). Rozważ walidację zakresu w formie.
    # TODO (clarity): Dla czytelności nazwij to np. initial_fee_percent.

    vehicle_registration_fee = cleaned_data["vehicle_registration_fee"]
    domestic_transport_license = cleaned_data["domestic_transport_license"]
    leasing_installment = cleaned_data["leasing_installment"]
    insurance = cleaned_data["insurance"]

    leasing_administration_fee = cleaned_data.get("leasing_administration_fee") or 0
    eu_community_license = cleaned_data.get("eu_community_license") or 0
    gap_insurance = cleaned_data.get("gap_insurance") or 0
    security_installment = cleaned_data.get("security_installment") or 0
    # TODO (bug): Te "or 0" wprowadza int 0. Lepiej użyć Decimal("0") żeby nie mieszać typów z Decimal.
    # TODO (bug): Jeśli któreś pole może być Decimal('0.00'), to "or 0" nadal zwróci 0 (int) — typowo nie szkodzi
    # TODO (bug): w sumowaniu, ale to słaby nawyk i może wyjść w bardziej złożonych obliczeniach/typowaniu.

    initial_cost_base = (
        vehicle_price * (initial_fee / 100)
        # TODO (bug): initial_fee / 100 może dać float/int zależnie od typów. Najbezpieczniej:
        # TODO (bug): vehicle_price * (initial_fee / Decimal("100"))
        # TODO (clarity): albo: vehicle_price * (initial_fee_percent / Decimal("100"))

        + vehicle_registration_fee
        + domestic_transport_license
        + leasing_administration_fee
        + eu_community_license
    )

    monthly_cost_base = (
        leasing_installment
        + insurance
        + gap_insurance
        + security_installment
    )

    total_initial_payment = initial_cost_base + monthly_cost_base

    # TODO (finance): Rozważ zaokrąglanie (quantize) do 2 miejsc po przecinku, jeśli to kwoty pieniężne:
    # TODO (finance): total_initial_payment = total_initial_payment.quantize(Decimal("0.01"))

    return {
        "total_initial_payment": total_initial_payment,
        "monthly_cost": monthly_cost_base,
    }
    # TODO (clarity): Nazwa monthly_cost_base vs zwracane "monthly_cost" jest OK, ale możesz uprościć
    # TODO (clarity): (monthly_cost = monthly_cost_base) dla spójności nazewnictwa.
