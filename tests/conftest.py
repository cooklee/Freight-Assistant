import pytest
from django.contrib.auth.models import User
from django.test import Client

from apps.company.models import Carrier, Customer, CustomerBranch
from apps.drivers.models import Driver


@pytest.fixture
def client():
    return Client()


@pytest.fixture
def user():
    user = User.objects.create_user(
        username="test",
        email="test@mail.com",
    )
    user.set_password("testpassword")
    user.save()
    return user


@pytest.fixture
def profile(user):
    profile = user.profile

    profile.about_me = 'lorem ipsum dolor sit amet'
    profile.job = 'test_job'
    profile.country = 'test_country'
    profile.address = 'test_address'
    profile.phone = '111222333'
    profile.twitter = 'test_twitter.com'
    profile.facebook = 'test_facebook.com'
    profile.instagram = 'test_instagram.com'
    profile.linkedin = 'test_linkedin.com'
    profile.save()

    return profile


@pytest.fixture
def carrier_list():
    carriers = [
        Carrier(
            name=f"test_carrier{i}",
            nip=f"123456789{i}",
            address=f"test_carrier_address{i}",
            email=f"test_carrier{i}@mail.com",
            phone=f"12345678{i}",
        )
        for i in range(1, 6)
    ]
    Carrier.objects.bulk_create(carriers)
    return carriers


@pytest.fixture
def carrier(carrier_list):
    return carrier_list[0]


@pytest.fixture
def customer_list():
    customers = [
        Customer(
            name=f"test_customer{i}",
            nip=f"123456789{i}",
            address=f"test_customer_address{i}",
            email=f"test_customer{i}@mail.com",
            phone=f"12345678{i}",
        )
        for i in range(1, 6)
    ]
    Customer.objects.bulk_create(customers)
    return customers


@pytest.fixture
def customer(customer_list):
    return customer_list[0]

@pytest.fixture
def branch_list(customer_list):
    all_branches = []
    for customer in customer_list:
        customer_branches = [
             CustomerBranch(
                customer=customer,
                name=f"{customer.name} Test Branch {i}",
                address=f"Test Branch Address{i}"
            )
        for i in range(1,3)
        ]
        all_branches.extend(customer_branches)
    CustomerBranch.objects.bulk_create(all_branches)
    return CustomerBranch.objects.all()

@pytest.fixture
def branch(branch_list):
    return CustomerBranch.objects.first()

@pytest.fixture
def driver_list(carrier_list):
    all_drivers = []
    for carrier in carrier_list:
        carrier_drivers = [
            Driver(
                carrier=carrier,
                first_name=f"test_driver_name{i} - {carrier.name}",
                last_name=f"test_driver_surname{i} - {carrier.name}",
                phone=f"12345678{i}"
            )
            for i in range(1,3)
        ]
        all_drivers.extend(carrier_drivers)
    Driver.objects.bulk_create(all_drivers)
    return Driver.objects.all()

@pytest.fixture
def driver(driver_list):
    return Driver.objects.first()



