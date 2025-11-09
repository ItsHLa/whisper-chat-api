from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import TokenBlacklistView, TokenRefreshView
from .views import *
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register('otp', OTPViewSet, basename='otp')
router.register('users/me', AccountViewSet, basename='account')

urlpatterns = [
    path('', include(router.urls)),
    path('users/login/', CustomTokenObtainPairView.as_view(), name='log-in'),
    path('users/logout/', TokenBlacklistView.as_view(),  name='log-out'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
     
]