from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth import get_user_model
from django.contrib.auth import authenticate
from .models import *
User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password', 'role']

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            role=validated_data.get('role')
        )
        return user


class MyTokenObtainPairSerializer(TokenObtainPairSerializer):

    username_field = 'email'   # IMPORTANT
    email = serializers.EmailField()

    def validate(self, attrs):

        email = attrs.get("email")
        password = attrs.get("password")

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise serializers.ValidationError({
                "email": "Invalid email or password"
            })

        user = authenticate(username=user.username, password=password)

        if user is None:
            raise serializers.ValidationError("Invalid email or password")

        refresh = self.get_token(user)

        return {
            "refresh": str(refresh),
            "access": str(refresh.access_token),
            "email": user.email,
            "username": user.username,
            "role": user.role
        }





class StaffCreateSerializer(serializers.ModelSerializer):

    username = serializers.CharField(write_only=True)
    email = serializers.EmailField(write_only=True)
    password = serializers.CharField(write_only=True)

    class Meta:
        model = Staff
        fields = [
            "id",
            "username",
            "email",
            "password",
            "staff_name",
            "department"
        ]

    def validate_username(self, value):

        if CustomUser.objects.filter(username=value).exists():
            raise serializers.ValidationError("Username already exists")

        return value

    def create(self, validated_data):

        username = validated_data.pop("username")
        email = validated_data.pop("email")
        password = validated_data.pop("password")

        user = CustomUser.objects.create_user(
            username=username,
            email=email,
            password=password,
            role="staff"
        )

        staff = Staff.objects.create(
            user=user,
            **validated_data
        )

        return staff


class StaffListSerializer(serializers.ModelSerializer):

    email = serializers.CharField(source="user.email")
    username = serializers.CharField(source="user.username")

    class Meta:
        model = Staff
        fields = [
            "id",
            "staff_name",
            "username",
            "email",
            "department"
        ]

from rest_framework import serializers
from .models import Department


class DepartmentSerializer(serializers.ModelSerializer):

    class Meta:
        model = Department
        fields = ["id", "department_name", "department_code"]

class BatchStaffMappingSerializer(serializers.ModelSerializer):

    class Meta:
        model = BatchStaffMapping
        fields = ["id", "staff", "department", "batch"]