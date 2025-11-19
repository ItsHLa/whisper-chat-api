from rest_framework import permissions
from .models.chat_messages_models import *
from django.shortcuts import get_object_or_404

class IsGroupAdmin(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return not obj.is_private and obj.are_admins([request.user.id])
    
class IsGroupOwner(permissions.BasePermission):
    def has_permission(self, request, view):
        pk = view.kwargs.get('pk')
        group = get_object_or_404(Chat, id=pk, is_private=False)
        return group.is_owner(request.user)

class IsGroupMember(permissions.BasePermission):
    def has_permission(self, request, view):
        pk = view.kwargs.get("pk")
        group = get_object_or_404(Chat, id=pk)
        return group.are_members([request.user])