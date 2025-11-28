from django.db import models
from django.contrib.auth import get_user_model
from a_chats.models.chat import Chat

User = get_user_model()


class ChatMessage(models.Model):
    chat = models.ForeignKey(
        Chat, 
        related_name='chat_messages', 
        on_delete=models.CASCADE)
    user = models.ForeignKey(
        User,
        related_name='user_messages',
        on_delete=models.SET_NULL,
        null=True, blank=True)
    body = models.TextField()
    # media = models.ImageField()
    seen = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    # received_at = models.DateTimeField()
    reply_to = models.ForeignKey(
        'self',
        related_name='replies',
        blank=True, null=True,
        on_delete=models.SET_NULL)
    
    @property
    def is_edited(self):
        return self.created_at.replace(microsecond=0) != self.updated_at.replace(microsecond=0)
    
    @property
    def replies_count(self):
        return self.replies.count()
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self) -> str:
        return f"pk: {self.pk} | author: {self.user.username} | body: {self.body}"
    
    