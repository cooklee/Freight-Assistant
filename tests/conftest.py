import pytest
from django.contrib.auth.models import User
from django.test import Client

from apps.company.models import Carrier, Customer, CustomerBranch
from apps.drivers.models import Driver
from apps.messaging.models import Conversation, Message
from apps.transport.models import Route, Stop


@pytest.fixture
def client():
    return Client()


@pytest.fixture
def user_list():
    users_list = []
    for i in range(1, 5):
        user = User(
            username=f"test_username{i}",
            email=f"test{i}@mail.com",
        )
        user.set_password(f"testpassword{i}")
        user.save()
        users_list.append(user)
    return users_list


@pytest.fixture
def user(user_list):
    return User.objects.first()


@pytest.fixture
def user_2(user_list):
    return User.objects.last()


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
            for i in range(1, 3)
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
            for i in range(1, 3)
        ]
        all_drivers.extend(carrier_drivers)
    Driver.objects.bulk_create(all_drivers)
    return Driver.objects.all()


@pytest.fixture
def driver(driver_list):
    return Driver.objects.first()


@pytest.fixture
def conversation(user, user_2):
    return Conversation.objects.create(user1=user, user2=user_2, subject="Hello")


@pytest.fixture
def message(conversation, user):
    return Message.objects.create(conversation=conversation, sender=user, text='Initial msg')


@pytest.fixture
def route(user):
    return Route.objects.create(name='test_route', user=user)

@pytest.fixture
def stop(route):
    return Stop.objects.create(
        route=route,
        stop_number=1,
        stop_type='START_FROM_BASE',
        location='initial',
        )