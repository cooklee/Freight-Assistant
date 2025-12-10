import requests
from django.conf import settings


def get_distance_duration(origin, destination):
    base_url = 'https://maps.googleapis.com/maps/api/distancematrix/json'
    params = {
        'origins': origin,
        'destinations': destination,
        'key': settings.GOOGLE_MAPS_API_KEY,
        'units': 'metric',
    }
    response = requests.get(base_url, params=params)
    data = response.json()

    try:
        element = data['rows'][0]['elements'][0]
        distance = element['distance']['value']  # in meters
        duration = element['duration']['value']  # in seconds
        return distance / 1000, duration / 60  # km, minutes
    except (KeyError, IndexError):
        return None, None

