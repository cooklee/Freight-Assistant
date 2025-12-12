import pytest
from django.shortcuts import reverse
from apps.company.models import Customer, CustomerBranch



def valid_branch_data():
    return {
        'name': 'test_branch',
        'address': 'test_address',
    }


@pytest.mark.django_db
def test_branch_list_view(client, user, branch_list):
    client.force_login(user)
    response = client.get(reverse('branch-list'))
    assert response.status_code == 200
    for branch in branch_list:
        assert branch in response.context['branches']


@pytest.mark.django_db
def test_branch_add_view_get(client, user, customer):
    client.force_login(user)
    response = client.get(reverse('branch-add', args=[customer.id]))
    assert response.status_code == 200
    assert 'form' in response.context


@pytest.mark.django_db
def test_branch_add_view_post(client, user, customer):
    client.force_login(user)
    response = client.post(reverse('branch-add', args=[customer.id]), valid_branch_data())
    assert response.status_code == 302
    assert CustomerBranch.objects.filter(name='test_branch', customer=customer).exists()


@pytest.mark.django_db
def test_branch_add_view_post_invalid(client, user, customer):
    client.force_login(user)
    response = client.post(reverse('branch-add', args=[customer.id]), data={'name': '', 'address': ''})
    assert response.status_code == 200
    assert response.context['form'].errors
    assert CustomerBranch.objects.count() == 0


@pytest.mark.django_db
def test_branch_detail_view(client, user, branch):
    client.force_login(user)
    response = client.get(reverse('branch-detail', args=[branch.id]))
    assert response.status_code == 200
    assert response.context['branch'] == branch


@pytest.mark.django_db
def test_branch_update_view_get(client, user, branch):
    client.force_login(user)
    response = client.get(reverse('branch-update', args=[branch.id]))
    assert response.status_code == 200
    assert response.context['form'].instance == branch


@pytest.mark.django_db
def test_branch_update_view_post(client, user, branch):
    client.force_login(user)
    data = {'name': 'Updated Branch', 'address': 'Updated Address'}
    response = client.post(reverse('branch-update', args=[branch.id]), data=data)
    assert response.status_code == 302
    branch.refresh_from_db()
    assert branch.name == 'Updated Branch'


@pytest.mark.django_db
def test_branch_update_view_post_invalid(client, user, branch):
    client.force_login(user)
    response = client.post(reverse('branch-update', args=[branch.id]), data={'name': '', 'address': ''})
    assert response.status_code == 200
    assert response.context['form'].errors


@pytest.mark.django_db
def test_branch_delete_view_get(client, user, branch):
    client.force_login(user)
    response = client.get(reverse('branch-delete', args=[branch.id]))
    assert response.status_code == 200
    assert response.context['branch'] == branch


@pytest.mark.django_db
def test_branch_delete_view_post(client, user, branch):
    client.force_login(user)
    response = client.post(reverse('branch-delete', args=[branch.id]))
    assert response.status_code == 302
    assert not CustomerBranch.objects.filter(id=branch.id).exists()
