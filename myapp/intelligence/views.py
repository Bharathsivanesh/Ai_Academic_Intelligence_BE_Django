from django.db.models import Prefetch
from django.db.models.aggregates import Sum
from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import status
from rest_framework_simplejwt.views import TokenObtainPairView
from .permissions import IsAdminUserCustom
from .models import *
from .serializers import UserSerializer, MyTokenObtainPairSerializer, StaffCreateSerializer, StaffListSerializer, \
    DepartmentSerializer, BatchStaffMappingSerializer, BatchSerializer, SubjectSerializer, StudentExamCreateSerializer, \
    StudentCreateSerializer, StudentListSerializer
from django.db.models import Avg, Q

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

    queryset = Staff.objects.select_related(
        "user", "department"
    ).prefetch_related(
        Prefetch("batch_assignments", queryset=BatchStaffMapping.objects.select_related("batch"))
    )

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

class BatchListView(generics.ListAPIView):

    queryset = Batch.objects.all()
    serializer_class = BatchSerializer

class SubjectByDepartmentView(generics.ListAPIView):
    serializer_class = SubjectSerializer

    def get_queryset(self):
        department_id = self.kwargs["department_id"]
        return Subject.objects.filter(department_id=department_id)

class AdminCreateExamView(generics.CreateAPIView):

    queryset = StudentExam.objects.all()
    serializer_class = StudentExamCreateSerializer
    permission_classes = [IsAdminUserCustom]

class AdminDashboardStatsView(APIView):

    permission_classes = [IsAdminUserCustom]  # or IsAdminUserCustom

    def get(self, request):

        total_staff = Staff.objects.count()

        total_students = Student.objects.count()

        total_subjects = Subject.objects.count()

        data = {
            "total_staff": total_staff,
            "total_students": total_students,
            "total_subjects": total_subjects
        }

        return Response(data)


class StaffCreateStudentView(generics.CreateAPIView):

    queryset = Student.objects.all()
    serializer_class = StudentCreateSerializer
    permission_classes = [IsAdminUserCustom]

class AdminStudentListView(generics.ListAPIView):
    queryset = Student.objects.select_related("user", "department", "batch")
    serializer_class = StudentListSerializer
    permission_classes = [IsAdminUserCustom]

class AdminStudentDetailView(generics.RetrieveAPIView):
    queryset = Student.objects.select_related("user", "department", "batch")
    serializer_class = StudentListSerializer
    permission_classes = [IsAdminUserCustom]

class AdminStudentUpdateView(generics.UpdateAPIView):
    queryset = Student.objects.all()
    serializer_class = StudentCreateSerializer
    permission_classes = [IsAdminUserCustom]

class AdminStudentDeleteView(generics.DestroyAPIView):
    queryset = Student.objects.all()
    permission_classes = [IsAdminUserCustom]

    def destroy(self, request, *args, **kwargs):
        student = self.get_object()
        user = student.user

        student.delete()
        user.delete()

        return Response(
            {"message": "Student and user deleted successfully"},
            status=status.HTTP_200_OK
        )


