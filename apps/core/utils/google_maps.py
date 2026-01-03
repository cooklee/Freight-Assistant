import requests
from django.conf import settings


def get_distance_duration(origin: str, destination: str):
    base_url = "https://maps.googleapis.com/maps/api/distancematrix/json"
    params = {
        "origins": origin,
        "destinations": destination,
        "key": settings.GOOGLE_MAPS_API_KEY,
        "units": "metric",
    }

    try:
        resp = requests.get(base_url, params=params, timeout=10)
        resp.raise_for_status()
        data = resp.json()
    except (requests.RequestException, ValueError):
        return None, None

    if data.get("status") != "OK":
        return None, None

    try:
        element = data["rows"][0]["elements"][0]
        if element.get("status") != "OK":
            return None, None

        distance_m = element["distance"]["value"]
        duration_s = element["duration"]["value"]
        return distance_m / 1000.0, int(duration_s / 60)
    except (KeyError, IndexError, TypeError):
        return None, None
