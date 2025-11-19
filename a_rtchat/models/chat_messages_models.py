from django.db import models
from django.contrib.auth import get_user_model
from a_rtchat.models.chat_model import Chat

User = get_user_model()


      
   
class ChatMessage(models.Model):
    group = models.ForeignKey(Chat, related_name='group_messages', on_delete=models.CASCADE)
    user = models.ForeignKey(
        User,
        related_name='user_messages',
        on_delete=models.SET_NULL,
        null=True, blank=True)
    body = models.TextField()
    # media = models.ImageField()
    seen = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)
    # received_at = models.DateTimeField()
    reply_to = models.ForeignKey(
        'self',
        related_name='replies',
        blank=True, null=True,
        on_delete=models.SET_NULL )
    
    @property
    def replies_count(self):
        return self.replies.count()
    
    def __str__(self) -> str:
        return f"{self.user.username} : {self.body}"
    
    class Meta:
        ordering = ['-created']