class StaffDashboardAnalyticsView(APIView):

    # permission_classes = [IsAuthenticated]

    def get(self, request):

        user = request.user

        # ✅ Step 1: Check staff
        if not hasattr(user, "staff_profile"):
            return Response({"error": "Not a staff user"}, status=403)

        staff = user.staff_profile

        # ✅ Step 2: Get mapping
        mappings = BatchStaffMapping.objects.filter(staff=staff)

        batch_ids = mappings.values_list("batch_id", flat=True)
        department_ids = mappings.values_list("department_id", flat=True)

        # ✅ Step 3: Base queryset (SECURITY FILTER)
        queryset = StudentMarks.objects.filter(
            exam__batch_id__in=batch_ids,
            exam__department_id__in=department_ids
        ).select_related("student", "exam", "co")

        # ✅ Step 4: Filters (LEFT → RIGHT)
        batch_id = request.query_params.get("batch")
        semester = request.query_params.get("semester")
        subject_id = request.query_params.get("subject")
        topic_id = request.query_params.get("topic")
        exam_type = request.query_params.get("exam_type")

        if batch_id:
            queryset = queryset.filter(exam__batch_id=batch_id)

        if semester:
            queryset = queryset.filter(exam__semester=semester)

        if subject_id:
            queryset = queryset.filter(exam__subject_id=subject_id)

        if topic_id:
            queryset = queryset.filter(co__topic_id=topic_id)

        if exam_type:
            queryset = queryset.filter(exam__exam_type=exam_type)

        # ✅ Step 5: Dynamic grouping
        group_fields = ["student__id", "student__student_name"]

        # 👉 Only group by exam if explicitly filtering by exam_type
        if exam_type:
            group_fields.append("exam__exam_type")

        student_data = queryset.values(*group_fields).annotate(
            total_obtained=Sum("obtained_marks"),
            total_max=Sum("max_marks")
        )

        # ✅ Step 6: Convert to percentage
        high_performers = []
        low_performers = []

        for s in student_data:
            total_obtained = s["total_obtained"] or 0
            total_max = s["total_max"] or 1  # avoid division error

            percentage = (total_obtained / total_max) * 100

            data = {
                "student_id": s["student__id"],
                "name": s["student__student_name"],
                "percentage": round(percentage, 2)
            }

            # optional: include exam_type if present
            if "exam__exam_type" in s:
                data["exam_type"] = s["exam__exam_type"]

            if percentage >= 65:
                high_performers.append(data)
            elif percentage <=64:
                low_performers.append(data)

        # ✅ Step 7: Sort
        high_performers = sorted(high_performers, key=lambda x: -x["percentage"])
        low_performers = sorted(low_performers, key=lambda x: x["percentage"])

        # ✅ Step 8: Total unique students
        total_students = queryset.values("student").distinct().count()

        return Response({
            "total_students": total_students,
            "high_performers": high_performers[:10],
            "underperformers": low_performers[:10]
        })


class StaffDashboardOverview(APIView):

    # permission_classes = [IsAuthenticated]

    def get(self, request):

        user = request.user

        # ✅ Staff check
        if not hasattr(user, "staff_profile"):
            return Response({"error": "Not staff"}, status=403)

        staff = user.staff_profile

        # ✅ Mapping restriction
        mappings = BatchStaffMapping.objects.filter(staff=staff)
        batch_ids = mappings.values_list("batch_id", flat=True)
        dept_ids = mappings.values_list("department_id", flat=True)

        # ✅ Input (ONLY batch)
        batch_id = request.query_params.get("batch")

        if not batch_id:
            return Response({"error": "Batch is required"}, status=400)

        if int(batch_id) not in batch_ids:
            return Response({"error": "Unauthorized batch"}, status=403)

        # ✅ Base queryset
        queryset = StudentMarks.objects.filter(
            exam__batch_id=batch_id,
            exam__department_id__in=dept_ids
        )

        # =========================
        # 🎯 1. STUDENT PERFORMANCE
        # =========================
        student_qs = queryset.values("student").annotate(
            total_obtained=Sum("obtained_marks"),
            total_max=Sum("max_marks")
        )

        total_students = student_qs.count()

        percentages = []
        pass_count = 0
        risk_count = 0

        for s in student_qs:
            percent = (s["total_obtained"] / s["total_max"]) * 100
            percentages.append(percent)

            if percent >= 60:
                pass_count += 1
            else:
                risk_count += 1

        overall_performance = sum(percentages) / total_students if total_students else 0
        pass_percentage = (pass_count / total_students * 100) if total_students else 0

        # =========================
        # 📊 2. TREND (ORDERED)
        # =========================
        trend_qs = queryset.values(
            "exam__semester",
            "exam__exam_type"
        ).annotate(
            total_obtained=Sum("obtained_marks"),
            total_max=Sum("max_marks")
        )

        # 🎯 Custom order
        exam_order = {
            "IAT1": 1,
            "IAT2": 2,
            "SEM": 3
        }

        trend_list = []

        for t in trend_qs:
            percent = (t["total_obtained"] / t["total_max"]) * 100

            trend_list.append({
                "semester": t["exam__semester"],
                "exam_type": t["exam__exam_type"],
                "order": exam_order.get(t["exam__exam_type"], 99),
                "value": round(percent, 2)
            })

        # 🔥 SORT: semester first, then exam type
        trend_list = sorted(
            trend_list,
            key=lambda x: (x["semester"], x["order"])
        )

        # 🔥 Final format for UI
        trend = [
            {
                "label": f"{t['exam_type']} (Sem {t['semester']})",
                "value": t["value"]
            }
            for t in trend_list
        ]

        # =========================
        # 📊 3. SUBJECT PROFICIENCY
        # =========================
        subject_qs = queryset.values(
            "exam__subject__subject_name"
        ).annotate(
            total_obtained=Sum("obtained_marks"),
            total_max=Sum("max_marks")
        )

        subjects = []

        for s in subject_qs:
            percent = (s["total_obtained"] / s["total_max"]) * 100

            subjects.append({
                "subject": s["exam__subject__subject_name"],
                "percentage": round(percent, 2)
            })

        # =========================
        # 🚀 FINAL RESPONSE
        # =========================
        return Response({
            "summary": {
                "total_students": total_students,
                "overall_performance": round(overall_performance, 2),
                "pass_percentage": round(pass_percentage, 2),
                "students_at_risk": risk_count
            },
            "trend": trend,
            "subjects": subjects
        })

