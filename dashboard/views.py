from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import View
from django.contrib import messages
from django.utils import timezone
from django.db.models import Count, Sum, Avg
from datetime import date, timedelta
from accounts.permissions import SessionLoginRequiredMixin, AdminRequiredMixin, get_current_user
from accounts.models import UserModel, Profile
from .models import ActivityLog, LessonView, DailyStreak


def update_streak(user):
    today = date.today()
    streak, _ = DailyStreak.objects.get_or_create(user=user)

    if streak.last_active_date == today:
        return

    if streak.last_active_date == today - timedelta(days=1):
        streak.current_streak += 1
    else:
        streak.current_streak = 1

    if streak.current_streak > streak.longest_streak:
        streak.longest_streak = streak.current_streak

    streak.last_active_date = today
    streak.save()


class DashboardView(SessionLoginRequiredMixin, View):
    def get(self, request):
        user = get_current_user(request)
        update_streak(user)

        ActivityLog.objects.create(
            user=user,
            action=ActivityLog.LOGIN,
            description='Visited dashboard',
        )

        streak, _ = DailyStreak.objects.get_or_create(user=user)
        recent_logs = ActivityLog.objects.filter(user=user).order_by('-created_at')[:10]
        lesson_views = LessonView.objects.filter(user=user).select_related('lesson').order_by('-viewed_at')[:5]

        from assignments.models import AssignmentSubmission
        submissions = AssignmentSubmission.objects.filter(student=user).select_related('assignment')
        total_submitted = submissions.filter(status=AssignmentSubmission.SUBMITTED).count()
        total_graded = submissions.filter(status=AssignmentSubmission.GRADED).count()
        avg_score = submissions.filter(status__in=[
            AssignmentSubmission.SUBMITTED, AssignmentSubmission.GRADED
        ]).aggregate(avg=Avg('total_score'))['avg'] or 0

        from crm.models import Enrollment
        enrollments = Enrollment.objects.filter(student=user, status=Enrollment.APPROVED).select_related('course')

        profile = Profile.objects.filter(user=user).first()

        return render(request, 'dashboard/dashboard.html', {
            'user': user,
            'profile': profile,
            'streak': streak,
            'recent_logs': recent_logs,
            'lesson_views': lesson_views,
            'total_submitted': total_submitted,
            'total_graded': total_graded,
            'avg_score': round(avg_score, 1),
            'enrollments': enrollments,
        })


class ActivityLogListView(SessionLoginRequiredMixin, View):
    def get(self, request):
        user = get_current_user(request)

        if user.is_admin_role:
            logs = ActivityLog.objects.select_related('user').all()
        else:
            logs = ActivityLog.objects.filter(user=user)

        return render(request, 'dashboard/activity_log_list.html', {
            'logs': logs,
        })


class LessonViewListView(SessionLoginRequiredMixin, View):
    def get(self, request):
        user = get_current_user(request)

        if user.is_admin_role:
            views = LessonView.objects.select_related('user', 'lesson').all()
        else:
            views = LessonView.objects.filter(user=user).select_related('lesson')

        return render(request, 'dashboard/lesson_view_list.html', {
            'views': views,
        })


class StreakView(SessionLoginRequiredMixin, View):
    def get(self, request):
        user = get_current_user(request)
        streak, _ = DailyStreak.objects.get_or_create(user=user)

        top_streaks = DailyStreak.objects.select_related('user').order_by('-current_streak')[:10]

        return render(request, 'dashboard/streak.html', {
            'streak': streak,
            'top_streaks': top_streaks,
        })


class StudentProgressView(SessionLoginRequiredMixin, View):
    def get(self, request):
        user = get_current_user(request)

        from assignments.models import AssignmentSubmission, Assignment
        from crm.models import Enrollment, WeeklyJournal, Attendance

        if user.is_student:
            target = user
        else:
            student_id = request.GET.get('student_id')
            if student_id:
                target = get_object_or_404(UserModel, id=student_id, role=UserModel.STUDENT)
            else:
                target = user

        submissions = AssignmentSubmission.objects.filter(student=target).select_related('assignment')
        enrollments = Enrollment.objects.filter(student=target, status=Enrollment.APPROVED).select_related('course')
        journals = WeeklyJournal.objects.filter(student=target).select_related('period')
        attendance = Attendance.objects.filter(student=target)

        total_lessons_viewed = LessonView.objects.filter(user=target).count()
        total_submitted = submissions.filter(status=AssignmentSubmission.SUBMITTED).count()
        total_graded = submissions.filter(status=AssignmentSubmission.GRADED).count()

        present_count = attendance.filter(status=Attendance.PRESENT).count()
        absent_count = attendance.filter(status=Attendance.ABSENT).count()
        excused_count = attendance.filter(status=Attendance.EXCUSED).count()

        streak, _ = DailyStreak.objects.get_or_create(user=target)
        profile = Profile.objects.filter(user=target).first()

        students = None
        if user.is_teacher or user.is_admin_role:
            students = UserModel.objects.filter(role=UserModel.STUDENT)

        return render(request, 'dashboard/student_progress.html', {
            'target': target,
            'profile': profile,
            'submissions': submissions,
            'enrollments': enrollments,
            'journals': journals,
            'total_lessons_viewed': total_lessons_viewed,
            'total_submitted': total_submitted,
            'total_graded': total_graded,
            'present_count': present_count,
            'absent_count': absent_count,
            'excused_count': excused_count,
            'streak': streak,
            'students': students,
        })


class AdminStatsView(AdminRequiredMixin, View):
    def get(self, request):
        from assignments.models import AssignmentSubmission
        from crm.models import Enrollment
        from chat.models import Group, Message

        total_users = UserModel.objects.count()
        total_students = UserModel.objects.filter(role=UserModel.STUDENT).count()
        total_teachers = UserModel.objects.filter(role=UserModel.TEACHER).count()
        total_submissions = AssignmentSubmission.objects.count()
        total_enrollments = Enrollment.objects.filter(status=Enrollment.APPROVED).count()
        total_groups = Group.objects.count()
        total_messages = Message.objects.filter(is_deleted=False).count()
        total_lesson_views = LessonView.objects.count()

        recent_registrations = UserModel.objects.order_by('-date_joined')[:10]
        recent_submissions = AssignmentSubmission.objects.select_related('student', 'assignment').order_by('-submitted_at')[:10]

        top_students = AssignmentSubmission.objects.filter(
            status__in=[AssignmentSubmission.SUBMITTED, AssignmentSubmission.GRADED]
        ).values('student__username').annotate(
            total=Sum('total_score')
        ).order_by('-total')[:5]

        return render(request, 'dashboard/admin_stats.html', {
            'total_users': total_users,
            'total_students': total_students,
            'total_teachers': total_teachers,
            'total_submissions': total_submissions,
            'total_enrollments': total_enrollments,
            'total_groups': total_groups,
            'total_messages': total_messages,
            'total_lesson_views': total_lesson_views,
            'recent_registrations': recent_registrations,
            'recent_submissions': recent_submissions,
            'top_students': top_students,
        })