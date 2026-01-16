from django.http import JsonResponse

from apps.drivers.models import Driver


def drivers_by_carrier(request, carrier_id):
    qs = Driver.objects.filter(carrier_id=carrier_id).order_by("first_name")
    # TODO (security): Ten endpoint nie ma żadnej kontroli dostępu. Jeśli to aplikacja za loginem,
    # TODO (security): dodaj @login_required albo sprawdzaj request.user (np. czy ma dostęp do tego carrier).
    # TODO (validation): carrier_id przychodzi z URL jako string/int — jeśli masz niestandardowe wartości,
    # TODO (validation): rozważ walidację/cast i obsługę błędów.

    data = [
        {"id": d.id, "name": f"{d.first_name} {d.last_name}"}
        for d in qs
    ]
    # TODO (perf): Jeśli lista jest duża, rozważ limit/paginację lub przynajmniej .values("id","first_name","last_name")
    # TODO (perf): żeby nie tworzyć pełnych obiektów modelu.

    return JsonResponse({"drivers": data})
    # TODO (http): Jeśli ten endpoint ma być używany tylko przez GET, rozważ sprawdzenie request.method
    # TODO (http): lub dekorator require_GET.