from django.db import models
from apps.company.models.carrier import Carrier

class Driver(models.Model):
    carrier = models.ForeignKey(Carrier, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    phone = models.CharField(max_length=20)
