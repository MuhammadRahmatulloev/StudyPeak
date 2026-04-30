from django.contrib import admin
from .models import Subject, Lesson, Material


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ('title', 'teacher', 'group', 'is_active', 'created_at')
    list_filter = ('is_active',)
    search_fields = ('title', 'teacher__username')


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ('title', 'subject', 'order', 'created_at')
    list_filter = ('subject',)
    search_fields = ('title', 'subject__title')
    ordering = ('subject', 'order')


@admin.register(Material)
class MaterialAdmin(admin.ModelAdmin):
    list_display = ('title', 'lesson', 'type', 'order', 'created_at')
    list_filter = ('type',)
    search_fields = ('title', 'lesson__title')