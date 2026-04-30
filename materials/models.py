from django.db import models
from accounts.models import UserModel


class Subject(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(null=True, blank=True)
    teacher = models.ForeignKey(UserModel, on_delete=models.CASCADE, related_name='subjects')
    group = models.ForeignKey('chat.Group', on_delete=models.SET_NULL, null=True, blank=True, related_name='subjects')
    cover = models.ImageField(upload_to='subject_covers/', null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.title} [{self.teacher.username}]'


class Lesson(models.Model):
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='lessons')
    title = models.CharField(max_length=200)
    description = models.TextField(null=True, blank=True)
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f'{self.subject.title} | {self.order}. {self.title}'


class Material(models.Model):
    PDF = 'pdf'
    LINK = 'link'
    TEXT = 'text'
    IMAGE = 'image'
    VIDEO = 'video'

    TYPE_CHOICES = [
        (PDF, 'PDF'),
        (LINK, 'Link'),
        (TEXT, 'Text'),
        (IMAGE, 'Image'),
        (VIDEO, 'Video'),
    ]

    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name='materials')
    title = models.CharField(max_length=200)
    type = models.CharField(max_length=10, choices=TYPE_CHOICES)
    file = models.FileField(upload_to='materials/files/', null=True, blank=True)
    url = models.URLField(null=True, blank=True)
    content = models.TextField(null=True, blank=True)
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f'{self.title} [{self.type}]'