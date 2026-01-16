from django.db import models


class Customer(models.Model):
    """
    Client who orders transport services. Stores key company
    information used when creating transport orders.
    """
    name = models.CharField(max_length=150)
    nip = models.CharField(max_length=10, unique=True)
    address = models.CharField(max_length=150)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=20, blank=True)

    def __str__(self):
        return self.name


class CustomerBranch(models.Model):
    """
    Branch or office belonging to a customer. Stores the branch
    name and address for more precise pickup or delivery details.
    """
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='branches')
    name = models.CharField(max_length=150)
    address = models.CharField(max_length=200)

    def __str__(self):
        return f"{self.name} ({self.customer.name})"
    #todo brak unikalności nazw w obrębie klienta uniqueConstraint(fields=['customer', 'name'], name='uniq_branch_name_per_customer')

#todo zauważ ze carrier i customer maja te same dane moze da sie coś z tym zrobi mozna zrobić jedną tabele z opcja customer, i zrobić proxy model