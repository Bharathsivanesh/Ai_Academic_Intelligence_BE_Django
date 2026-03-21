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

#Get All the batches
path("batches/", BatchListView.as_view(), name="batch-list"),
#Get Subject basodn on department id
path("departments/<int:department_id>/subjects/",SubjectByDepartmentView.as_view(),name="subjects-by-department"),

#Add Exam admin
path("admin/create-exam/", AdminCreateExamView.as_view(), name="create-exam"),

#Admin overview
path("admin/dashboard-stats/", AdminDashboardStatsView.as_view(), name="dashboard-stats"),

#--------------------------------------------------------------------------------------------------------------------------

#Staff Protected Routes
# path("admin/staff/", AdminStaffListView.as_view()),
path("admin/student/create/", StaffCreateStudentView.as_view()),
path("admin/students/", AdminStudentListView.as_view()),
path("admin/students/<int:pk>/", AdminStudentDetailView.as_view()),
path("admin/students/<int:pk>/update/", AdminStudentUpdateView.as_view()),
path("admin/students/<int:pk>/delete/", AdminStudentDeleteView.as_view()),
#staff
path("staff/dashboard-overview/", StaffDashboardOverview.as_view(), name="staff-dashboard-overview"),
path("staff-dashboard/", StaffDashboardAnalyticsView.as_view(), name="staff-dashboard"),
path("staff/topic-distribution/", TopicAnalyticsView.as_view()),

#studnet routes
path("student/dashboard/", StudentDashboardView.as_view(), name="student-dashboard"),
]