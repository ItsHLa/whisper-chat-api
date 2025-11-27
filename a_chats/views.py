from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.status import *
from a_chats.models.chat_folder import Folder
from a_chats.permissions import *
from a_chats.serializers.chat_folder import *
from a_chats.serializers.chat import *
from a_chats.serializers.membership import *
from django.shortcuts import get_object_or_404

class FolderViewSet(ModelViewSet):
    permission_classes = [IsAuthenticated, NoRetrieveFolderPermission]
    
    def get_queryset(self):
        return Folder.objects.filter(user = self.request.user).values('id', 'name')
    
    def get_object(self):
        return get_object_or_404(Folder, id= self.kwargs['pk'], user=self.request.user)
    
    def get_serializer_class(self):
        print(self.action)
        if self.action == 'create':
            return CreateChatFolderSerializer
        if self.action == 'partial_update':
            return UpdateChatFolderSerializer

        return FolderSerializer

# Leave group API

     
class ChatViewSet(ModelViewSet):
    
    def get_serializer_class(self):
        print(self.action)
        
        if self.action == 'partial_update':
            return UpdatePublicChatSerializer
        
        if self.action == "list":
            return ListChatSerializer

        return ChatSerializer  
    
    def get_queryset(self):
        if self.action == 'join':
            return Chat.objects.all()
        return Chat.objects.filter(members=self.request.user).prefetch_related('folders','members')
    
    def get_permissions(self):
        print(self.action)
        if self.action in ['destroy', 'remove_admins', 'add_admins' ] :
            return [IsAuthenticated(), IsGroupOwner()]
        if self.action in ['retrieve','add_members', 'leave']:
            return [IsAuthenticated(), IsGroupMember()]
        if self.action in ['join', 'create']:
            return [AllowAny()]
        return [IsAuthenticated(), IsGroupAdmin()]
    
    def list(self, request, *args, **kwargs):
        chats = self.get_queryset()
        folders = Folder.objects.filter(chats__in = chats).distinct()
        
        return Response({
            "folders" : FolderSerializer(folders, many=True).data,
            "chats" : self.get_serializer(chats, many=True).data}, HTTP_200_OK)
    
    @action(detail=True, methods=['post'] )
    def join(self, request, pk):
        group = get_object_or_404(Chat, id=pk, is_private=False)
        group.add_members([request.user])
        return Response(status= HTTP_200_OK)
    
    @action(detail=True, methods=['delete'] )
    def leave(self, request, pk):
        group = get_object_or_404(Chat, id=pk, is_private = False)
        group.remove_membership([request.user])
        return Response(status= HTTP_200_OK)
    
    # Member + list, get
    @action(detail=True, methods=['post'])
    def add_members(self, request, pk):
        group = get_object_or_404(Chat, id=pk, is_private = False)
        serializer = MembershipSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.validated_data['group'] = group
        serializer.add_users() 
        return Response(status= HTTP_200_OK)
               
    @action(detail=True, methods=['delete'],)
    def remove_admins(self, request, pk):
        object = get_object_or_404(Chat, id=pk, is_private = False)
        serializer = AdminSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.validated_data['group'] = object
        serializer.remove_users()
        return Response(status= HTTP_200_OK)
    
    @action(detail=True, methods=['patch'],)
    def add_admins(self, request, pk):
        object = get_object_or_404(Chat, id=pk, is_private = False)
        serializer = AdminSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.validated_data['group'] = object
        serializer.add_users()
        return Response(status= HTTP_200_OK)
 
    @action(detail=True, methods=['delete'])
    def remove_members(self, request, pk):
        group = self.get_object()
        serializer = MembershipSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.validated_data['group'] = group
        serializer.remove_users() 
        return Response(status= HTTP_200_OK)
    
