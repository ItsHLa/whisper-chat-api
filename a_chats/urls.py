from django.urls import include, path
from rest_framework.routers import DefaultRouter
from rest_framework_nested.routers  import NestedDefaultRouter

from a_messages.views import MessageViewSet
from .views import *

router = DefaultRouter()

router.register('folders', FolderViewSet, basename='folders')
router.register('', ChatViewSet, basename='chats')

# create nested route inside chats
messages_routes = NestedDefaultRouter(router, '', lookup='chat')
messages_routes.register('messages', MessageViewSet, basename='chat-messages')


urlpatterns = [
    path('', include(router.urls)),
    path('', include(messages_routes.urls)),
]