class TopicProficiencyDistributionView(APIView):

    def get(self, request):

        batch_id = request.query_params.get("batch")
        subject_id = request.query_params.get("subject")

        if not batch_id or not subject_id:
            return Response({"error": "batch and subject are required"}, status=400)

        user = request.user

        # ✅ STAFF VALIDATION
        if not hasattr(user, "staff_profile"):
            return Response({"error": "Not a staff user"}, status=403)

        staff = user.staff_profile

        # ✅ GET ALLOWED MAPPINGS
        mappings = BatchStaffMapping.objects.filter(staff=staff)
        batch_ids = mappings.values_list("batch_id", flat=True)
        dept_ids = mappings.values_list("department_id", flat=True)

        # ✅ SECURITY FILTER
        queryset = StudentMarks.objects.filter(
            exam__batch_id__in=batch_ids,
            exam__department_id__in=dept_ids,
            exam__batch_id=batch_id,
            exam__subject_id=subject_id
        )

        # ✅ AGGREGATE PER STUDENT PER TOPIC
        topic_data = queryset.values(
            "co__topic__id",
            "co__topic__topic_name",
            "student__id"
        ).annotate(
            total_obtained=Sum("obtained_marks"),
            total_max=Sum("max_marks")
        )

        # ✅ DISTRIBUTION STRUCTURE
        topic_distribution = {}

        for row in topic_data:
            topic_id = row["co__topic__id"]
            topic_name = row["co__topic__topic_name"]

            if topic_id not in topic_distribution:
                topic_distribution[topic_id] = {
                    "topic": topic_name,
                    "exceeding": 0,
                    "meeting": 0,
                    "developing": 0,
                    "below": 0
                }

            obtained = row["total_obtained"] or 0
            max_marks = row["total_max"] or 1

            percentage = (obtained / max_marks) * 100

            # ✅ CATEGORY
            if percentage >= 75:
                topic_distribution[topic_id]["exceeding"] += 1
            elif percentage >= 50:
                topic_distribution[topic_id]["meeting"] += 1
            elif percentage >= 35:
                topic_distribution[topic_id]["developing"] += 1
            else:
                topic_distribution[topic_id]["below"] += 1

        return Response({
            "topics": list(topic_distribution.values())
        })


