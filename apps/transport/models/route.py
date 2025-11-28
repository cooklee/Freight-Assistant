from django.contrib.auth.models import User
from django.db import models


class Route(models.Model):
    """
    Saved route template consisting of multiple ordered stops.
    Used to calculate distance and build driver schedules.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=256)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    @property
    def total_stops(self):
        return self.stops.count()
