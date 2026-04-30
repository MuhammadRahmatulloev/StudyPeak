from django.contrib import admin
from .models import NewsFeed


@admin.register(NewsFeed)
class NewsFeedAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'type', 'is_active', 'created_at')
    list_filter = ('type', 'is_active')
    search_fields = ('title', 'author__username')