from django.http import JsonResponse

from apps.drivers.models import Driver


def drivers_by_carrier(request, carrier_id):
    qs = Driver.objects.filter(carrier_id=carrier_id).order_by("first_name")
    data = [
        {"id": d.id, "name": f"{d.first_name} {d.last_name}"}
        for d in qs
    ]
    return JsonResponse({"drivers": data})
