import pytest
from django.shortcuts import reverse

from apps.company.models import Carrier


def valid_carrier_data(**kwargs):
    data = {
        'name': 'test_carrier',
        'nip': '1112223334',
        'address': 'test_address',
        'email': 'test_email@mail.com',
        'phone': '111222333',
    }
    data.update(kwargs)
    return data


@pytest.mark.django_db
def test_carrier_list_view(client, user, carrier_list):
    client.force_login(user)
    response = client.get(reverse('carrier-list'))
    assert response.status_code == 200
    for carrier_obj in carrier_list:
        assert carrier_obj in response.context['carriers']


@pytest.mark.django_db
def test_carrier_add_view_get(client, user):
    client.force_login(user)
    response = client.get(reverse('carrier-add'))
    assert response.status_code == 200
    assert response.context['form']


@pytest.mark.django_db
def test_carrier_add_view_post(client, user):
    client.force_login(user)
    response = client.post(reverse('carrier-add'), valid_carrier_data())
    assert response.status_code == 302
    assert Carrier.objects.get(name=valid_carrier_data()['name'])


@pytest.mark.django_db
def test_carrier_detail_view_get(client, user, carrier):
    client.force_login(user)
    url = reverse('carrier-detail', args=[carrier.id])
    response = client.get(url)
    assert response.status_code == 200
    assert 'carrier' in response.context
    assert carrier == response.context['carrier']
    assert 'drivers' in response.context


@pytest.mark.django_db
def test_carrier_update_view_get(client, user, carrier):
    client.force_login(user)
    url = reverse('carrier-update', args=[carrier.id])
    response = client.get(url)
    assert response.status_code == 200
    form = response.context['form']
    assert form.instance == carrier
    for field in ['name', 'nip', 'address', 'email', 'phone']:
        assert form.initial[field] == getattr(carrier, field)


@pytest.mark.django_db
def test_carrier_update_view_post(client, user, carrier):
    client.force_login(user)
    url = reverse('carrier-update', args=[carrier.id])
    response = client.post(url, valid_carrier_data())
    assert response.status_code == 302
    carrier.refresh_from_db()
    for key, value in valid_carrier_data().items():
        assert getattr(carrier, key) == value


@pytest.mark.django_db
def test_carrier_update_view_post_bad_data(client, user, carrier):
    bad_data = valid_carrier_data(
        name='',
        nip='a',
        address='',
        email='',
        phone='a',
    )
    client.force_login(user)
    url = reverse('carrier-update', args=[carrier.id])
    response = client.post(url, bad_data)
    assert response.status_code == 200
    error_list = response.context['form'].errors
    print(error_list)
    assert 'This field is required.' in error_list['name']
    assert 'NIP must contain digits only.' in error_list['nip']
    assert 'Phone must contain digits only.' in error_list['phone']


@pytest.mark.django_db
def test_carrier_update_view_post_bad_nip_length(client, user, carrier):
    bad_data = valid_carrier_data(
        nip='123',
    )
    client.force_login(user)
    url = reverse('carrier-update', args=[carrier.id])
    response = client.post(url, bad_data)
    assert response.status_code == 200
    error_list = response.context['form'].errors
    assert 'NIP must be exactly 10 digits.' in error_list['nip']


@pytest.mark.django_db
def test_carrier_delete_view_get(client, user, carrier):
    client.force_login(user)
    url = reverse('carrier-delete', args=[carrier.id])
    response = client.get(url)
    assert response.status_code == 200
    assert 'carrier' in response.context
    assert carrier == response.context['carrier']


@pytest.mark.django_db
def test_carrier_delete_view_post(client, user, carrier):
    client.force_login(user)
    url = reverse('carrier-delete', args=[carrier.id])
    response = client.post(url)
    assert response.status_code == 302
    assert not Carrier.objects.filter(id=carrier.id).exists()
