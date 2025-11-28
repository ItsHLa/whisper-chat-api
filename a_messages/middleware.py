import jwt
from rest_framework_simplejwt.tokens  import  AccessToken
from rest_framework_simplejwt.token_blacklist.models  import  BlacklistedToken
from channels.db  import database_sync_to_async
from django.conf import settings
from django.contrib.auth.models import AnonymousUser
from django.contrib.auth import get_user_model

User = get_user_model()

@database_sync_to_async
def is_blacklisted(token_jti):
    """Check if token is blacklisted using JWT ID"""
    try:
        return BlacklistedToken.objects.filter(token__jti = token_jti).exists()
    except Exception as e:
        print(f'Exception: {e}')
        return False

@database_sync_to_async
def get_user(id):
    """Get user by ID"""
    try:
        return User.objects.get(id = int(id))
    except User.DoesNotExist:
        return AnonymousUser()

class JWTMiddelware:
    def __init__(self, app):
        self.app = app
            
    def _validate_token(self, token):
        """Validate token and extract payload"""
        try:
            payload = jwt.decode(
                token,
                settings.SECRET_KEY,
                algorithms=["HS256"]
            )
            print(payload)
            return True, payload
        except jwt.ExpiredSignatureError:
            return False, 'Token Expired' 
        except jwt.InvalidTokenError:
            return False, 'Token Invalid'
        except Exception as e:
            return False, f'Token validation error: {str(e)}'
    
    def _get_authorization(self, scope):
        try:
            headers = dict(scope.get('headers'))
            return headers.get(b'authorization',b'').decode()
        except Exception as e:
            print(f'Authorization Exception: {e}') 
            return None  
    
    def _extract_token(self, authorization):
        try:
            if authorization and authorization.startswith('Bearer'):
                return authorization.split(' ')[1]
            return None
        except Exception as e:
            print(f'Extract Token: {e}') 
            return None 
    
    async def __call__(self, scope, receive, send):
        if scope["type"] != "websocket":
            return await self.app(scope, receive, send)
        scope['user'] = AnonymousUser()
        authorization = self._get_authorization(scope)
        if authorization:
            token = self._extract_token(authorization)
            is_valid, data = self._validate_token(token)
            if is_valid: 
                jti = data.get('jti')
                blacklisted = await is_blacklisted(jti)
                if not blacklisted:
                    scope['user'] = await get_user(data['user_id'])
                    
        return await self.app(scope, receive, send)