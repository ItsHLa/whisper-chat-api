from rest_framework.viewsets import ModelViewSet
from channels.layers import get_channel_layer
from a_messages.models.chat_messages import ChatMessage
from a_messages.serializers.chat_message import *
from asgiref.sync import async_to_sync
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action

from rest_framework.response import Response
from rest_framework.status import *

class MessageViewSet(ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = ChatMessage.objects.filter(reply_to__isnull=True).select_related('user').prefetch_related('replies')
    
    def _notify_chat(self, chat_pk, event):
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f'chat{chat_pk}',
            event)
    
    def get_serializer_class(self):
        if self.action in ['create','partial_update', 'reply' ]:
            return CreateUpdateChatMessageSerializer
        return ChatMessageSerializer
    
    @action(detail=True, methods=['post'])
    def reply(self, request, chat_pk, pk):
        message = self.get_object()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        reply = serializer.save(
            user = request.user,
            chat_id = chat_pk,
            reply_to = message)
        data = self.get_serializer(reply).data
        event = {
            'type' : 'send.response',
            'response' : {
                'type' : 'reply message',
                'reply_to' : message.pk,
                **data
            }
        }
        self._notify_chat(chat_pk, event)
        return Response(data, HTTP_201_CREATED)
        
    def perform_create(self, serializer):
        chat_pk = self.kwargs['chat_pk']
        print(chat_pk)
        message = serializer.save(
            user = self.request.user,
            chat_id = chat_pk)
        data  = ChatMessageSerializer(message).data
        event = {
            'type' : 'send.response',
            'response' : {
                'type' : 'send_message',
                **data
            }
        }
        self._notify_chat(chat_pk, event)
        return message
    
    def perform_update(self, serializer):
        chat_pk = self.kwargs['chat_pk']
        message = serializer.save()
        data = ChatMessageSerializer(message).data
        event = {
                'type': 'send.response',
                'response' : {
                    'type' : 'update_message',
                    **data
                }
            }
        self._notify_chat(chat_pk, event)
        return message
    
    def perform_destroy(self, instance):
        chat_pk = self.kwargs['chat_pk']
        message_pk = instance.pk
        instance.delete()
        print(chat_pk)
        print(message_pk)
        event = {
                'type': 'send.response',
                'response' : {
                    'type' : 'delete_message',
                    'pk' : message_pk
                }
            }
        self._notify_chat(chat_pk, event)
        return None