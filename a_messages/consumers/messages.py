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
            # get user from scope
            self.user = self.scope['user']
            print(self.user.id)
            if self.user.is_anonymous:
                self.close()
                return
            
            # get pk from scope kwargs
            pk = self.scope['url_route']['kwargs']['pk']
            
            # get chat
            self.chat = get_object_or_404(Chat, id=pk)
            self.chat_room =  f'chat{self.chat.pk}'
        
            
            
            # create channel for each websocket connection using unique uuid
            async_to_sync(self.channel_layer.group_add)(
            self.chat_room, # group-name
            self.channel_name)
        
            if not self.chat.is_online(self.user):
                print(f'{self.user.id} is online')
                self.chat.online.add(self.user) # add to online users
                self.track_online_user() # update online users
           
            self.accept()
        except Exception as e:
            print('Discconect')
            print(f"WebSocket REJECT: {str(e)}")
            self.close()
    
    def notify_chat(self, event):
        async_to_sync(self.channel_layer.group_send)(
            self.chat_room,
            event)
    
    def track_online_user(self):
        event = {
            'type' : 'send.response',
            'response':{
                'type' : 'update_online_count',
                'online_count' : self.chat.online_count}
        }
        self.notify_chat(event)
    
    def get_typing_event(self, is_typing = False):
        event = {'type' :'send.response',
                 'response' : {
                     'type' : 'typing',
                     'is_typing' : is_typing,
                     'user' : {'id' : self.user.pk,
                               'name' :f'{self.user.first_name} {self.user.last_name}'}}}
        return event
        
    def receive(self, text_data=None, bytes_data=None):
        data = json.loads(text_data)
        type = data['type']
        
        event = None
        if type == 'start_typing':
            event = self.get_typing_event(True)
        if type == 'stop_typing':
            event = self.get_typing_event(False)
        
        if event:
            self.notify_chat(event)
           
    def disconnect(self, code):
        
        if self.chat.is_online(self.user):
            print(self.chat.is_online(self.user))
            self.chat.online.remove(self.user)
            self.track_online_user()
            
        async_to_sync(self.channel_layer.group_discard(
             self.chat_room,
            self.channel_name
        ))