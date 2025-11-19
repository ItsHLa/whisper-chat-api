from django.urls import include, path
from rest_framework_nested import routers
from .views import *

router = routers.DefaultRouter()

router.register('', ChatViewSet, basename='chats')
router.register('folders', ChatFolderViewSet, basename='folders')


urlpatterns = [
    path('', include(router.urls)),
    
]