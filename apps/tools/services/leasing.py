from decimal import Decimal
from typing import Dict, Any


def calculate_leasing(cleaned_data: Dict[str, Any]) -> Dict[str, Decimal]:
    vehicle_price = cleaned_data["vehicle_price"]
    initial_fee = cleaned_data["initial_fee"]
    vehicle_registration_fee = cleaned_data["vehicle_registration_fee"]
    domestic_transport_license = cleaned_data["domestic_transport_license"]
    leasing_installment = cleaned_data["leasing_installment"]
    insurance = cleaned_data["insurance"]

    leasing_administration_fee = cleaned_data.get("leasing_administration_fee") or 0
    eu_community_license = cleaned_data.get("eu_community_license") or 0
    gap_insurance = cleaned_data.get("gap_insurance") or 0
    security_installment = cleaned_data.get("security_installment") or 0

    initial_cost_base = (
        vehicle_price * (initial_fee / 100)
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

    return {
        "total_initial_payment": total_initial_payment,
        "monthly_cost": monthly_cost_base,
    }
