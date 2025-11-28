import uuid
from django.db import models
from django.contrib.auth import get_user_model
from a_chats.managers.chat import ChatManager
from a_chats.models.public_group_membership import ChatMembership

User = get_user_model()

class Chat(models.Model):
    name = models.CharField(max_length=128, null=True, blank=True)
    description = models.CharField(max_length=300, blank=True, null=True)
    uid = models.UUIDField(unique=True, default=uuid.uuid4, editable=False)
    is_private = models.BooleanField(default=False)
    is_empty = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    members = models.ManyToManyField(
        User,
        through= 'ChatMembership',
        through_fields=['chat','user'],
        related_name='chats')
    online = models.ManyToManyField(
        User,
        blank=True,
        related_name='group_online_members')
    
    def is_owner(self, user):
        return self.chat_membership.filter(
            user=user, 
            is_owner=True) 
    
    def are_admins(self, users):
        return self.chat_membership.filter(
            user__in=users,
            is_admin=True)
        
    def are_members(self, users):
        return self.chat_membership.filter(
            user__in=users,
            is_member=True)
    
    def remove_membership(self, users): 
        self.chat_membership.filter(user__in = users).delete()
        if self.chat_membership.all().count() == 0:
            print(self.chat_membership.all().count())
            self.is_empty = True
            self.save()
    
    def add_admins(self, users):
       return self.chat_membership.filter(user__in = users).update(is_admin=True)
    
    def remove_admin(self, users):
        return self.chat_membership.filter(user__in = users).update(is_admin=False)
    
    def add_members(self,  users):
        role= {"is_member" : True}
        members = [ChatMembership(
            chat= self,
            user=user,
            **role
        ) for user in users ]
        return ChatMembership.objects.bulk_create(members)
    
    def add_owner(self, user):
        role = {"is_owner" : True, "is_admin" : True, "is_member" : True}
        return ChatMembership.objects.create(
            chat= self,
            user=user,
            **role)    
    
    def is_online(self, user):
        return self.online.filter(id=user.id).exists()   
     
    objects = ChatManager()
    
    @property
    def members_count(self):
        return self.members.count()
    
    @property
    def online_count(self):
        return self.online.count()
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['name'], name='chat_name_idx'),
        ]
        
    def __str__(self) -> str:
        str = None
        if self.is_private:
            return f"Private {self.id} - {self.uid}"
        return f"Public {self.id} - {self.uid}"
 
 
