from django.contrib import admin
from .models import Course, CoursePeriod, Enrollment, WeeklyJournal, Grade, Attendance


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('name', 'teacher', 'is_active', 'created_at')
    list_filter = ('is_active',)
    search_fields = ('name', 'teacher__username')


@admin.register(CoursePeriod)
class CoursePeriodAdmin(admin.ModelAdmin):
    list_display = ('name', 'course', 'order', 'start_date', 'end_date')
    search_fields = ('name', 'course__name')


@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ('student', 'course', 'type', 'status', 'enrolled_at')
    list_filter = ('type', 'status')
    search_fields = ('student__username', 'course__name')


@admin.register(WeeklyJournal)
class WeeklyJournalAdmin(admin.ModelAdmin):
    list_display = ('student', 'period', 'week_number', 'base_score', 'bonus_score', 'coins_awarded')
    list_filter = ('coins_awarded',)
    search_fields = ('student__username',)


@admin.register(Grade)
class GradeAdmin(admin.ModelAdmin):
    list_display = ('student', 'period', 'score', 'graded_at')
    search_fields = ('student__username',)


@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ('student', 'period', 'date', 'status')
    list_filter = ('status',)
    search_fields = ('student__username',)