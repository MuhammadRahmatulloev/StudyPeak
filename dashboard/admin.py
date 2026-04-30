from django.contrib import admin
from .models import ActivityLog, LessonView, DailyStreak


@admin.register(ActivityLog)
class ActivityLogAdmin(admin.ModelAdmin):
    list_display = ('user', 'action', 'description', 'created_at')
    list_filter = ('action',)
    search_fields = ('user__username',)


@admin.register(LessonView)
class LessonViewAdmin(admin.ModelAdmin):
    list_display = ('user', 'lesson', 'viewed_at')
    search_fields = ('user__username', 'lesson__title')


@admin.register(DailyStreak)
class DailyStreakAdmin(admin.ModelAdmin):
    list_display = ('user', 'current_streak', 'longest_streak', 'last_active_date')
    search_fields = ('user__username',)