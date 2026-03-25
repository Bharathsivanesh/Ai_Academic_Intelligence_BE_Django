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
    StudentCreateSerializer, StudentListSerializer, StudyPlanSerializer
from django.db.models import Avg, Q
from collections import defaultdict
import pandas as pd
from django.db import transaction,connection
from django.db.models import Max

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
    # permission_classes = [IsAdminUserCustom]

class AdminStudentListView(generics.ListAPIView):
    queryset = Student.objects.select_related("user", "department", "batch")
    serializer_class = StudentListSerializer
    # permission_classes = [IsAdminUserCustom]

class AdminStudentDetailView(generics.RetrieveAPIView):
    queryset = Student.objects.select_related("user", "department", "batch")
    serializer_class = StudentListSerializer
    # permission_classes = [IsAdminUserCustom]

class AdminStudentUpdateView(generics.UpdateAPIView):
    queryset = Student.objects.all()
    serializer_class = StudentCreateSerializer
    # permission_classes = [IsAdminUserCustom]

class AdminStudentDeleteView(generics.DestroyAPIView):
    queryset = Student.objects.all()
    # permission_classes = [IsAdminUserCustom]

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
    # permission_classes = [IsAuthenticated]

    def get(self, request):

        user = request.user

        # -----------------------------
        # 1. Validate student
        # -----------------------------
        if user.role != "student":
            return Response({"error": "Access denied"}, status=403)

        student = getattr(user, "student_profile", None)

        if not student:
            return Response({"error": "Student profile not found"}, status=404)

        # -----------------------------
        # 2. Get latest exam FROM MARKS (FIXED 🔥)
        # -----------------------------
        latest_mark = StudentMarks.objects.filter(
            student=student
        ).select_related("exam").order_by("-exam__exam_date").first()

        if not latest_mark:
            return Response({"error": "No marks data available"}, status=404)

        label_exam = latest_mark.exam

        # -----------------------------
        # 3. Base marks (till latest exam)
        # -----------------------------
        marks = StudentMarks.objects.filter(
            student=student,
            exam__semester__lte=label_exam.semester,
            exam__exam_date__lte=label_exam.exam_date
        )

        # -----------------------------
        # 4. Apply Filters
        # -----------------------------
        semester = request.query_params.get("semester")
        exam_type = request.query_params.get("exam_type")

        if semester:
            marks = marks.filter(exam__semester=semester)

        if exam_type:
            marks = marks.filter(exam__exam_type=exam_type)

        # -----------------------------
        # 5. Overall percentage
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
        # 6. Total subjects
        # -----------------------------
        total_subjects = Subject.objects.filter(
            department=student.department
        ).count()

        # -----------------------------
        # 7. Subject-wise performance
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
        # 8. Semester trend
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
        # 9. Improvement + trend status
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
        # 10. Data scope label (FIXED 🔥)
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
            },
            "filters": {
                "semester": semester,
                "exam_type": exam_type
            }
        })


class CreateStudyPlanView(generics.CreateAPIView):
    queryset = StudyPlan.objects.all()
    serializer_class = StudyPlanSerializer
    # permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(student=self.request.user)

class StudentStudyPlanListView(generics.ListAPIView):
    serializer_class = StudyPlanSerializer
    # permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return StudyPlan.objects.filter(
            student=self.request.user
        ).prefetch_related("details")

class StudyPlanDetailView(generics.RetrieveAPIView):
    queryset = StudyPlan.objects.prefetch_related("details")
    serializer_class = StudyPlanSerializer
    # permission_classes = [IsAuthenticated]


class MarkDayCompleteView(APIView):
    # permission_classes = [IsAuthenticated]

    def post(self, request, pk):

        # pk = StudyPlanDetail id
        try:
            day = StudyPlanDetail.objects.get(
                id=pk,
                plan__student=request.user
            )
        except StudyPlanDetail.DoesNotExist:
            return Response({"error": "Not found"}, status=404)

        # toggle completion
        day.is_completed = True
        day.save()

        # 🔥 update overall progress
        plan = day.plan

        total_days = plan.details.count()
        completed_days = plan.details.filter(is_completed=True).count()

        progress = (completed_days / total_days) * 100
        plan.overall_progress = round(progress, 2)

        # mark completed if 100%
        if progress == 100:
            plan.status = "completed"

        plan.save()

        return Response({
            "message": "Day marked complete",
            "progress": plan.overall_progress
        })

