from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone


class UserModel(AbstractUser):
    STUDENT = 'student'
    TEACHER = 'teacher'
    ADMIN = 'admin'

    ROLE_CHOICES = [
        (STUDENT, 'Student'),
        (TEACHER, 'Teacher'),
        (ADMIN, 'Admin'),
    ]

    email = models.EmailField(unique=True)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default=STUDENT)
    is_verified = models.BooleanField(default=False)
    otp_code = models.CharField(max_length=6, null=True, blank=True)
    otp_created_at = models.DateTimeField(null=True, blank=True)
    reset_token = models.CharField(max_length=100, null=True, blank=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    REQUIRED_FIELDS = ['email', 'role']

    @property
    def is_student(self):
        return self.role == self.STUDENT

    @property
    def is_teacher(self):
        return self.role == self.TEACHER

    @property
    def is_admin_role(self):
        return self.role == self.ADMIN

    def soft_delete(self):
        self.is_active = False
        self.deleted_at = timezone.now()
        self.save()

    def restore(self):
        self.is_active = True
        self.deleted_at = None
        self.save()

    def hard_delete(self):
        super().delete()

    def __str__(self):
        return f'{self.username} [{self.role}]'


class Profile(models.Model):
    ACTIVE = 'active'
    BUSY = 'busy'
    AWAY = 'away'
    OFFLINE = 'offline'

    STATUS_CHOICES = [
        (ACTIVE, 'Active'),
        (BUSY, 'Busy'),
        (AWAY, 'Away'),
        (OFFLINE, 'Offline'),
    ]

    user = models.OneToOneField(UserModel, on_delete=models.CASCADE, related_name='profile')
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
    bio = models.TextField(null=True, blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=OFFLINE)
    phone = models.CharField(max_length=20, null=True, blank=True)
    coins = models.PositiveIntegerField(default=0)
    post_text = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'Profile [{self.user.username}]'


class Notification(models.Model):
    ENROLLMENT_REQUEST = 'enrollment_request'
    ENROLLMENT_INVITE = 'enrollment_invite'
    ENROLLMENT_APPROVED = 'enrollment_approved'
    ENROLLMENT_REJECTED = 'enrollment_rejected'
    COURSE_ADMIN_ASSIGNED = 'course_admin_assigned'
    COURSE_ADMIN_INVITE = 'course_admin_invite'
    
    TYPE_CHOICES = [
        (ENROLLMENT_REQUEST, 'Enrollment Request'),
        (ENROLLMENT_INVITE, 'Enrollment Invite'),
        (ENROLLMENT_APPROVED, 'Enrollment Approved'),
        (ENROLLMENT_REJECTED, 'Enrollment Rejected'),
        (COURSE_ADMIN_ASSIGNED, 'Course Admin Assigned'),
        (COURSE_ADMIN_INVITE, 'Course Admin Invite'),
    ]

    user = models.ForeignKey(UserModel, on_delete=models.CASCADE, related_name='notifications')
    type = models.CharField(max_length=30, choices=TYPE_CHOICES)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Notification [{self.user.username}] - {self.type}'