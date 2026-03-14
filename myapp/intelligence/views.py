from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import status
from rest_framework_simplejwt.views import TokenObtainPairView
from .permissions import IsAdminUserCustom
from .models import *
from .serializers import UserSerializer, MyTokenObtainPairSerializer, StaffCreateSerializer, StaffListSerializer, \
    DepartmentSerializer, BatchStaffMappingSerializer


class RegisterView(generics.CreateAPIView):
    queryset=CustomUser.objects.all()
    serializer_class=UserSerializer
    permission_classes=[permissions.AllowAny]

class LogoutView(APIView):
    def post(self, request):
        try:
            refresh_token = request.data.get("refresh")
            if refresh_token is None:
                return Response({"error": "Refresh token required"}, status=status.HTTP_400_BAD_REQUEST)

            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({"message": "Logout successful"}, status=status.HTTP_205_RESET_CONTENT)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer

class AdminCreateStaffView(generics.CreateAPIView):

    queryset = Staff.objects.all()
    serializer_class = StaffCreateSerializer
    permission_classes = [IsAdminUserCustom]

class AdminStaffListView(generics.ListAPIView):

    queryset = Staff.objects.select_related("user","department").all()
    serializer_class = StaffListSerializer
    permission_classes = [IsAdminUserCustom]

class AdminStaffDetailView(generics.RetrieveAPIView):

    queryset = Staff.objects.select_related("user","department").all()
    serializer_class = StaffListSerializer
    permission_classes = [IsAdminUserCustom]

class AdminStaffUpdateView(generics.UpdateAPIView):

    queryset = Staff.objects.all()
    serializer_class = StaffCreateSerializer
    permission_classes = [IsAdminUserCustom]

class AdminStaffDeleteView(generics.DestroyAPIView):

    queryset = Staff.objects.all()
    permission_classes = [IsAdminUserCustom]

    def destroy(self, request, *args, **kwargs):

        staff = self.get_object()
        user = staff.user

        staff.delete()
        user.delete()

        return Response(
            {"message": "Staff and user deleted successfully"},
            status=status.HTTP_200_OK
        )

class AdminDepartmentListView(generics.ListAPIView):

    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer
    # permission_classes = [IsAdminUserCustom]

class AdminCreateDepartmentView(generics.CreateAPIView):

    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer
    permission_classes = [IsAdminUserCustom]

class AssignStaffToBatchView(generics.CreateAPIView):

    queryset = BatchStaffMapping.objects.all()
    serializer_class = BatchStaffMappingSerializer
    permission_classes = [IsAdminUserCustom]