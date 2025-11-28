from rest_framework import serializers
from ..models.chat_messages import ChatMessage

class ChatMessageSerializer(serializers.ModelSerializer):

    user = serializers.SerializerMethodField()
    replies = serializers.SerializerMethodField()
    
    class Meta:
        model = ChatMessage
        fields = ('id', 'body', 'user', 'seen', 'is_edited', 'replies_count', 'replies')
    
    def get_replies(self, obj):
        return ChatMessageSerializer(obj.replies, many= True).data
    
    def get_user(self, obj):
        return {
            'id' : obj.user.id,
            'name' : obj.user.username,
            'profile_photo' : None
        }


class ChatRepresentationMixin:
    def to_representation(self, instance):
        return ChatMessageSerializer(instance, context=self.context).data
    

class CreateUpdateChatMessageSerializer(ChatRepresentationMixin, serializers.ModelSerializer):
    
    class Meta:
        model = ChatMessage
        fields = ('body',)