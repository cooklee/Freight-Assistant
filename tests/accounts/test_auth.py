import pytest
from django.contrib.auth import get_user_model
from django.shortcuts import reverse

User = get_user_model()


def valid_registration_data(**overrides):
    data = {
        'username': 'test',
        'first_name': 'test_name',
        'last_name': 'test_last_name',
        'email': 'test_email@mal.com',
        'password': 'secret',
        'password2': 'secret',
    }
    data.update(overrides)
    return data


@pytest.mark.django_db
def test_login_get(client):
    response = client.get(reverse("login"))
    assert response.status_code == 200
    assert response.context['form']


@pytest.mark.django_db
def test_login_success(client, user):
    response = client.post(reverse('login'), {
        'username': user.username,
        'password': 'testpassword1',
    })
    # print(response.context['form'].errors)
    assert response.status_code == 302
    assert '_auth_user_id' in client.session


@pytest.mark.django_db
def test_login_post_fail(client, user):
    response = client.post(reverse('login'), {
        'username': 'wrong',
        'password': 'data',
    })
    # print(response.context['form'].errors)
    assert response.status_code == 200
    assert '__all__' in response.context['form'].errors


@pytest.mark.django_db
def test_logout_get(client):
    response = client.get(reverse("logout"))
    assert response.status_code == 302
    assert '_auth_user_id' not in client.session


@pytest.mark.django_db
def test_register_get(client):
    response = client.get(reverse("register"))
    assert response.status_code == 200
    assert response.context['form']


@pytest.mark.django_db
def test_register_success(client):
    response = client.post(reverse('register'), valid_registration_data())
    assert response.status_code == 302
    assert '_auth_user_id' in client.session
    assert User.objects.get(username=valid_registration_data()['username']).first_name == 'test_name'


@pytest.mark.django_db
def test_register_fail(client, user):
    response = client.post(reverse('register'), valid_registration_data(
        first_name='',
        last_name='',
        email='wrongmail',
        password='password',
        password2='wrong',
    ))
    print(response.context['form'].errors)
    assert response.status_code == 200
    assert '__all__' in response.context['form'].errors
    assert "Passwords don't match." in response.context['form'].errors["__all__"]
    assert "Enter a valid email address." in response.context['form'].errors['email']


@pytest.mark.django_db
def test_register_username_taken(client, user):
    response = client.post(reverse('register'), valid_registration_data(username=user.username))
    print(response.context['form'].errors)
    assert response.status_code == 200
    assert 'User with this username already exists.' in response.context['form'].errors['__all__']
