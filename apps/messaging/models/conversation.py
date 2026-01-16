from django.contrib.auth.models import User
# TODO: user na sztywno

from django.db import models


class Conversation(models.Model):
    """
    One-to-one chat thread between two users. Groups messages
    exchanged in the internal messaging system.
    """
    user1 = models.ForeignKey(User, on_delete=models.CASCADE, related_name='conversations_started')
    # TODO: Warto przemyśleć nazewnictwo: user1/user2 jest OK, ale bywa nieczytelne. moze sender albo initiator ...

    user2 = models.ForeignKey(User, on_delete=models.CASCADE, related_name='conversations_received')
    # TODO: Brakuje ograniczenia, żeby user1 != user2 (żeby nie dało się zrobić rozmowy z samym sobą).
    # TODO: Brakuje ograniczenia unikalności pary (user1, user2) niezależnie od kolejności.
    #       Aktualnie można stworzyć duplikaty: (A,B) i (B,A) oraz wiele identycznych wątków.


    subject = models.CharField(max_length=255, blank=True)
    # TODO: Jeśli subject ma być opcjonalny, OK. Jeśli ma być nullowalny w DB, to potrzebne null=True 
    # TODO: Możesz rozważyć index, jeśli często filtrujesz po subject (zwykle nie trzeba).

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    # TODO: updated_at będzie się zmieniać przy każdym zapisie Conversation.
    #       Jeśli chcesz, by aktualizowało się przy nowej wiadomości, a wiadomość jest osobnym modelem,
    #       musisz to robić jawnie (np. update() przy dodaniu Message) — auto_now tego sam nie załatwi.

    def participants(self):
        return [self.user1, self.user2]

    def get_other_user(self, current_user):
        # TODO: Jeśli current_user nie jest ani user1 ani user2, to ta metoda zwróci user1 (bo warunek false).
        #       To może maskować bugi/autoryzację. Lepiej byłoby w takiej sytuacji rzucić wyjątek
        return self.user2 if self.user1 == current_user else self.user1

    def __str__(self):
        # TODO: subject może być długie; czasem lepiej skracać do np. 50 znaków w __str__
        return f"Conversation: {self.subject or 'No subject'}"