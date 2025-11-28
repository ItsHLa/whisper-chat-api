import os
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from django.core.asgi import get_asgi_application
from channels.security.websocket import AllowedHostsOriginValidator
from a_messages.middleware import JWTMiddelware
from a_messages.ws_urls import websocket_urlpatterns

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'a_core.settings')

django_asgi_app = get_asgi_application()

application = ProtocolTypeRouter({
    'http' : django_asgi_app,
    'websocket' : AuthMiddlewareStack(JWTMiddelware(URLRouter(websocket_urlpatterns)))
})
