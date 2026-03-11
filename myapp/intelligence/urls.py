from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

from intelligence.views.auth_views import LogoutView

urlpatterns=[
    # JWT authentication
# path('api/register/', RegisterView.as_view(), name='register'),
# path('api/token/',  MyTokenObtainPairView.as_view(), name='token_obtain_pair'),
path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
path('api/logout/', LogoutView.as_view(), name='logout'),


]