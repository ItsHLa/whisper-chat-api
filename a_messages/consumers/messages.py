from channels.generic.websocket import WebsocketConsumer
from django.shortcuts import get_object_or_404
from a_chats.models.chat import *
from a_messages.models.chat_messages import ChatMessage
from a_messages.serializers.chat_message import *
from asgiref.sync import async_to_sync
import json



class MessagesWebsocketConsumer(WebsocketConsumer):
    
    def send_response(self, event):
        self.send(json.dumps(event['response']))
    
    def connect(self):
        try:
            kwargs = self.scope['url_route']['kwargs']
            
        # get pk from scope kwargs
            pk = kwargs['pk']
            
        # get chat
            self.chat = get_object_or_404(Chat, id=pk)
            
        # get user from scope
            self.user = User.objects.get(id=2)
            
        # create channel for each websocket connection using unique uuid
            async_to_sync(self.channel_layer.group_add)(
            f'chat{self.chat.pk}', # group-name
            self.channel_name)
        
            if not self.chat.is_online(self.user):
                self.chat.online.add(self.user) # add to online users
                self.track_online_user() # update online users
           
            self.accept()
        except Exception as e:
            print('Discconect')
            print(f"WebSocket REJECT: {str(e)}")
            self.close()
    
    def notify_chat(self, event):
        async_to_sync(self.channel_layer.group_send)(
            f'chat{self.chat.pk}',
            event)
    
    def track_online_user(self):
        event = {
            'type' : 'send.response',
            'response':{
                'type' : 'update_online_count',
                'online_count' : self.chat.online_count}
        }
        
        self.notify_chat(event)
        
    def receive(self, text_data=None, bytes_data=None):
       pass
    
           
    def disconnect(self, code):
        
        if self.chat.is_online(self.user):
            self.chat.online.remove(self.user)
            self.track_online_user()
            
        async_to_sync(self.channel_layer.group_discard(
            f'chat{self.chat.pk}',
            self.channel_name
        ))