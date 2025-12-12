import pytest
from django.shortcuts import reverse


def valid_profile_data(**kwargs):
    data = {
        'about_me': 'lorem ipsum dolor sit amet',
        'job': 'test_job',
        'country': 'test_country',
        'address': 'test_address',
        'phone': '111222333',
        'twitter': 'test_twitter.com',
        'facebook': 'test_facebook.com',
        'instagram': 'test_instagram.com',
        'linkedin': 'test_linkedin.com',
    }
    data.update(kwargs)
    return data


@pytest.mark.django_db
def test_userprofile_str(user, profile):
    assert str(profile) == f"{user.username} Profile"


@pytest.mark.django_db
def test_profile_get(client, user, profile):
    returned_data = ['form', 'profile', 'password_form']
    client.force_login(user)
    response = client.get(reverse('profile'))
    data = profile
    print(data.about_me)
    print(response.context['form'])
    assert response.status_code == 200
    for data in returned_data:
        assert data in response.context
    form = response.context['form']
    for key, value in valid_profile_data().items():
        assert form.initial[key] == value


@pytest.mark.django_db
def test_profile_update(client, user, profile):
    client.force_login(user)
    updated_data = valid_profile_data(
        first_name='test_first_name',
        last_name='test_last_name',
        about_me='new',
        job='new',
        country='new',
        address='new',
        phone='333222111',
        twitter='http://new.com',
        facebook='http://new.com',
        instagram='http://new.com',
        linkedin='http://new.com',
    )
    response = client.post(reverse('profile'), data=updated_data)
    assert response.status_code == 302
    profile.refresh_from_db()
    for key, value in updated_data.items():
        if key not in ('first_name', 'last_name'):
            assert getattr(profile, key) == value
    user.refresh_from_db()
    assert user.first_name == 'test_first_name'
    assert user.last_name == 'test_last_name'


@pytest.mark.django_db
def test_password_change(client, user, profile):
    client.force_login(user)
    response = client.post(reverse('profile'), data={
        'old_password': 'testpassword',
        'new_password': 'newpass123',
        'new_password_2': 'newpass123',
    })
    assert response.status_code == 302
    # print(response.context['form'].errors)
    # print(response.context['password_form'].errors)
    user.refresh_from_db()
    assert user.check_password('newpass123')


@pytest.mark.django_db
def test_password_change_mismatch(client, user, profile):
    client.force_login(user)
    response = client.post(reverse('profile'), data={
        'old_password': 'testpassword',
        'new_password': 'wrong',
        'new_password_2': 'data',
    })
    assert response.status_code == 200
    assert 'New passwords do not match.' in response.context['password_form'].errors['__all__']


@pytest.mark.django_db
def test_password_change_invalid_old_password(client, user, profile):
    client.force_login(user)
    response = client.post(reverse('profile'), data={
        'old_password': 'wrong-password',
        'new_password': 'good-data',
        'new_password_2': 'good-data',
    })
    assert response.status_code == 200
    assert 'Old password is incorrect.' in response.context['password_form'].errors['old_password']