class TopicAnalyticsView(APIView):

    def get(self, request):

        user = request.user

        # ✅ 1. Staff validation
        if not hasattr(user, "staff_profile"):
            return Response({"error": "Not a staff user"}, status=403)

        staff = user.staff_profile

        # ✅ 2. Staff mappings
        mappings = BatchStaffMapping.objects.filter(staff=staff)

        batch_ids = list(mappings.values_list("batch_id", flat=True))
        dept_ids = list(mappings.values_list("department_id", flat=True))

        # ✅ 3. Params
        batch_id = request.query_params.get("batch")
        subject_id = request.query_params.get("subject")

        if not batch_id or not subject_id:
            return Response(
                {"error": "batch and subject are required"},
                status=400
            )

        # ✅ 4. Validate subject
        if not Subject.objects.filter(id=subject_id).exists():
            return Response({"error": "Invalid subject id"}, status=400)

        # ✅ 5. Base queryset
        queryset = StudentMarks.objects.filter(
            exam__batch_id__in=batch_ids,
            exam__department_id__in=dept_ids,
            exam__batch_id=batch_id,
            exam__subject_id=subject_id,
            co__topic__subject_id=subject_id
        ).select_related(
            "student",
            "co__topic",
            "exam"
        )

        if not queryset.exists():
            return Response(
                {"error": "No marks found"},
                status=400
            )

        # ✅ 6. Student + Topic aggregation
        student_topic_data = queryset.values(
            "student_id",
            "co__topic__id",
            "co__topic__topic_name"
        ).annotate(
            total_obtained=Sum("obtained_marks"),
            total_max=Sum("max_marks")
        )

        # ✅ 7. Build distribution
        topic_map = {}

        for row in student_topic_data:
            topic_id = row["co__topic__id"]
            topic_name = row["co__topic__topic_name"]

            percent = 0
            if row["total_max"] > 0:
                percent = (row["total_obtained"] / row["total_max"]) * 100

            # classify level
            if percent >= 75:
                level = "Exceeding"
            elif percent >= 60:
                level = "Meeting"
            elif percent >= 40:
                level = "Developing"
            else:
                level = "Below"

            if topic_id not in topic_map:
                topic_map[topic_id] = {
                    "topic": topic_name,
                    "Exceeding": 0,
                    "Meeting": 0,
                    "Developing": 0,
                    "Below": 0,
                }

            topic_map[topic_id][level] += 1

        # ✅ 8. Convert to percentage (ONLY topics with marks)
        topic_distribution = []

        for data in topic_map.values():
            total = (
                data["Exceeding"] +
                data["Meeting"] +
                data["Developing"] +
                data["Below"]
            )

            topic_distribution.append({
                "topic": data["topic"],
                "Exceeding": round((data["Exceeding"] / total) * 100, 2),
                "Meeting": round((data["Meeting"] / total) * 100, 2),
                "Developing": round((data["Developing"] / total) * 100, 2),
                "Below": round((data["Below"] / total) * 100, 2),
            })

        # ✅ 9. Total students
        total_students = queryset.values("student_id").distinct().count()

        # ✅ 10. Response
        return Response({
            "total_students": total_students,
            "topic_distribution": topic_distribution
        })


