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


class Stop(models.Model):
    """
    A single stop on the route.
    Arranging the order of stops/route numbers.
    """
    route = models.ForeignKey(Route, on_delete=models.CASCADE, related_name='stops')

    stop_number = models.IntegerField()
    stop_type = models.CharField(max_length=30, choices=STOP_TYPE_CHOICES)
    location = models.CharField(max_length=150)

    driver_participates = models.BooleanField(default=True)

    def __str__(self):
        return f"Stop {self.stop_number} - {self.stop_type} ({self.location})"

    class Meta:
        ordering = ['stop_number']
