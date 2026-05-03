from django.db import models
from django.utils import timezone
from accounts.models import UserModel


class Course(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(null=True, blank=True)
    teacher = models.ForeignKey(UserModel, on_delete=models.CASCADE, related_name='courses')
    students = models.ManyToManyField(UserModel, through='Enrollment', related_name='enrolled_courses')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.name} [{self.teacher.username}]'


class CoursePeriod(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='periods')
    name = models.CharField(max_length=100)
    order = models.PositiveIntegerField(default=1)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f'{self.course.name} — {self.name}'


class Enrollment(models.Model):
    PENDING = 'pending'
    APPROVED = 'approved'
    REJECTED = 'rejected'

    STATUS_CHOICES = [
        (PENDING, 'Pending'),
        (APPROVED, 'Approved'),
        (REJECTED, 'Rejected'),
    ]

    STUDENT_REQUEST = 'student_request'
    ADMIN_INVITE = 'admin_invite'

    TYPE_CHOICES = [
        (STUDENT_REQUEST, 'Student Request'),
        (ADMIN_INVITE, 'Admin Invite'),
    ]

    student = models.ForeignKey(UserModel, on_delete=models.CASCADE, related_name='enrollments')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='enrollments')
    type = models.CharField(max_length=20, choices=TYPE_CHOICES, default=STUDENT_REQUEST)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=PENDING)
    enrolled_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('student', 'course')

    def __str__(self):
        return f'{self.student.username} → {self.course.name} [{self.status}]'


class WeeklyJournal(models.Model):
    student = models.ForeignKey(UserModel, on_delete=models.CASCADE, related_name='weekly_journals')
    period = models.ForeignKey(CoursePeriod, on_delete=models.CASCADE, related_name='weekly_journals')
    week_number = models.PositiveIntegerField()
    base_score = models.PositiveIntegerField(default=0)
    bonus_score = models.PositiveIntegerField(default=0)
    teacher_comment = models.TextField(null=True, blank=True)
    coins_awarded = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('student', 'period', 'week_number')

    @property
    def total_score(self):
        return self.base_score + self.bonus_score

    def save(self, *args, **kwargs):
        if self.bonus_score > 10:
            self.bonus_score = 10
        if self.base_score > 100:
            self.base_score = 100
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.student.username} | Week {self.week_number} | {self.total_score}/110'


class Grade(models.Model):
    student = models.ForeignKey(UserModel, on_delete=models.CASCADE, related_name='grades')
    period = models.ForeignKey(CoursePeriod, on_delete=models.CASCADE, related_name='grades')
    title = models.CharField(max_length=200, default='Grade')        
    score = models.PositiveIntegerField(default=0)
    max_score = models.PositiveIntegerField(default=100)
    teacher_comment = models.TextField(null=True, blank=True)
    graded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.student.username} | {self.title} | {self.score}/{self.max_score}'


class Attendance(models.Model):
    PRESENT = 'present'
    ABSENT = 'absent'
    EXCUSED = 'excused'

    STATUS_CHOICES = [
        (PRESENT, 'Present'),
        (ABSENT, 'Absent'),
        (EXCUSED, 'Excused'),
    ]

    student = models.ForeignKey(UserModel, on_delete=models.CASCADE, related_name='attendances')
    period = models.ForeignKey(CoursePeriod, on_delete=models.CASCADE, related_name='attendances')
    date = models.DateField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=PRESENT)

    class Meta:
        unique_together = ('student', 'period', 'date')

    def __str__(self):
        return f'{self.student.username} | {self.date} [{self.status}]'
    

class StudentPeriodSummary(models.Model):
    student = models.ForeignKey(UserModel, on_delete=models.CASCADE, related_name='period_summaries')
    period = models.ForeignKey(CoursePeriod, on_delete=models.CASCADE, related_name='student_summaries')
    bonus_score = models.PositiveIntegerField(default=0)
    exam_score = models.PositiveIntegerField(default=0)
    comment = models.TextField(null=True, blank=True)

    class Meta:
        unique_together = ('student', 'period')

    def __str__(self):
        return f'{self.student.username} | {self.period.name} | exam: {self.exam_score}'