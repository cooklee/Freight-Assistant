import pytest
from django.urls import reverse

from apps.transport.models import Route, Stop


@pytest.mark.django_db
def test_route_str_and_total_stops(user):
    route = Route.objects.create(user=user, name="test")
    Stop.objects.create(route=route, location='A', stop_type="START_FROM_BASE", stop_number='1')
    Stop.objects.create(route=route, location='B', stop_type="FINAL_STOP", stop_number='2')
    assert str(route) == 'test'
    assert route.total_stops == 2


@pytest.mark.django_db
def test_route_list_view(client, user):
    client.force_login(user)
    response = client.get(reverse('route-list'))
    assert response.status_code == 200
    assert 'routes' in response.context


@pytest.mark.django_db
def test_route_create_get(client, user):
    client.force_login(user)
    response = client.get(reverse('route-create'))
    assert response.status_code == 200
    assert response.context['form']


@pytest.mark.django_db
def test_route_create_view_post(client, user):
    client.force_login(user)
    data = {'name': 'Test Route'}
    response = client.post(reverse('route-create'), data)
    assert response.status_code == 302
    assert Route.objects.filter(name='Test Route', user=user).exists()


@pytest.mark.django_db
def test_route_create_view_post_bad_data(client, user):
    client.force_login(user)
    data = {'name': ''}
    response = client.post(reverse('route-create'), data)
    assert response.status_code == 200
    assert response.context['form'].errors['name']


@pytest.mark.django_db
def test_route_detail_view(client, user, route, stop):
    client.force_login(user)
    response = client.get(reverse('route-detail', args=[route.id]))
    assert response.status_code == 200
    assert response.context['route'] == route
    assert response.context['stops']


@pytest.mark.django_db
def test_route_update_view_get(client, user, route):
    client.force_login(user)
    response = client.get(reverse('route-update', args=[route.id]), {'name': 'updated_route'})
    assert response.status_code == 200
    assert response.context['route'] == route


@pytest.mark.django_db
def test_route_update_view_post(client, user, route):
    client.force_login(user)
    response = client.post(reverse('route-update', args=[route.id]), {'name': 'updated_route'})
    assert response.status_code == 302
    route.refresh_from_db()
    assert route.name == 'updated_route'


@pytest.mark.django_db
def test_route_update_view_post_bad_data(client, user, route):
    client.force_login(user)
    response = client.post(reverse('route-update', args=[route.id]), {'name': ''})
    assert response.status_code == 200
    assert response.context['form'].errors['name']


@pytest.mark.django_db
def test_route_delete_view_post_get(client, user, route):
    client.force_login(user)
    response = client.get(reverse('route-delete', args=[route.id]))
    assert response.status_code == 200
    assert response.context['route'] == route


@pytest.mark.django_db
def test_route_delete_view_post(client, user, route):
    client.force_login(user)
    response = client.post(reverse('route-delete', args=[route.id]))
    assert response.status_code == 302
    assert not Route.objects.filter(id=route.id).exists()


@pytest.mark.django_db
def test_route_with_stops_create_view_get(client, user):
    client.force_login(user)
    response = client.get(reverse('route-with-stops'))
    assert response.status_code == 200
    assert response.context['form']
    assert response.context['formset']
    assert response.context['GOOGLE_MAPS_API_KEY']


@pytest.mark.django_db
def test_route_with_stops_create_view_post(client, user):
    client.force_login(user)

    route_data = {
        'name': 'Combined Route'
    }

    formset_data = {
        'stops-TOTAL_FORMS': '2',
        'stops-INITIAL_FORMS': '0',
        'stops-MIN_NUM_FORMS': '0',
        'stops-MAX_NUM_FORMS': '1000',
        'stops-0-location': 'Berlin',
        'stops-0-stop_number': '1',
        'stops-0-stop_type': 'START_FROM_BASE',
        'stops-1-location': 'Warsaw',
        'stops-1-stop_number': '2',
        'stops-1-stop_type': 'FINAL_STOP',
    }

    post_data = {
        **route_data,
        **formset_data
    }

    response = client.post(reverse('route-with-stops'), data=post_data)

    assert response.status_code == 302

    route = Route.objects.get(name='Combined Route')
    stops = route.stops.order_by('stop_number')

    assert route.user == user
    assert stops.count() == 2
    assert stops[0].location == 'Berlin'
    assert stops[1].location == 'Warsaw'


@pytest.mark.django_db
def test_route_with_stops_create_view_post_bad_data(client, user):
    client.force_login(user)

    route_data = {
        'name': ''
    }

    formset_data = {
        'stops-TOTAL_FORMS': '2',
        'stops-INITIAL_FORMS': '0',
        'stops-MIN_NUM_FORMS': '0',
        'stops-MAX_NUM_FORMS': '1000',
        'stops-0-location': '',
        'stops-0-stop_number': '',
        'stops-0-stop_type': '',
        'stops-1-location': '',
        'stops-1-stop_number': '',
        'stops-1-stop_type': '',
    }

    post_data = {
        **route_data,
        **formset_data
    }

    response = client.post(reverse('route-with-stops'), data=post_data)
    assert response.status_code == 200
    assert response.context['form'].errors['name']
    assert response.context['formset'].errors