class SubjectIntelligenceView(APIView):

    def get(self, request):

        subject_id = request.GET.get("subject_id")

        if not subject_id:
            return Response({"error": "subject_id required"}, status=400)

        exams = StudentExam.objects.filter(subject_id=subject_id)

        marks = StudentMarks.objects.filter(exam__in=exams).select_related(
            "exam", "co__topic"
        )

        # -----------------------------
        # 1. Overall Subject Performance
        # -----------------------------
        total_obtained = sum(m.obtained_marks for m in marks)
        total_max = sum(m.max_marks for m in marks)

        overall_avg = round((total_obtained / total_max) * 100, 2) if total_max else 0

        # difficulty
        if overall_avg >= 75:
            difficulty = "Easy"
        elif overall_avg >= 60:
            difficulty = "Medium"
        else:
            difficulty = "Hard"

        # -----------------------------
        # 2. Batch-wise Trend
        # -----------------------------
        batch_data = defaultdict(lambda: {"obtained": 0, "max": 0})

        for m in marks:
            batch_name = m.exam.batch.batch_name

            batch_data[batch_name]["obtained"] += m.obtained_marks
            batch_data[batch_name]["max"] += m.max_marks

        batch_trend = []

        for batch, data in batch_data.items():
            avg = (data["obtained"] / data["max"]) * 100 if data["max"] else 0

            batch_trend.append({
                "batch": batch,
                "percentage": round(avg, 2)
            })

        # sort by batch (optional)
        batch_trend = sorted(batch_trend, key=lambda x: x["batch"])

        # -----------------------------
        # 3. Topic-wise Difficulty
        # -----------------------------
        topic_data = defaultdict(lambda: {"obtained": 0, "max": 0})

        for m in marks:
            topic_name = m.co.topic.topic_name

            topic_data[topic_name]["obtained"] += m.obtained_marks
            topic_data[topic_name]["max"] += m.max_marks

        topic_analysis = []

        for topic, data in topic_data.items():
            avg = (data["obtained"] / data["max"]) * 100 if data["max"] else 0

            if avg >= 75:
                level = "Easy"
            elif avg >= 60:
                level = "Medium"
            else:
                level = "Hard"

            topic_analysis.append({
                "topic": topic,
                "percentage": round(avg, 2),
                "difficulty": level
            })

        # -----------------------------
        # FINAL RESPONSE
        # -----------------------------
        return Response({
            "subject_overview": {
                "average_score": overall_avg,
                "difficulty": difficulty
            },
            "batch_trend": batch_trend,
            "topic_analysis": topic_analysis
        })


class BulkStaffUploadView(APIView):

    def reset_sequences(self):
        print("🔄 Resetting sequences...")

        staff_max = Staff.objects.aggregate(max_id=Max("id"))["max_id"] or 0
        user_max = CustomUser.objects.aggregate(max_id=Max("id"))["max_id"] or 0

        print(f"👉 Staff max ID: {staff_max}")
        print(f"👉 User max ID: {user_max}")

        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT setval(pg_get_serial_sequence('staff','id'), %s, true);",
                [staff_max]
            )
            cursor.execute(
                "SELECT setval(pg_get_serial_sequence('intelligence_customuser','id'), %s, true);",
                [user_max]
            )

        print("✅ Sequence reset done")

    def post(self, request):

        print("📥 Bulk upload API called")

        file = request.FILES.get("file")

        if not file:
            return Response({"error": "Excel file is required"}, status=400)

        try:
            df = pd.read_excel(file)
            print("✅ Excel loaded:", df.shape)
        except Exception as e:
            print("❌ Excel error:", str(e))
            return Response({"error": "Invalid Excel file"}, status=400)

        required_columns = ["username", "email", "password", "staff_name", "department"]

        for col in required_columns:
            if col not in df.columns:
                return Response({"error": f"Missing column: {col}"}, status=400)

        errors = []
        success_count = 0

        # ✅ FIX SEQUENCE FIRST
        self.reset_sequences()

        with transaction.atomic():

            for index, row in df.iterrows():
                row_num = index + 2
                print(f"\n🔹 Row {row_num}")

                try:
                    username = str(row["username"]).strip() if pd.notna(row["username"]) else ""
                    email = str(row["email"]).strip() if pd.notna(row["email"]) else ""
                    password = str(row["password"]).strip() if pd.notna(row["password"]) else ""
                    staff_name = str(row["staff_name"]).strip() if pd.notna(row["staff_name"]) else ""
                    department_id = int(row["department"]) if pd.notna(row["department"]) else None

                    # ✅ VALIDATION
                    if not username or not email or not password or not staff_name:
                        errors.append(f"Row {row_num}: Missing required fields")
                        continue

                    if CustomUser.objects.filter(username=username).exists():
                        errors.append(f"Row {row_num}: Username already exists")
                        continue

                    if CustomUser.objects.filter(email=email).exists():
                        errors.append(f"Row {row_num}: Email already exists")
                        continue

                    try:
                        department = Department.objects.get(id=department_id)
                    except Department.DoesNotExist:
                        errors.append(f"Row {row_num}: Invalid department ID")
                        continue

                    # ✅ CREATE USER
                    user = CustomUser.objects.create_user(
                        username=username,
                        email=email,
                        password=password,
                        role="staff"
                    )

                    # ✅ CREATE STAFF
                    Staff.objects.create(
                        user=user,
                        staff_name=staff_name,
                        department=department
                    )

                    print(f"✅ Created: {username}")
                    success_count += 1

                except Exception as e:
                    print("🔥 ERROR:", str(e))
                    errors.append(f"Row {row_num}: {str(e)}")

            # ❌ ROLLBACK IF ANY ERROR
            if errors:
                transaction.set_rollback(True)
                return Response({
                    "status": "failed",
                    "errors": errors
                }, status=400)

        return Response({
            "status": "success",
            "created": success_count
        })