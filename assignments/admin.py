from django.contrib import admin
from .models import Assignment, Question, Choice, AssignmentSubmission, Answer


@admin.register(Assignment)
class AssignmentAdmin(admin.ModelAdmin):
    list_display = ('title', 'teacher', 'subject', 'group', 'type', 'is_published', 'deadline')
    list_filter = ('type', 'is_published')
    search_fields = ('title', 'teacher__username')


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('assignment', 'text', 'type', 'order', 'score')
    list_filter = ('type',)
    search_fields = ('text', 'assignment__title')


@admin.register(Choice)
class ChoiceAdmin(admin.ModelAdmin):
    list_display = ('question', 'text', 'is_correct')
    list_filter = ('is_correct',)
    search_fields = ('text',)


@admin.register(AssignmentSubmission)
class AssignmentSubmissionAdmin(admin.ModelAdmin):
    list_display = ('student', 'assignment', 'status', 'total_score', 'submitted_at')
    list_filter = ('status',)
    search_fields = ('student__username', 'assignment__title')


@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    list_display = ('submission', 'question', 'is_correct', 'score')
    list_filter = ('is_correct',)