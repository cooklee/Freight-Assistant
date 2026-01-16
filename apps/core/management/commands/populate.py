import os
import random
from datetime import date, timedelta
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from faker import Faker

from apps.company.models import Carrier
from apps.company.models import Customer, CustomerBranch
from apps.drivers.models import Driver
from apps.messaging.models import Conversation, Message
from apps.transport.models import Route, Calculation
from apps.transport.models import Stop, STOP_TYPE_CHOICES
from apps.transport.models import TransportOrder
from apps.transport.services.calculation_service import apply_schedule

fake = Faker("pl_PL")
User = get_user_model()


class Command(BaseCommand):
    help = "Populates the database with development data."

    # MAIN ENTRY

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING("Resetting data..."))
        self._reset_data()

        self.stdout.write(self.style.WARNING("Creating test user and random users..."))
        test_user = self._create_test_user()
        users = [test_user] + self._create_random_users(10)

        self.stdout.write(self.style.WARNING("Creating customers + branches..."))
        customers = self._create_customers()

        self.stdout.write(self.style.WARNING("Creating carriers..."))
        carriers = self._create_carriers()

        self.stdout.write(self.style.WARNING("Creating drivers..."))
        drivers = self._create_drivers(carriers)

        self.stdout.write(self.style.WARNING("Creating routes + stops..."))
        routes = []
        for u in users:
            routes.extend(self._create_routes(u, count=3))

        self.stdout.write(self.style.WARNING("Creating transport orders..."))
        self._create_transport_orders(customers, carriers, drivers, routes)

        self.stdout.write(self.style.WARNING("Creating calculations..."))
        self._create_calculations(routes, carriers, drivers, test_user)

        self.stdout.write(self.style.WARNING("Creating messaging demo..."))
        self._create_messaging(users)

        self.stdout.write(self.style.SUCCESS("Database populated successfully!"))

    # RESET DATA

    def _reset_data(self):
        #TODO zajebiscie niebespieczne wywala ci całość w kosmos warto zrobić zabezpieczenie ze jesli nie debug to rise CommandError chba ze z --force
        Message.objects.all().delete()
        Conversation.objects.all().delete()
        Calculation.objects.all().delete()
        TransportOrder.objects.all().delete()
        Stop.objects.all().delete()
        Route.objects.all().delete()
        Driver.objects.all().delete()
        Carrier.objects.all().delete()
        CustomerBranch.objects.all().delete()
        Customer.objects.all().delete()

        User.objects.exclude(is_superuser=True).delete()
        #todo nie ma potrzeby recznie wywalać wszystkiego usuń główne obiekty reszta spadnie sama za pomoca cascade
    # TEST USER

    def _create_test_user(self):
        test_username = os.getenv("TEST_USERNAME", "test_user")
        test_pass = os.getenv("TEST_USER_PASS", "test1234")

        user, created = User.objects.get_or_create(
            username=test_username,
            defaults={
                "email": 'dispatcher@test.com',
                "first_name": 'Test',
                "last_name": "Dispatcher",
            }
        )
        user.set_password(test_pass)
        user.save()

        if created:
            self.stdout.write(self.style.SUCCESS(f" Created test user: {test_username}"))
        else:
            self.stdout.write(self.style.WARNING(" Updated existing test user password"))

        return user

    # RANDOM USERS

    def _create_random_users(self, count=10):
        users = []

        for i in range(1, count + 1):
            username = f"user{i}"
            email = f"{username}@example.com"

            user, created = User.objects.get_or_create(
                username=username,
                defaults={
                    "email": email,
                    "first_name": fake.first_name(),
                    "last_name": fake.last_name(),
                }
            )

            user.set_password(f"{username}pass")
            user.save()

            users.append(user)

        return users

    # CUSTOMERS + BRANCHES

    def _create_customers(self, count=8):
        customers = []

        for _ in range(count):
            customer = Customer.objects.create(
                name=fake.company(),
                nip=fake.unique.msisdn()[:10],
                #todo generalnie spoko ale jakisli dorobisz walidacje nip'a po checksumie to sie wyjebie
                address=fake.address().replace("\n", ", "),
                email=fake.email(),
                phone=fake.phone_number(),
            )
            customers.append(customer)

            for i in range(random.randint(1, 3)):
                CustomerBranch.objects.create(
                    customer=customer,
                    name=f"{fake.city()} ({customer.name} Branch {i})",
                    address=fake.address().replace("\n", ", "),
                )

        return customers

    # CARRIERS

    def _create_carriers(self, count=6):
        carriers = []

        for _ in range(count):
            carrier = Carrier.objects.create(
                name=fake.company(),
                nip=fake.unique.msisdn()[:10],
                address=fake.address().replace("\n", ", "),
                email=fake.email(),
                phone=fake.phone_number(),
            )
            carriers.append(carrier)

        return carriers

    # DRIVERS

    def _create_drivers(self, carriers):
        drivers = []

        for carrier in carriers:
            for _ in range(random.randint(2, 5)):
                driver = Driver.objects.create(
                    carrier=carrier,
                    first_name=fake.first_name(),
                    last_name=fake.last_name(),
                    phone=fake.phone_number(),
                )
                drivers.append(driver)

        return drivers

    # ROUTES + STOPS

    def _create_routes(self, user, count=10):
        routes = []

        for _ in range(count):
            route = Route.objects.create(
                user=user,
                name=f"{fake.city()} → {fake.city()}",
            )
            routes.append(route)

            stops_count = random.randint(3, 6)

            for num in range(1, stops_count + 1):
                Stop.objects.create(
                    route=route,
                    stop_number=num,
                    stop_type=random.choice([c[0] for c in STOP_TYPE_CHOICES]),
                    location=fake.city(),
                    driver_participates=random.choice([True, False]),
                )

        return routes

    # TRANSPORT ORDERS

    def _create_transport_orders(self, customers, carriers, drivers, routes, count=20):
        for _ in range(count):
            customer = random.choice(customers)
            carrier = random.choice(carriers)
            carrier_drivers = [d for d in drivers if d.carrier_id == carrier.id]
            #todo nie potrzebnie budujesz mape za kazdym razem kiedy robisz pętelke
            #mozesz ja zbudować powyżej
            """
            drivers_by_carrier = {}
            for d in drivers:
                drivers_by_carrier.setdefault(d.carrier_id, []).append(d)
                #to powinno być linijce 213
            """
            driver_1 = random.choice(carrier_drivers) if carrier_drivers else None
            driver_2 = random.choice(carrier_drivers) if carrier_drivers and random.choice([True, False]) else None
            #todo obaj driverzy maga być ty samym driverem polecam urzyć random sample
            route = random.choice(routes)

            stops = list(route.stops.all())
            distance = random.randint(300, 2200)

            TransportOrder.objects.create(
                user=route.user,
                customer=customer,
                carrier=carrier,
                driver_1=driver_1,
                driver_2=driver_2,

                loading_place=stops[0].location if stops else fake.city(),
                unloading_place=stops[-1].location if stops else fake.city(),

                distance_km=distance,
                price_for_customer=Decimal(distance) * Decimal("1.50"),
                rate_per_km=Decimal("0.95"),

                carrier_cost=Decimal(distance) * Decimal("0.95"),
                profit=Decimal(distance) * Decimal("1.50") - Decimal(distance) * Decimal("0.95"),
            )

    # CALCULATIONS (apply_schedule + mock)

    def _create_calculations(self, routes, carriers, drivers, test_user):
        for route in routes:
            carrier = random.choice(carriers)
            chosen = random.sample(drivers, k=random.randint(1, 2))
            #todo wybrany driver jest kierowca z całej bazy driverów a nie z danego przewoźnika czy to jest bład ??
            calculation = Calculation(
                user=route.user,
                route=route,
                carrier=carrier,
                driver_1=chosen[0],
                driver_2=chosen[1] if len(chosen) == 2 else None,
                date=date.today() - timedelta(days=random.randint(0, 30)),
            )

            if route.user == test_user:
                apply_schedule(calculation)
            else:
                calculation.total_km = random.randint(200, 2200)
                calculation.total_drive_time_minutes = random.randint(300, 900)
                calculation.total_break_time_minutes = random.randint(30, 200)
                calculation.total_rest_time_minutes = random.randint(200, 600)
                calculation.total_other_work_time_minutes = random.randint(30, 200)
                calculation.admin_time_minutes = random.randint(10, 60)
                calculation.schedule = "Generated schedule data (mock)"

            calculation.save()

    # MESSAGING

    def _create_messaging(self, users):
        for u1 in users:
            partners = [u for u in users if u != u1]
            #todo towrzysz konwersacje które mogą sie powtorzyć powiedzmy ze napierw pan AA jako u1 bedzie miał połaczenie z BB
            #todo następnie pan bb jako u1 bedzie miał poączenie z AA
            for _ in range(2):
                partner = random.choice(partners)

                convo = Conversation.objects.create(
                    user1=u1,
                    user2=partner,
                    subject=fake.sentence(nb_words=4),
                )

                sender = random.choice([u1, partner])
                for _ in range(random.randint(4, 12)):
                    Message.objects.create(
                        conversation=convo,
                        sender=sender,
                        text=fake.sentence(nb_words=random.randint(5, 15)),
                    )
                    sender = partner if sender == u1 else u1


#todo moze warto ustawić seeda tak by nie był losowy, przy debagowaniu bardzo ułatwia sprawe
#todo brak transakcji (transaction.atomic()) jak cos sie wyjebie bedziesz miał baze w połowie wypelniona lepiej dodać i miec pewność ze zawsze albo jest pusta albo w pełni wypełniona
