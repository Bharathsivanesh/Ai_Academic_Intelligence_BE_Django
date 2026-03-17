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


class BatchSimpleSerializer(serializers.ModelSerializer):

    class Meta:
        model = Batch
        fields = ["id", "batch_name"]

class StaffListSerializer(serializers.ModelSerializer):

    email = serializers.CharField(source="user.email")
    username = serializers.CharField(source="user.username")

    batches = serializers.SerializerMethodField()

    class Meta:
        model = Staff
        fields = [
            "id",
            "staff_name",
            "username",
            "email",
            "department",
            "batches"
        ]

    def get_batches(self, obj):
        return [
            {
                "id": mapping.batch.id,
                "batch_name": mapping.batch.batch_name
            }
            for mapping in obj.batch_assignments.all()
        ]


class DepartmentSerializer(serializers.ModelSerializer):

    class Meta:
        model = Department
        fields = ["id", "department_name", "department_code"]

class BatchStaffMappingSerializer(serializers.ModelSerializer):

    class Meta:
        model = BatchStaffMapping
        fields = ["id", "staff", "department", "batch"]

class BatchSerializer(serializers.ModelSerializer):

    class Meta:
        model = Batch
        fields = "__all__"


class SubjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subject
        fields = ["id", "subject_name", "subject_code"]

class StudentExamCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = StudentExam
        fields = [
            "exam_type",
            "subject",
            "department",
            "batch",
            "semester",
            "exam_date",
            "file_url"
        ]


class StudentCreateSerializer(serializers.ModelSerializer):

    username = serializers.CharField(write_only=True)
    email = serializers.EmailField(write_only=True)
    password = serializers.CharField(write_only=True)

    class Meta:
        model = Student
        fields = [
            "id",
            "username",
            "email",
            "password",
            "student_name",
            "department",
            "batch"
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
            role="student"
        )

        student = Student.objects.create(
            user=user,
            **validated_data
        )

        return student

class StudentListSerializer(serializers.ModelSerializer):

    email = serializers.CharField(source="user.email")
    username = serializers.CharField(source="user.username")

    class Meta:
        model = Student
        fields = [
            "id",
            "student_name",
            "username",
            "email",
            "department",
            "batch"
        ]