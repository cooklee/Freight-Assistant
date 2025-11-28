from django.db import models

from apps.company.models.carrier import Carrier
from apps.company.models.customer import Customer
from apps.drivers.models import Driver


class TransportOrder(models.Model):
    """
    Represents a single transport job. Stores route details,
    pricing, assigned carrier and assigned driver(s).
    """
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    carrier = models.ForeignKey(Carrier, on_delete=models.CASCADE)

    driver_1 = models.ForeignKey(
        Driver, on_delete=models.SET_NULL, null=True, blank=True, related_name='main_driver'
    )
    driver_2 = models.ForeignKey(
        Driver, on_delete=models.SET_NULL, null=True, blank=True, related_name='co_driver'
    )

    loading_place = models.CharField(max_length=150)
    unloading_place = models.CharField(max_length=150)

    distance_km = models.PositiveIntegerField(default=0)

    price_for_customer = models.DecimalField(max_digits=10, decimal_places=2)
    rate_per_km = models.DecimalField(max_digits=6, decimal_places=2)

    carrier_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    profit = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order {self.id} for {self.customer.name}"
