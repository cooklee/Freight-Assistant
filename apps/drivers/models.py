from django.db import models

from apps.company.models.carrier import Carrier


class Driver(models.Model):
    """
    Driver working for a specific carrier. Used when assigning
    drivers to transport orders or worktime calculations.
    """
    carrier = models.ForeignKey(Carrier, on_delete=models.CASCADE)
    # TODO (style): Rozważ related_name="drivers" na FK, wtedy w Carrier masz carrier.drivers.all() zamiast driver_set. poprawia czytelnosc


    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)

    phone = models.CharField(max_length=20)
    # TODO (data): Rozważ blank=True jeśli numer nie jest zawsze znany na etapie dodawania.
    # TODO (data): Dodaj walidację/normalizację (np. E.164) albo chociaż RegexValidator,
    # TODO (data): bo inaczej pole szybko robi się "śmietnikiem" (spacje, myślniki, różne formaty).
    # TODO (data): Jeśli telefon ma być unikalny w obrębie przewoźnika, rozważ UniqueConstraint(carrier, phone).

    def __str__(self):
        return f'{self.first_name} {self.last_name} - ({self.carrier})'
