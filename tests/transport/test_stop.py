import pytest
from django.urls import reverse

from apps.transport.models import Stop


@pytest.mark.django_db
def test_stop_create_view_get(client, user, route):
    client.force_login(user)
    response = client.get(reverse('stop-add', args=[route.id]))
    assert response.status_code == 200
    assert response.context['form']
    assert response.context['route']
    assert response.context['GOOGLE_MAPS_API_KEY']


@pytest.mark.django_db
def test_stop_create_view_post(client, user, route):
    client.force_login(user)
    data = {
        'location': 'Paris',
        'stop_number': 1,
        'stop_type': 'START_FROM_BASE',
    }
    response = client.post(reverse('stop-add', args=[route.id]), data)
    assert response.status_code == 302
    assert Stop.objects.filter(route=route, location='Paris').exists()


@pytest.mark.django_db
def test_stop_create_view_post_bad_data(client, user, route):
    client.force_login(user)
    data = {
        'location': '',
        'stop_number': '',
        'stop_type': '',
    }
    response = client.post(reverse('stop-add', args=[route.id]), data)
    assert response.status_code == 200
    assert response.context['form']['location']
    assert response.context['form']['stop_number']
    assert response.context['form']['stop_type']


@pytest.mark.django_db
def test_stop_update_view_get(client, user, stop):
    client.force_login(user)
    response = client.get(reverse('stop-update', args=[stop.id]))
    assert response.status_code == 200
    assert response.context['form']
    assert response.context['form'].instance == stop
    assert response.context['GOOGLE_MAPS_API_KEY']


@pytest.mark.django_db
def test_stop_update_view_post(client, user, stop):
    client.force_login(user)
    response = client.post(reverse('stop-update', args=[stop.id]), {
        'location': 'Berlin',
        'stop_number': stop.stop_number,
        'stop_type': stop.stop_type
    })
    assert response.status_code == 302
    stop.refresh_from_db()
    assert stop.location == 'Berlin'


@pytest.mark.django_db
def test_stop_update_view_post_bad_data(client, user, stop):
    client.force_login(user)
    response = client.post(reverse('stop-update', args=[stop.id]), {
        'location': '',
        'stop_number': '',
        'stop_type': ','
    })
    assert response.status_code == 200
    assert response.context['form']['location']
    assert response.context['form']['stop_number']
    assert response.context['form']['stop_type']


@pytest.mark.django_db
def test_stop_delete_view_get(client, user, stop):
    client.force_login(user)
    response = client.get(reverse('stop-delete', args=[stop.id]))
    assert response.status_code == 200
    assert response.context['stop'] == stop


@pytest.mark.django_db
def test_stop_delete_view_post(client, user, stop):
    client.force_login(user)
    response = client.post(reverse('stop-delete', args=[stop.id]))
    assert response.status_code == 302
    assert not Stop.objects.filter(id=stop.id).exists()
