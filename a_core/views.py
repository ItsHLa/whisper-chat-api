from rest_framework_simplejwt.views import TokenObtainPairView

from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.viewsets import ViewSet
from rest_framework.decorators import action
from rest_framework.status import *

from .utils.OTP import *
from .serializers import *




class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

class OTPViewSet(ViewSet):
    permission_classes = [AllowAny]
    
    @action(detail=False, methods=['POST'])
    def send(self, request):
        data = request.data
        serializer = SendOTPSerializer(data=data)
        serializer.is_valid(raise_exception = True)
        otp = OTP.generate(serializer.validated_data['email'])
        return Response({'otp':str(otp)},status=HTTP_201_CREATED)
            
    @action(detail=False, methods=['POST'])
    def verify(self, request):
        data = request.data
        serializer = VerifyOTPSerializer(data=data)
        serializer.is_valid(raise_exception = True)
        print(serializer.validated_data)
        is_valid = OTP.verify(
            serializer.validated_data['email'],
            serializer.validated_data['otp'])
        if not is_valid:
            return Response({'otp':'Invalid OTP code'},status=HTTP_400_BAD_REQUEST)
        return Response(status=HTTP_200_OK)

class AccountViewSet(ViewSet) :
    @action(detail=False, methods=['patch'])
    def deactivate(self, request):
        user = request.user
        user.is_active = False
        user.save(update_fields = ['is_active'])  
        return Response(status=HTTP_200_OK)     