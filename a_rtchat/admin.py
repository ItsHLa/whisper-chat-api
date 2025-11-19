from django.contrib import admin

from a_rtchat.models.chat_folder_mode import ChatFolder
from a_rtchat.models.chat_model import Chat
from a_rtchat.models.chat_model import ChatMembership
from .models.chat_messages_models import *

admin.site.register(Chat)
admin.site.register(ChatFolder)
admin.site.register(ChatMessage)
admin.site.register(ChatMembership)
