from django.db import models

from apps.company.models.carrier import Carrier


class Driver(models.Model):
    """
    Driver working for a specific carrier. Used when assigning
    drivers to transport orders or worktime calculations.
    """
    carrier = models.ForeignKey(Carrier, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    phone = models.CharField(max_length=20)

    def __str__(self):
        return f'{self.first_name} {self.last_name} - ({self.carrier})'
