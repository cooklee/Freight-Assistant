from django.db import models

from .route import Route

STOP_TYPE_CHOICES = [
    ('START_FROM_BASE', 'Start from base'),
    ('LOADING', 'Loading'),
    ('UNLOADING', 'Unloading'),
    ('PARTIAL_LOADING', 'Partial loading'),
    ('PARTIAL_UNLOADING', 'Partial unloading'),
    ('FINAL_STOP', 'Final stop'),
    ('RETURN_TO_BASE', 'Return to base'),
]
# TODO (style): Rozważ użycie TextChoices (Django) zamiast listy krotek — lepsza czytelność i autouzupełnianie.


class Stop(models.Model):
    """
    A single stop on the route.
    Arranging the order of stops/route numbers.
    """
    route = models.ForeignKey(Route, on_delete=models.CASCADE, related_name='stops')

    stop_number = models.IntegerField()
    # TODO (validation): Rozważ PositiveIntegerField albo walidację min_value=1.
    # TODO (data): Dodaj UniqueConstraint(route, stop_number), żeby nie dało się mieć dwóch stopów o tym samym numerze w jednej trasie.

    stop_type = models.CharField(max_length=30, choices=STOP_TYPE_CHOICES)
    # TODO (data): Jeśli stop_type jest wymagany, OK. Jeśli czasem może być pusty, ustaw blank=True i dodaj empty choice.

    location = models.CharField(max_length=150)
    # TODO (data): Jeśli location to miasto/adres, rozważ większy max_length (adresy potrafią być dłuższe).

    driver_participates = models.BooleanField(default=True)

    def __str__(self):
        return f"Stop {self.stop_number} - {self.stop_type} ({self.location})"

    class Meta:
        ordering = ['stop_number']
