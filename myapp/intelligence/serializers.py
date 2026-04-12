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



class StaffUpdateSerializer(serializers.ModelSerializer):

    username = serializers.CharField(required=False)
    email = serializers.EmailField(required=False)
    password = serializers.CharField(write_only=True, required=False)

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

    # ✅ FIX: username validation for update
    def validate_username(self, value):
        user = self.instance.user if self.instance else None

        if CustomUser.objects.filter(username=value).exclude(id=user.id if user else None).exists():
            raise serializers.ValidationError("Username already exists")

        return value

    # ✅ UPDATE LOGIC
    def update(self, instance, validated_data):
        user = instance.user

        # --- Update CustomUser ---
        if "username" in validated_data:
            user.username = validated_data["username"]

        if "email" in validated_data:
            user.email = validated_data["email"]

        if "password" in validated_data:
            user.set_password(validated_data["password"])

        user.save()

        # --- Update Staff ---
        if "staff_name" in validated_data:
            instance.staff_name = validated_data["staff_name"]

        if "department" in validated_data:
            instance.department = validated_data["department"]

        instance.save()

        return instance

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
            "batch"   # ❌ removed department
        ]

    def validate_username(self, value):
        if CustomUser.objects.filter(username=value).exists():
            raise serializers.ValidationError("Username already exists")
        return value

    def validate_email(self, value):
        if CustomUser.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email already exists")
        return value

    def create(self, validated_data):
        request = self.context.get("request")

        # ✅ get logged-in staff
        user = request.user

        if not hasattr(user, "staff_profile"):
            raise serializers.ValidationError("Only staff can create students")

        staff = user.staff_profile

        try:
            username = validated_data.pop("username")
            email = validated_data.pop("email")
            password = validated_data.pop("password")

            # ✅ create user
            user_obj = CustomUser.objects.create_user(
                username=username,
                email=email,
                password=password,
                role="student"
            )

            # ✅ AUTO ASSIGN DEPARTMENT FROM STAFF
            student = Student.objects.create(
                user=user_obj,
                department=staff.department,   # 🔥 AUTO SET
                **validated_data
            )

            return student

        except Exception as e:
            raise serializers.ValidationError(str(e))

class StudentUpdateSerializer(serializers.ModelSerializer):

    username = serializers.CharField(required=False)
    email = serializers.EmailField(required=False)
    password = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = Student
        fields = [
            "id",
            "username",
            "email",
            "password",
            "student_name",
            "batch"
        ]

    # ✅ Fix username validation (exclude current user)
    def validate_username(self, value):
        if self.instance:
            user = self.instance.user
            if CustomUser.objects.filter(username=value).exclude(id=user.id).exists():
                raise serializers.ValidationError("Username already exists")
        else:
            if CustomUser.objects.filter(username=value).exists():
                raise serializers.ValidationError("Username already exists")

        return value

    # ✅ UPDATE LOGIC
    def update(self, instance, validated_data):
        user = instance.user

        # --- Update CustomUser ---
        if "username" in validated_data:
            user.username = validated_data["username"]

        if "email" in validated_data:
            user.email = validated_data["email"]

        if "password" in validated_data:
            user.set_password(validated_data["password"])

        user.save()

        # --- Update Student ---
        if "student_name" in validated_data:
            instance.student_name = validated_data["student_name"]

        if "department" in validated_data:
            instance.department = validated_data["department"]

        if "batch" in validated_data:
            instance.batch = validated_data["batch"]

        instance.save()

        return instance
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

class StudyPlanDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudyPlanDetail
        fields = "__all__"
        read_only_fields = ["plan"]  # ✅ cleaner

class StudyPlanSerializer(serializers.ModelSerializer):

    details = StudyPlanDetailSerializer(many=True)

    class Meta:
        model = StudyPlan
        fields = "__all__"
        read_only_fields = ["student"]  # ✅ cleaner

    def create(self, validated_data):
        details_data = validated_data.pop("details")

        plan = StudyPlan.objects.create(**validated_data)

        for day in details_data:
            StudyPlanDetail.objects.create(plan=plan, **day)

        return plan

class StudyPlanRequestSerializer(serializers.Serializer):
    subject = serializers.CharField(required=True)
    duration = serializers.IntegerField(required=True)
    dailyHours = serializers.IntegerField(required=True)


class SubjectSerializer(serializers.ModelSerializer):
    department_name = serializers.CharField(
        source="department.department_name",
        read_only=True
    )

    class Meta:
        model = Subject
        fields = [
            "id",
            "subject_name",
            "subject_code",
            "department",
            "department_name"
        ]


class BatchSerializer(serializers.ModelSerializer):
    class Meta:
        model = Batch
        fields = ["id", "batch_name", "batch_code", "start_year", "end_year"]

class BatchCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Batch
        fields = ["id", "batch_name", "batch_code", "start_year", "end_year"]

    def validate(self, data):
        if data["start_year"] >= data["end_year"]:
            raise serializers.ValidationError("start_year must be less than end_year")
        if Batch.objects.filter(batch_code=data["batch_code"]).exists():
            raise serializers.ValidationError("Batch code already exists")
        return data


class StudentExamSerializer(serializers.ModelSerializer):
    subject_name = serializers.CharField(source="subject.subject_name", read_only=True)
    department_name = serializers.CharField(source="department.department_name", read_only=True)
    batch_name = serializers.CharField(source="batch.batch_name", read_only=True)

    class Meta:
        model = StudentExam
        fields = [
            "id",
            "exam_type",
            "subject", "subject_name",
            "department", "department_name",
            "batch", "batch_name",
            "semester",
            "exam_date",
            "file_url",
            "created_at"
        ]

class COTopicSerializer(serializers.ModelSerializer):
    co_id = serializers.CharField(source="co_mappings.first.co_id", read_only=True)

    class Meta:
        model = Topic
        fields = ["id", "topic_name", "topic_description"]

class TopicWithCOSerializer(serializers.ModelSerializer):
    co_ids = serializers.SerializerMethodField()

    class Meta:
        model = Topic
        fields = ["id", "topic_name", "topic_description", "co_ids"]

    def get_co_ids(self, obj):
        # co_mappings is the related_name from COTopicMapping -> Topic
        return list(obj.co_mappings.values_list("co_id", flat=True))

class SubjectWithTopicsSerializer(serializers.ModelSerializer):
    topics = TopicWithCOSerializer(many=True, read_only=True)

    class Meta:
        model = Subject
        fields = ["id", "subject_name", "subject_code", "topics"]