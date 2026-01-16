from django.db import models
from django.contrib.auth.models import User
# TODO (maint): Nie importuj User "na sztywno".
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
    user = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name="calculations",
        null=True,
        blank=True,
    )
    # TODO (data): user jest null=True/blank=True — czy Calculation może istnieć bez usera?

    route = models.ForeignKey(Route, on_delete=models.PROTECT)
    # TODO (data/security): Warto rozważyć related_name="calculations" na route, żeby mieć route.calculations.all().
    # TODO (data/security): Sprawdź spójność: route.user powinien == calculation.user (jeśli oba istnieją).

    carrier = models.ForeignKey(Carrier, on_delete=models.CASCADE)
    # TODO (data): Jeśli chcesz reverse relację, dodaj related_name="calculations" (np. carrier.calculations.all()).

    driver_1 = models.ForeignKey(
        Driver, on_delete=models.SET_NULL, null=True, related_name="calc_driver_1"
    )
    driver_2 = models.ForeignKey(
        Driver, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="calc_driver_2"
    )
    # TODO (data): Rozważ walidację:
    # TODO (data): - driver_1 != driver_2
    # TODO (data): - driver_1/driver_2 należą do carrier (driver.carrier_id == carrier_id)
    # TODO (data): To najlepiej zrobić w clean() / ModelForm.clean().

    date = models.DateField()
    # TODO (data): Rozważ db_index=True jeśli często filtrujesz po dacie (np. raporty).
    # TODO (validation): Jeśli date nie może być w przyszłości/przeszłości, dodaj walidację w formie.

    total_km = models.IntegerField(null=True, blank=True)
    total_drive_time_minutes = models.IntegerField(null=True, blank=True)

    total_break_time_minutes = models.IntegerField(null=True, blank=True)
    total_rest_time_minutes = models.IntegerField(null=True, blank=True)
    total_other_work_time_minutes = models.IntegerField(null=True, blank=True)
    admin_time_minutes = models.IntegerField(null=True, blank=True)
    # TODO (validation): Jeśli to są czasy w minutach, rozważ PositiveIntegerField albo walidację min_value=0
    # TODO (validation): żeby uniknąć ujemnych wartości.

    schedule = models.TextField(null=True, blank=True)
    # TODO (data): Jeśli schedule bywa duży i często wyświetlasz listy Calculation, rozważ defer('schedule') w querysetach.
    # TODO (data): Jeśli schedule ma strukturę (np. JSON), rozważ JSONField zamiast TextField.

    created_at = models.DateTimeField(auto_now_add=True)
    # TODO (data): Jeśli często sortujesz po created_at, rozważ db_index=True.

    def __str__(self):
        # TODO (perf): self.route.name wymaga dostępu do powiązanego obiektu; w admin listach może powodować dodatkowe zapytania
        # TODO (perf): jeśli nie używasz select_related('route') w querysetach.
        # TODO (ux): Warto dodać pk/ID w stringu dla jednoznaczności.
        return (
            f"Calculation for route {self.route.name} "
            f"[{self.date}] - {self.total_km or 0} km"
        )
