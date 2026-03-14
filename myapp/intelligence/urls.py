from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

from .views import *

urlpatterns=[
# JWT authentication
path('register/', RegisterView.as_view(), name='register'),
path('token/',  MyTokenObtainPairView.as_view(), name='token_obtain_pair'),
path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
path('logout/', LogoutView.as_view(), name='logout'), #need to send the access token in bearer then only work

#Admin Protected Routes
path("admin/staff/", AdminStaffListView.as_view()),
path("admin/staff/create/", AdminCreateStaffView.as_view()),
path("admin/staff/<int:pk>/", AdminStaffDetailView.as_view()),
path("admin/staff/<int:pk>/update/", AdminStaffUpdateView.as_view()),
path("admin/staff/<int:pk>/delete/", AdminStaffDeleteView.as_view()),

#Departmenets
path("admin/departments/", AdminDepartmentListView.as_view()),
path("admin/departments/create/", AdminCreateDepartmentView.as_view()),

# Assign Batch with staff mapping
path("admin/staff/assign-batch/",AssignStaffToBatchView.as_view(),name="assign-staff-batch"),



]