from django.db import models
from accounts.models import UserModel


class ActivityLog(models.Model):
    LOGIN = 'login'
    LOGOUT = 'logout'
    SUBMITTED_ASSIGNMENT = 'submitted_assignment'
    COMPLETED_QUIZ = 'completed_quiz'
    VIEWED_LESSON = 'viewed_lesson'
    JOINED_COURSE = 'joined_course'
    SENT_MESSAGE = 'sent_message'
    EARNED_COINS = 'earned_coins'

    ACTION_CHOICES = [
        (LOGIN, 'Login'),
        (LOGOUT, 'Logout'),
        (SUBMITTED_ASSIGNMENT, 'Submitted Assignment'),
        (COMPLETED_QUIZ, 'Completed Quiz'),
        (VIEWED_LESSON, 'Viewed Lesson'),
        (JOINED_COURSE, 'Joined Course'),
        (SENT_MESSAGE, 'Sent Message'),
        (EARNED_COINS, 'Earned Coins'),
    ]

    user = models.ForeignKey(UserModel, on_delete=models.CASCADE, related_name='activity_logs')
    action = models.CharField(max_length=30, choices=ACTION_CHOICES)
    description = models.CharField(max_length=300, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.user.username} | {self.action}'


class LessonView(models.Model):
    user = models.ForeignKey(UserModel, on_delete=models.CASCADE, related_name='lesson_views')
    lesson = models.ForeignKey('materials.Lesson', on_delete=models.CASCADE, related_name='views')
    viewed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'lesson')

    def __str__(self):
        return f'{self.user.username} | {self.lesson.title}'


class DailyStreak(models.Model):
    user = models.OneToOneField(UserModel, on_delete=models.CASCADE, related_name='streak')
    current_streak = models.PositiveIntegerField(default=0)
    longest_streak = models.PositiveIntegerField(default=0)
    last_active_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return f'{self.user.username} | streak: {self.current_streak}'