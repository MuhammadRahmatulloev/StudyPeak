from django.db import models
from accounts.models import UserModel


class AIRequest(models.Model):
    MATERIAL = 'material'
    ASSIGNMENT = 'assignment'
    GENERAL = 'general'

    CONTEXT_CHOICES = [
        (MATERIAL, 'Material'),
        (ASSIGNMENT, 'Assignment'),
        (GENERAL, 'General'),
    ]

    user = models.ForeignKey(UserModel, on_delete=models.CASCADE, related_name='ai_requests')
    question = models.TextField()
    response = models.TextField(null=True, blank=True)
    context = models.CharField(max_length=15, choices=CONTEXT_CHOICES, default=GENERAL)
    lesson = models.ForeignKey('materials.Lesson', on_delete=models.SET_NULL, null=True, blank=True, related_name='ai_requests')
    assignment = models.ForeignKey('assignments.Assignment', on_delete=models.SET_NULL, null=True, blank=True, related_name='ai_requests')
    is_blocked = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.user.username} | {self.context} | {self.created_at}'


class AIUsageLimit(models.Model):
    user = models.OneToOneField(UserModel, on_delete=models.CASCADE, related_name='ai_limit')
    daily_count = models.PositiveIntegerField(default=0)
    last_reset_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return f'{self.user.username} | {self.daily_count} requests today'