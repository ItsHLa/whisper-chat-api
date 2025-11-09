from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # auth
    path('api/', include('a_core.urls')),
    path('api/', include("djoser.urls")),
]