class StudentDashboardView(APIView):


    def get(self, request):

        user = request.user

        # -----------------------------
        # Validate student
        # -----------------------------
        if user.role != "student":
            return Response({"error": "Access denied"}, status=403)

        student = getattr(user, "student_profile", None)

        if not student:
            return Response({"error": "Student profile not found"}, status=404)

        # -----------------------------
        # 1. Get latest semester
        # -----------------------------
        latest_semester = StudentExam.objects.filter(
            batch=student.batch,
            department=student.department
        ).order_by("-semester").values_list("semester", flat=True).first()

        if not latest_semester:
            return Response({"error": "No exam data available"}, status=404)

        # -----------------------------
        # 2. Prefer SEM exam
        # -----------------------------
        latest_sem_exam = StudentExam.objects.filter(
            batch=student.batch,
            department=student.department,
            semester=latest_semester,
            exam_type="SEM"
        ).order_by("-exam_date").first()

        if latest_sem_exam:
            label_exam = latest_sem_exam
        else:
            label_exam = StudentExam.objects.filter(
                batch=student.batch,
                department=student.department,
                semester=latest_semester
            ).order_by("-exam_date").first()

        # -----------------------------
        # 3. Filter marks till latest exam
        # -----------------------------
        marks = StudentMarks.objects.filter(
            student=student,
            exam__semester__lte=label_exam.semester,
            exam__exam_date__lte=label_exam.exam_date
        )

        # -----------------------------
        # 4. Overall percentage
        # -----------------------------
        total_obtained = marks.aggregate(total=Sum("obtained_marks"))["total"] or 0
        total_max = marks.aggregate(total=Sum("max_marks"))["total"] or 1

        overall_percentage = round((total_obtained / total_max) * 100, 2)

        # Grade & Risk
        if overall_percentage >= 85:
            grade = "A+"
            risk = "Low"
        elif overall_percentage >= 70:
            grade = "A"
            risk = "Medium"
        else:
            grade = "B"
            risk = "High"

        # -----------------------------
        # 5. Total subjects
        # -----------------------------
        total_subjects = Subject.objects.filter(
            department=student.department
        ).count()

        # -----------------------------
        # 6. Subject-wise performance
        # -----------------------------
        subjects_data = []

        subjects = Subject.objects.filter(department=student.department)

        for subject in subjects:
            subject_marks = marks.filter(exam__subject=subject)

            sub_total = subject_marks.aggregate(total=Sum("obtained_marks"))["total"] or 0
            sub_max = subject_marks.aggregate(total=Sum("max_marks"))["total"] or 1

            percentage = round((sub_total / sub_max) * 100, 2)

            subjects_data.append({
                "subject_name": subject.subject_name,
                "subject_code": subject.subject_code,
                "percentage": percentage
            })

        # -----------------------------
        # 7. Semester trend
        # -----------------------------
        trend = []

        semesters = marks.values_list("exam__semester", flat=True).distinct()

        for sem in sorted(semesters):
            sem_marks = marks.filter(exam__semester=sem)

            sem_total = sem_marks.aggregate(total=Sum("obtained_marks"))["total"] or 0
            sem_max = sem_marks.aggregate(total=Sum("max_marks"))["total"] or 1

            sem_percentage = round((sem_total / sem_max) * 100, 2)

            trend.append({
                "semester": sem,
                "percentage": sem_percentage
            })

        # -----------------------------
        # 8. Improvement + status
        # -----------------------------
        improvement = 0
        trend_status = "same"

        if len(trend) >= 2:
            trend_sorted = sorted(trend, key=lambda x: x["semester"])

            last_sem = trend_sorted[-1]["percentage"]
            prev_sem = trend_sorted[-2]["percentage"]

            improvement = round(last_sem - prev_sem, 2)

            if improvement > 0:
                trend_status = "up"
            elif improvement < 0:
                trend_status = "down"

        # -----------------------------
        # 9. Data scope label
        # -----------------------------
        scope_label = f"Till Semester {label_exam.semester} ({label_exam.exam_type})"

        # -----------------------------
        # FINAL RESPONSE
        # -----------------------------
        return Response({
            "overall": {
                "percentage": overall_percentage,
                "grade": grade,
                "risk_level": risk,
                "total_subjects": total_subjects
            },
            "subjects": subjects_data,
            "trend": trend,
            "improvement": improvement,
            "trend_status": trend_status,
            "data_scope": {
                "label": scope_label,
                "semester": label_exam.semester,
                "exam_type": label_exam.exam_type
            }
        })