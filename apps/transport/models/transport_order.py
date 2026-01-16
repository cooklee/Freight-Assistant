from django.db import models
from django.contrib.auth.models import User
# TODO (maint): Nie importuj User "na sztywno".
from apps.company.models.carrier import Carrier
from apps.company.models.customer import Customer
from apps.drivers.models import Driver


class TransportOrder(models.Model):
    """
    Represents a single transport job. Stores route details,
    pricing, assigned carrier and assigned driver(s).
    """
    user = models.ForeignKey(
        User,
        related_name="orders",
        on_delete=models.CASCADE,
        null=True, blank=True,
    )
    # TODO (data/security): Czy order może istnieć bez usera? Jeśli nie, usuń null/blank.
    # TODO (data): Jeśli często filtrujesz po user, rozważ db_index=True (FK ma indeks w większości DB, ale warto wiedzieć).

    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    carrier = models.ForeignKey(Carrier, on_delete=models.CASCADE)

    driver_1 = models.ForeignKey(
        Driver, on_delete=models.SET_NULL, null=True, blank=True, related_name='main_driver'
    )
    driver_2 = models.ForeignKey(
        Driver, on_delete=models.SET_NULL, null=True, blank=True, related_name='co_driver'
    )
    # TODO (data): Rozważ walidację spójności:
    # TODO (data): - driver_1 != driver_2
    # TODO (data): - driver_1/driver_2 należą do carrier (driver.carrier_id == carrier_id)
    # TODO (data): To najlepiej zrobić w clean() / ModelForm.clean().

    loading_place = models.CharField(max_length=150)
    unloading_place = models.CharField(max_length=150)
    # TODO (data): Jeśli to adresy, 150 może być za mało. Rozważ 255+ lub osobne pola/Place ID.

    distance_km = models.PositiveIntegerField(default=0)
    # TODO (data): Jeśli dopuszczasz dystans niecałkowity (np. 12.5 km), rozważ DecimalField.
    # TODO (validation): Jeśli distance_km ma być zawsze > 0, dodaj walidację (min_value=1) zamiast default=0.

    price_for_customer = models.DecimalField(max_digits=10, decimal_places=2)
    rate_per_km = models.DecimalField(max_digits=6, decimal_places=2)
    # TODO (finance): Rozważ walidację min_value=0 dla obu pól (ujemne ceny/stawki raczej nie mają sensu).

    carrier_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    profit = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    # TODO (business): carrier_cost i profit wyglądają na pola pochodne.
    #  Rozważ liczenie ich w jednym miejscu (model.save/clean albo serwis) zamiast w formach,
    #  żeby nie rozjechało się przy innych ścieżkach zapisu (admin, import, API).
    # TODO (finance): Dla default w DecimalField lepiej użyć Decimal("0.00") (czytelność), choć 0 też działa.

    created_at = models.DateTimeField(auto_now_add=True)
    # TODO (data): Jeśli często sortujesz/filtrujesz po created_at, rozważ db_index=True.

    def __str__(self):
        # TODO (perf): self.customer.name wymaga dostępu do FK; w listach admina może powodować dodatkowe zapytania
        # TODO (perf): jeśli nie używasz select_related('customer') w querysetach.
        return f"Order {self.id} for {self.customer.name}"
