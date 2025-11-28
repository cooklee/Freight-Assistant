from django.db import models

from apps.company.models.carrier import Carrier
from apps.drivers.models import Driver
from .route import Route


class Calculation(models.Model):
    """
    Calculation results for a given route.
    Generated from:
    - Stop
    - Google Maps API (distances + durations)
    - EU regulations
    """

    route = models.ForeignKey(Route, on_delete=models.PROTECT)
    carrier = models.ForeignKey(Carrier, on_delete=models.CASCADE)

    driver_1 = models.ForeignKey(
        Driver, on_delete=models.SET_NULL, null=True, related_name="calc_driver_1"
    )
    driver_2 = models.ForeignKey(
        Driver, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="calc_driver_2"
    )

    date = models.DateField()

    total_km = models.IntegerField(null=True, blank=True)
    total_drive_time_minutes = models.IntegerField(null=True, blank=True)

    total_break_time_minutes = models.IntegerField(null=True, blank=True)
    total_rest_time_minutes = models.IntegerField(null=True, blank=True)
    total_other_work_time_minutes = models.IntegerField(null=True, blank=True)
    admin_time_minutes = models.IntegerField(null=True, blank=True)

    schedule = models.TextField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return (
            f"Calculation for route {self.route.name} "
            f"[{self.date}] - {self.total_km or 0} km"
        )
