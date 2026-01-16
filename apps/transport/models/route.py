from django.contrib.auth.models import User
# TODO (maint): Nie importuj User "na sztywno".
from django.db import models


class Route(models.Model):
    """
    Saved route template consisting of multiple ordered stops.
    Used to calculate distance and build driver schedules.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    # TODO (data): Dodaj related_name="routes" (np. user.routes.all()), jeśli będzie to często używane.

    name = models.CharField(max_length=256)
    # TODO (validation/data): Jeśli nazwa trasy ma być unikalna per użytkownik, dodaj UniqueConstraint(user, name)

    created_at = models.DateTimeField(auto_now_add=True)
    # TODO (data): Jeśli często sortujesz po created_at, rozważ db_index=True.

    def __str__(self):
        return self.name

    @property
    def total_stops(self):
        return self.stops.count()
        # TODO (perf): To wykonuje zapytanie COUNT() za każdym razem, gdy property jest użyte.
        # TODO (perf): W listach/ dashboardach lepiej użyć annotate(Count("stops")) i korzystać z tej wartości.