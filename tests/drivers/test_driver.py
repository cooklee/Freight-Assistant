import pytest
from django.shortcuts import reverse

from apps.drivers.models import Driver


def valid_driver_data(**kwargs):
    data = {
        'first_name': 'test_driver_name',
        'last_name': 'test_driver_surname',
        'email': 'test_driver@email.com',
        'phone': '123456789',
    }
    data.update(kwargs)
    return data


@pytest.mark.django_db
def test_driver_list_view(client, user, driver):
    client.force_login(user)
    response = client.get(reverse('driver-list'))
    assert response.status_code == 200
    assert 'drivers' in response.context
    assert driver in response.context['drivers']


@pytest.mark.django_db
def test_driver_add_view_get(client, user, carrier):
    client.force_login(user)
    response = client.get(reverse('driver-add', args=[carrier.id]))
    assert response.status_code == 200
    assert 'form' in response.context


@pytest.mark.django_db
def test_driver_add_view_post(client, user, carrier):
    client.force_login(user)
    data = valid_driver_data()
    response = client.post(reverse('driver-add', args=[carrier.id]), data)
    assert response.status_code == 302
    assert Driver.objects.get(first_name=data['first_name'])


@pytest.mark.django_db
def test_driver_add_view_post_invalid(client, user, carrier):
    client.force_login(user)
    data = valid_driver_data(first_name='', phone='a')
    response = client.post(reverse('driver-add', args=[carrier.id]), data)
    form_errors = response.context['form'].errors
    assert response.status_code == 200
    assert 'first_name' in form_errors
    assert 'Phone must contain digits only.' in form_errors['phone']


@pytest.mark.django_db
def test_driver_detail_view(client, user, driver):
    client.force_login(user)
    response = client.get(reverse('driver-detail', args=[driver.id]))
    assert response.status_code == 200
    assert 'driver' in response.context
    assert response.context['driver'] == driver


@pytest.mark.django_db
def test_driver_update_view_get(client, user, driver):
    client.force_login(user)
    response = client.get(reverse('driver-update', args=[driver.id]))
    assert response.status_code == 200
    assert 'form' in response.context
    assert response.context['form'].instance == driver


@pytest.mark.django_db
def test_driver_update_view_post(client, user, driver):
    client.force_login(user)
    data = valid_driver_data(first_name='Updated')
    response = client.post(reverse('driver-update', args=[driver.id]), data)
    assert response.status_code == 302
    driver.refresh_from_db()
    assert driver.first_name == 'Updated'


@pytest.mark.django_db
def test_driver_update_view_post_bad_data(client, user, driver):
    client.force_login(user)
    data = valid_driver_data(first_name='', phone='a')
    response = client.post(reverse('driver-update', args=[driver.id]), data)
    form_errors = response.context['form'].errors
    assert response.status_code == 200
    assert 'first_name' in form_errors
    assert 'Phone must contain digits only.' in form_errors['phone']


@pytest.mark.django_db
def test_driver_delete_view_get(client, user, driver):
    client.force_login(user)
    response = client.get(reverse('driver-delete', args=[driver.id]))
    assert response.status_code == 200
    assert 'driver' in response.context


@pytest.mark.django_db
def test_driver_delete_view_post(client, user, driver):
    client.force_login(user)
    response = client.post(reverse('driver-delete', args=[driver.id]))
    assert response.status_code == 302
    assert not Driver.objects.filter(id=driver.id).exists()
