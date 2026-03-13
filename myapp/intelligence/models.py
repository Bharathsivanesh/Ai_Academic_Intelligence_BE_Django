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

    batch = models.IntegerField()

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

    batch = models.IntegerField()

    class Meta:
        db_table = "batch_staff_mapping"
        unique_together = ("staff", "department", "batch")  #avoid duplicate cobimination of three also be unique rows

    def __str__(self):
        return f"{self.staff} - {self.department} - {self.batch}"

#subject table
class Subject(models.Model):

    subject_name = models.CharField(max_length=150)

    subject_code = models.CharField(max_length=20, unique=True)

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