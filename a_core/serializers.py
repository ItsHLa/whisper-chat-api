from rest_framework import serializers
from rest_framework import exceptions
from django.contrib.auth import get_user_model

from djoser.serializers import UserCreateSerializer

from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

User = get_user_model()

class CustomUserCreateSerializer(UserCreateSerializer):
    
    tokens = serializers.SerializerMethodField()
    
    class Meta(UserCreateSerializer.Meta):
        fields = ('id', 'first_name', 'last_name', 'username', 'email', 'phone_number', 'password', 'tokens')
        
    def get_tokens(self, obj):
        refresh = RefreshToken.for_user(obj)
        return{
            'refresh' : str(refresh),
            'access' : str(refresh.access_token)
        }
        
class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    
    def validate(self, attrs):
        auth_kwargs = {
            self.username_field : attrs[self.username_field],
            'password' : attrs['password']
        }
        
        try:
            auth_kwargs['request'] = self.context['request']
        except KeyError:
            pass
        try:
            self.user = User.objects.get(**{self.username_field : attrs[self.username_field]})
        except User.DoesNotExist:
            raise exceptions.AuthenticationFailed(
                'No active account found with the given credentials'
            )
        if not self.user.check_password(attrs['password']):
            raise exceptions.AuthenticationFailed(
                'No active account found with the given credentials')
        self.user.is_active = True
        self.user.save(update_fields=['is_active'])
        refresh = self.get_token(self.user)
        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }
        
class SendOTPSerializer(serializers.Serializer):
    email = serializers.EmailField()

class VerifyOTPSerializer(serializers.Serializer):
    email = serializers.EmailField() 
    otp = serializers.CharField(max_length = 6)    
        
