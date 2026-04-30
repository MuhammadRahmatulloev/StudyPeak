from django.db import models
from django.utils import timezone
from accounts.models import UserModel


class Assignment(models.Model):
    HOMEWORK = 'homework'
    TEST = 'test'
    QUIZ = 'quiz'

    TYPE_CHOICES = [
        (HOMEWORK, 'Homework'),
        (TEST, 'Test'),
        (QUIZ, 'Quiz'),
    ]

    title = models.CharField(max_length=200)
    description = models.TextField(null=True, blank=True)
    teacher = models.ForeignKey(UserModel, on_delete=models.CASCADE, related_name='assignments')
    subject = models.ForeignKey('materials.Subject', on_delete=models.CASCADE, related_name='assignments')
    group = models.ForeignKey('chat.Group', on_delete=models.CASCADE, related_name='assignments')
    type = models.CharField(max_length=10, choices=TYPE_CHOICES, default=HOMEWORK)
    deadline = models.DateTimeField(null=True, blank=True)
    time_limit = models.PositiveIntegerField(null=True, blank=True, help_text='Quiz time limit in minutes')
    is_published = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.title} [{self.type}]'


class Question(models.Model):
    MCQ = 'mcq'
    TEXT = 'text'
    TRUE_FALSE = 'true_false'

    TYPE_CHOICES = [
        (MCQ, 'Multiple Choice'),
        (TEXT, 'Text Answer'),
        (TRUE_FALSE, 'True / False'),
    ]

    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE, related_name='questions')
    text = models.TextField()
    type = models.CharField(max_length=10, choices=TYPE_CHOICES, default=MCQ)
    order = models.PositiveIntegerField(default=0)
    score = models.PositiveIntegerField(default=1)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f'Q{self.order}: {self.text[:50]} [{self.type}]'


class Choice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='choices')
    text = models.CharField(max_length=300)
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.text} [{"✓" if self.is_correct else "✗"}]'


class AssignmentSubmission(models.Model):
    PENDING = 'pending'
    SUBMITTED = 'submitted'
    GRADED = 'graded'

    STATUS_CHOICES = [
        (PENDING, 'Pending'),
        (SUBMITTED, 'Submitted'),
        (GRADED, 'Graded'),
    ]

    student = models.ForeignKey(UserModel, on_delete=models.CASCADE, related_name='submissions')
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE, related_name='submissions')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=PENDING)
    total_score = models.PositiveIntegerField(default=0)
    started_at = models.DateTimeField(null=True, blank=True)
    submitted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ('student', 'assignment')

    def submit(self):
        self.status = self.SUBMITTED
        self.submitted_at = timezone.now()
        self.save()

    def __str__(self):
        return f'{self.student.username} → {self.assignment.title} [{self.status}]'


class Answer(models.Model):
    submission = models.ForeignKey(AssignmentSubmission, on_delete=models.CASCADE, related_name='answers')
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='answers')
    selected_choice = models.ForeignKey(Choice, on_delete=models.SET_NULL, null=True, blank=True, related_name='answers')
    answer_text = models.TextField(null=True, blank=True)
    is_correct = models.BooleanField(null=True, blank=True)
    score = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f'Answer [{self.submission.student.username}] → Q:{self.question.pk}'