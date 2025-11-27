from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class ChatMembership(models.Model):
    chat = models.ForeignKey('Chat', related_name='chat_membership', on_delete=models.CASCADE) 
    user = models.ForeignKey(User, related_name='user_membership', on_delete=models.CASCADE)
    is_admin = models.BooleanField(default=False)
    is_owner = models.BooleanField(default=False)
    is_member = models.BooleanField(default=False)
    
    class Meta:
        unique_together = ['chat', 'user']
        indexes = [
            
            models.Index(
                fields=['user', 'chat'],
                name='user_chat_idx'),
            models.Index(
                fields=['chat'],
                condition= models.Q(is_admin=True),
            name='is_admin_idx'),
            models.Index(
                fields=['chat'],
                condition= models.Q(is_member=True),
                 name='is_member_idx',
                ),
            models.Index(
                fields=['chat'],
                condition= models.Q(is_owner=True),
                 name='is_owner_idx'
                ),]
    
    def __str__(self) -> str:
        role = 'member'
        if self.is_admin : 
            role = 'admin'
        if self.is_owner:
            role = 'owner'
        return f" user : {self.user.id} | chat: {self.chat.id} | role : {role}"
    
