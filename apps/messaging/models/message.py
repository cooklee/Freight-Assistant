from django.contrib.auth.models import User
# TODO (maint): Nie importuj User "na sztywno". Jeśli kiedyś przejdziesz na custom user model, to się wysypie.
from django.db import models

from .conversation import Conversation


class Message(models.Model):
    """
    Single message inside a conversation. Contains content,
    sender and timestamp information.
    """
    conversation = models.ForeignKey(
        Conversation,
        on_delete=models.CASCADE,
        related_name='messages'
    )
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    # TODO (data): Jeśli zależy Ci na sortowaniu po czasie, warto dodać db_index=True.
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.sender.username}: {self.text[:30]}"
