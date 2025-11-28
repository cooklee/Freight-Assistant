from django.contrib.auth.models import User
from django.db import models


class Conversation(models.Model):
    """
    One-to-one chat thread between two users. Groups messages
    exchanged in the internal messaging system.
    """
    user1 = models.ForeignKey(User, on_delete=models.CASCADE, related_name='conversations_started')
    user2 = models.ForeignKey(User, on_delete=models.CASCADE, related_name='conversations_received')
    subject = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def participants(self):
        return [self.user1, self.user2]

    def get_other_user(self, current_user):
        return self.user2 if self.user1 == current_user else self.user1

    def __str__(self):
        return f"Conversation: {self.subject or 'No subject'}"
