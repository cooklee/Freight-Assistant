from django.db import models


class Carrier(models.Model):
    """
    Transport company responsible for executing freight orders.
    Contains basic business and contact details.
    """
    name = models.CharField(max_length=150)
    nip = models.CharField(max_length=10, unique=True)
    address = models.CharField(max_length=150, blank=True)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=20, blank=True)

    def __str__(self):
        return self.name

#todo brak validatorow, nip,email,phon
#todo adres jako model bym zrobił
