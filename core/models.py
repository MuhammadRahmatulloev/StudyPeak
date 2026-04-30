from django.db import models
from accounts.models import UserModel


class NewsFeed(models.Model):
    IMAGE = 'image'
    TEXT = 'text'
    AD = 'ad'

    TYPE_CHOICES = [
        (IMAGE, 'Image'),
        (TEXT, 'Text'),
        (AD, 'Advertisement'),
    ]

    author = models.ForeignKey(UserModel, on_delete=models.CASCADE, related_name='news_posts')
    title = models.CharField(max_length=200)
    content = models.TextField()
    image = models.ImageField(upload_to='news/', null=True, blank=True)
    type = models.CharField(max_length=10, choices=TYPE_CHOICES, default=TEXT)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.title} [{self.type}]'