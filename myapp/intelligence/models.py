from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings

class CustomUser(AbstractUser):

    ROLE_CHOICES = (
        ('admin','Admin'),
        ('staff','Staff'),
        ('student','Student')
    )

    role = models.CharField(max_length=20, choices=ROLE_CHOICES)

    def __str__(self):
        return self.username

class Batch(models.Model):

    batch_name = models.CharField(max_length=100)  # Example: "2024-2028"
    batch_code = models.CharField(max_length=20, unique=True)  # Example: B2024
    start_year = models.IntegerField()
    end_year = models.IntegerField()

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "batches"

    def __str__(self):
        return self.batch_name


#Department table
class Department(models.Model):
    department_name = models.CharField(max_length=100)
    department_code = models.CharField(max_length=20)

    def __str__(self):
        return self.department_name


#Staff model

class Staff(models.Model):

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="staff_profile"
    )

    staff_name = models.CharField(max_length=150)

    department = models.ForeignKey(
        Department,
        on_delete=models.SET_NULL,
        null=True,
        related_name="staffs"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "staff"

    def __str__(self):
        return self.staff_name


#Studnet model

class Student(models.Model):

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="student_profile"
    )

    student_name = models.CharField(max_length=150)

    department = models.ForeignKey(
        Department,
        on_delete=models.SET_NULL,
        null=True,
        related_name="students"
    )

    batch = models.ForeignKey(
        Batch,
        on_delete=models.CASCADE,
        related_name="staff_assignments"
    )

    class Meta:
        db_table = "students"

    def __str__(self):
        return self.student_name

#Staff_Batch_Mapping
class BatchStaffMapping(models.Model):

    staff = models.ForeignKey(
        Staff,
        on_delete=models.CASCADE,
        related_name="batch_assignments"
    )

    department = models.ForeignKey(
        Department,
        on_delete=models.CASCADE
    )

    batch = models.ForeignKey(
        Batch,
        on_delete=models.CASCADE,
        related_name="staff_mappings"
    )

    class Meta:
        db_table = "batch_staff_mapping"
        unique_together = ("staff", "department", "batch")  #avoid duplicate cobimination of three also be unique rows

    def __str__(self):
        return f"{self.staff} - {self.department} - {self.batch}"

#subject table
class Subject(models.Model):

    subject_name = models.CharField(max_length=150)

    subject_code = models.CharField(max_length=20)

    department = models.ForeignKey(
        Department,
        on_delete=models.CASCADE,
        related_name="subjects"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "subjects"

    def __str__(self):
        return self.subject_name

#Topics table
class Topic(models.Model):

    subject = models.ForeignKey(
        Subject,
        on_delete=models.CASCADE,
        related_name="topics"
    )

    topic_name = models.CharField(max_length=200)

    topic_description = models.TextField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "topics"

    def __str__(self):
        return self.topic_name


#CoTopic-mapping table
class COTopicMapping(models.Model):

    co_id = models.CharField(max_length=20)  #Many topics can share same CO
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE,null=True)
    topic = models.ForeignKey(
        Topic,
        on_delete=models.CASCADE,
        related_name="co_mappings"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "co_topic_mapping"
        unique_together = ("co_id", "topic")

    def __str__(self):
        return f"{self.co_id} - {self.topic.topic_name}"



#StudentExam table (per exam one row)
class StudentExam(models.Model):

    EXAM_TYPES = (
        ("IAT1", "IAT1"),
        ("IAT2", "IAT2"),
        ("IAT3", "IAT3"),
        ("MODEL", "MODEL"),
        ("SEM", "SEM"),
    )

    exam_type = models.CharField(
        max_length=20,
        choices=EXAM_TYPES
    )

    subject = models.ForeignKey(
        Subject,
        on_delete=models.CASCADE
    )

    department = models.ForeignKey(
        Department,
        on_delete=models.CASCADE
    )
    file_url = models.URLField(null=True,max_length=500,blank=True)  #Co->qn mapping excel

    batch = models.ForeignKey(
        Batch,
        on_delete=models.CASCADE,
        related_name="exams"
    )

    semester = models.IntegerField()

    exam_date = models.DateField()

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "student_exam"

        unique_together = (
            "exam_type",
            "subject",
            "department",
            "batch",
            "semester",
        )

    def __str__(self):
        return f"{self.exam_type} - {self.subject} - Sem {self.semester}"

#Studnetmars table
class StudentMarks(models.Model):

    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE
    )

    exam = models.ForeignKey(
        StudentExam,
        on_delete=models.CASCADE,
        related_name="marks"
    )

    co = models.ForeignKey(
        COTopicMapping,
        on_delete=models.CASCADE
    )

    max_marks = models.IntegerField(default=0)

    obtained_marks = models.IntegerField()

    class Meta:
        db_table = "student_marks"
        unique_together = ("student", "exam", "co")

    def __str__(self):
        return f"{self.student} - {self.co.co_id}"


class StudyPlan(models.Model):

    STATUS_CHOICES = (
        ("active", "Active"),
        ("completed", "Completed"),
    )

    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="study_plans"
    )

    subject = models.ForeignKey(
        "Subject",
        on_delete=models.CASCADE
    )

    plan_name = models.CharField(max_length=200)

    time_horizon_days = models.PositiveIntegerField()  # e.g., 7 days

    daily_hours = models.FloatField()

    overall_progress = models.FloatField(default=0)

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="active"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "study_plan"
        ordering = ["-created_at"]

    def __str__(self):
        return self.plan_name

class StudyPlanDetail(models.Model):

    plan = models.ForeignKey(
        StudyPlan,
        on_delete=models.CASCADE,
        related_name="details"
    )

    day_number = models.PositiveIntegerField()  # Day 1, Day 2...

    topic_name = models.CharField(max_length=200)

    description = models.TextField(blank=True, null=True)

    # ✅ PDF links (your main idea)
    video_links_pdf = models.URLField(blank=True, null=True)
    reference_links_pdf = models.URLField(blank=True, null=True)

    # ✅ progress tracking
    is_completed = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "study_plan_details"
        unique_together = ("plan", "day_number")
        ordering = ["day_number"]

    def __str__(self):
        return f"{self.plan.plan_name} - Day {self.day_number}"
