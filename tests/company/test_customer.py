import pytest
from django.shortcuts import reverse

from apps.company.models import Customer


def valid_customer_data(**kwargs):
    data = {
        'name': 'test_customer',
        'nip': '1234567890',
        'address': 'test_address',
        'email': 'test_email@mail.com',
        'phone': '123456789',
    }
    data.update(kwargs)
    return data


@pytest.mark.django_db
def test_customer_list_view(client, user, customer_list):
    client.force_login(user)
    response = client.get(reverse('customer-list'))
    assert response.status_code == 200
    for customer_obj in customer_list:
        assert customer_obj in response.context['customers']


@pytest.mark.django_db
def test_customer_add_view_get(client, user):
    client.force_login(user)
    response = client.get(reverse('customer-add'))
    assert response.status_code == 200
    assert 'form' in response.context


@pytest.mark.django_db
def test_customer_add_view_post(client, user):
    client.force_login(user)
    data = valid_customer_data()
    response = client.post(reverse('customer-add'), data)
    assert response.status_code == 302
    assert Customer.objects.filter(name=data['name']).exists()


@pytest.mark.django_db
def test_customer_detail_view(client, user, customer):
    client.force_login(user)
    response = client.get(reverse('customer-detail', args=[customer.id]))
    assert response.status_code == 200
    assert response.context['customer'] == customer


@pytest.mark.django_db
def test_customer_update_view_get(client, user, customer):
    client.force_login(user)
    url = reverse('customer-update', args=[customer.id])
    response = client.get(url)
    assert response.status_code == 200
    assert response.context['form'].instance == customer


@pytest.mark.django_db
def test_customer_update_view_post(client, user, customer):
    client.force_login(user)
    url = reverse('customer-update', args=[customer.id])
    response = client.post(url, valid_customer_data())
    assert response.status_code == 302
    customer.refresh_from_db()
    for key, value in valid_customer_data().items():
        assert getattr(customer, key) == value


@pytest.mark.django_db
def test_customer_delete_view_get(client, user, customer):
    client.force_login(user)
    url = reverse('customer-delete', args=[customer.id])
    response = client.get(url)
    assert response.status_code == 200
    assert response.context['customer'] == customer


@pytest.mark.django_db
def test_customer_update_view_post_bad_data(client, user, customer):
    bad_data = valid_customer_data(
        name='',
        nip='a',
        address='',
        email='',
        phone='a',
    )
    client.force_login(user)
    url = reverse('customer-update', args=[customer.id])
    response = client.post(url, bad_data)
    assert response.status_code == 200
    error_list = response.context['form'].errors
    assert 'This field is required.' in error_list['name']
    assert 'NIP must contain digits only.' in error_list['nip']
    assert 'Phone must contain digits only.' in error_list['phone']


@pytest.mark.django_db
def test_customer_update_view_post_bad_nip_length(client, user, customer):
    bad_data = valid_customer_data(
        nip='123',
    )
    client.force_login(user)
    url = reverse('customer-update', args=[customer.id])
    response = client.post(url, bad_data)
    assert response.status_code == 200
    error_list = response.context['form'].errors
    assert 'NIP must be exactly 10 digits.' in error_list['nip']


@pytest.mark.django_db
def test_customer_delete_view_post(client, user, customer):
    client.force_login(user)
    url = reverse('customer-delete', args=[customer.id])
    response = client.post(url)
    assert response.status_code == 302
    assert not Customer.objects.filter(id=customer.id).exists()
