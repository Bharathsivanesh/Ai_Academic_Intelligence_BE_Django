from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

from .views import LogoutView, RegisterView, MyTokenObtainPairView

urlpatterns=[
# JWT authentication
path('register/', RegisterView.as_view(), name='register'),
path('token/',  MyTokenObtainPairView.as_view(), name='token_obtain_pair'),
path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
path('logout/', LogoutView.as_view(), name='logout'), #need to send the access token in bearer then only work


]