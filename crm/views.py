from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import View
from django.contrib import messages
from accounts.permissions import SessionLoginRequiredMixin, TeacherRequiredMixin, AdminRequiredMixin, TeacherOrAdminRequiredMixin, get_current_user
from accounts.models import UserModel
from .models import *
import json
from django.http import JsonResponse


class SearchStudentsView(SessionLoginRequiredMixin, View):
    def get(self, request, course_id):
        course = get_object_or_404(Course, id=course_id)
        q = request.GET.get('q', '').strip()

        if len(q) < 2:
            return JsonResponse({'users': []})

        enrolled_ids = course.enrollments.values_list('student_id', flat=True)
        users = UserModel.objects.filter(
            username__icontains=q,
            role=UserModel.STUDENT
        ).exclude(id__in=enrolled_ids)[:8]

        data = [{'id': u.id, 'username': u.username, 'role': u.role} for u in users]
        return JsonResponse({'users': data})


class CourseListView(SessionLoginRequiredMixin, View):
    def get(self, request):
        user = get_current_user(request)
        my_teacher_courses = Course.objects.filter(teacher=user)

        if user.is_superuser or user.is_admin_role:
            courses = Course.objects.all()
            available = None
        elif my_teacher_courses.exists() or user.is_teacher:
            courses = my_teacher_courses
            available = None
        else:
            courses = Course.objects.filter(
                enrollments__student=user,
                enrollments__status=Enrollment.APPROVED
            )
            enrolled_ids = Enrollment.objects.filter(
                student=user
            ).values_list('course_id', flat=True)
            available = Course.objects.filter(
                is_active=True
            ).exclude(id__in=enrolled_ids)

        return render(request, 'crm/course_list.html', {
            'courses': courses,
            'available': available,
            'user': user,
        })


class CourseCreateView(TeacherOrAdminRequiredMixin, View):
    def get(self, request):
        return render(request, 'crm/course_create.html')

    def post(self, request):
        from accounts.models import Notification

        user = get_current_user(request)
        name = request.POST.get('name', '').strip()
        description = request.POST.get('description', '').strip()
        become_self = request.POST.get('become_self')
        admin_identifier = request.POST.get('admin_identifier', '').strip()

        if not name:
            messages.error(request, 'Course name is required.')
            return render(request, 'crm/course_create.html')

        course = Course.objects.create(
            name=name,
            description=description,
            teacher=user,
        )

        if not become_self and admin_identifier:
            admin_user = (
                UserModel.objects.filter(email=admin_identifier).first()
                or UserModel.objects.filter(username=admin_identifier).first()
            )

            if not admin_user:
                course.delete()
                messages.error(request, 'User not found. Check the username or email.')
                return render(request, 'crm/course_create.html')

            if admin_user.is_student:
                course.delete()
                messages.error(
                    request,
                    f'"{admin_user.username}" is a student and cannot be assigned as course admin.'
                )
                return render(request, 'crm/course_create.html')

            if admin_user == user:
                messages.success(request, f'Course "{course.name}" created. You are the admin. ✓')
                return redirect('course_detail', course_id=course.id)

            # Создаём приглашение
            CourseAdminInvitation.objects.create(
                course=course,
                sender=user,
                receiver=admin_user,
            )

            Notification.objects.create(
                user=admin_user,
                type=Notification.COURSE_ADMIN_INVITE,
                message=(
                    f'{user.username} invited you to become the administrator '
                    f'of the course "{course.name}".'
                )
            )

            messages.success(
                request,
                f'Course "{course.name}" created. '
                f'Invitation sent to {admin_user.username} — waiting for their response.'
            )
        else:
            messages.success(request, f'Course "{course.name}" created. You are the admin. ✓')

        return redirect('course_detail', course_id=course.id)


class CourseDetailView(SessionLoginRequiredMixin, View):
    def get(self, request, course_id):
        user = get_current_user(request)
        course = get_object_or_404(Course, id=course_id)

        if user.is_student:
            enrollment = Enrollment.objects.filter(student=user, course=course).first()
            if not enrollment or enrollment.status != Enrollment.APPROVED:
                messages.error(request, 'You are not enrolled in this course.')
                return redirect('course_list')

        periods = course.periods.all()
        enrollments = course.enrollments.filter(status=Enrollment.APPROVED).select_related('student')
        pending = course.enrollments.filter(status=Enrollment.PENDING).select_related('student')

        pending_admin_invitation = CourseAdminInvitation.objects.filter(
            course=course,
            status=CourseAdminInvitation.PENDING
        ).select_related('receiver', 'sender').first()

        my_admin_invitation = CourseAdminInvitation.objects.filter(
            course=course,
            receiver=user,
            status=CourseAdminInvitation.PENDING
        ).first()

        return render(request, 'crm/course_detail.html', {
            'course': course,
            'periods': periods,
            'enrollments': enrollments,
            'pending': pending,
            'user': user,
            'pending_admin_invitation': pending_admin_invitation,
            'my_admin_invitation': my_admin_invitation,
        })


class CourseUpdateView(TeacherOrAdminRequiredMixin, View):
    def get(self, request, course_id):
        user = get_current_user(request)
        course = get_object_or_404(Course, id=course_id)

        if user.is_teacher and course.teacher != user:
            messages.error(request, 'Access denied.')
            return redirect('course_detail', course_id=course_id)

        return render(request, 'crm/course_update.html', {'course': course})

    def post(self, request, course_id):
        user = get_current_user(request)
        course = get_object_or_404(Course, id=course_id)

        if user.is_teacher and course.teacher != user:
            messages.error(request, 'Access denied.')
            return redirect('course_detail', course_id=course_id)

        course.name = request.POST.get('name', course.name).strip()
        course.description = request.POST.get('description', course.description)
        course.is_active = request.POST.get('is_active') == 'on'
        course.save()

        messages.success(request, 'Course updated.')
        return redirect('course_detail', course_id=course_id)


class CourseDeleteView(TeacherOrAdminRequiredMixin, View):
    def post(self, request, course_id):
        user = get_current_user(request)
        course = get_object_or_404(Course, id=course_id)

        if user.is_teacher and course.teacher != user:
            messages.error(request, 'Access denied.')
            return redirect('course_detail', course_id=course_id)

        course.delete()
        messages.success(request, 'Course deleted.')
        return redirect('course_list')


class EnrollRequestView(SessionLoginRequiredMixin, View):
    def post(self, request, course_id):
        user = get_current_user(request)
        course = get_object_or_404(Course, id=course_id)

        if not user.is_student:
            messages.error(request, 'Only students can enroll.')
            return redirect('course_list')

        if Enrollment.objects.filter(student=user, course=course).exists():
            messages.warning(request, 'You already have a request or enrollment for this course.')
            return redirect('course_list')

        Enrollment.objects.create(student=user, course=course, type=Enrollment.STUDENT_REQUEST)
        messages.success(request, f'Enrollment request sent for "{course.name}".')
        return redirect('course_list')


class EnrollInviteView(TeacherOrAdminRequiredMixin, View):
    def post(self, request, course_id):
        from accounts.models import Notification
        user = get_current_user(request)
        course = get_object_or_404(Course, id=course_id)

        if user.is_teacher and course.teacher != user:
            return JsonResponse({'status': 'error', 'message': 'Access denied.'})

        student_id = request.POST.get('student_id')
        student = UserModel.objects.filter(id=student_id, role=UserModel.STUDENT).first()
        if not student:
            return JsonResponse({'status': 'error', 'message': 'Student not found.'})

        if Enrollment.objects.filter(student=student, course=course).exists():
            return JsonResponse({'status': 'error', 'message': f'{student.username} already enrolled or invited.'})

        Enrollment.objects.create(
            student=student,
            course=course,
            type=Enrollment.ADMIN_INVITE,
            status=Enrollment.PENDING  
        )

        Notification.objects.create(
            user=student,
            type=Notification.ENROLLMENT_INVITE,
            message=f'{user.username} invited you to join the course "{course.name}".'
        )

        return JsonResponse({'status': 'ok', 'message': f'Invitation sent to {student.username}!'})


class EnrollApproveView(TeacherOrAdminRequiredMixin, View):
    def post(self, request, enrollment_id):
        enrollment = get_object_or_404(Enrollment, id=enrollment_id)
        user = get_current_user(request)

        if user.is_teacher and enrollment.course.teacher != user:
            messages.error(request, 'Access denied.')
            return redirect('course_list')

        enrollment.status = Enrollment.APPROVED
        enrollment.save()
        messages.success(request, f'{enrollment.student.username} approved.')
        return redirect('course_detail', course_id=enrollment.course.id)


class EnrollRejectView(TeacherOrAdminRequiredMixin, View):
    def post(self, request, enrollment_id):
        enrollment = get_object_or_404(Enrollment, id=enrollment_id)
        user = get_current_user(request)

        if user.is_teacher and enrollment.course.teacher != user:
            messages.error(request, 'Access denied.')
            return redirect('course_list')

        enrollment.status = Enrollment.REJECTED
        enrollment.save()
        messages.success(request, f'{enrollment.student.username} rejected.')
        return redirect('course_detail', course_id=enrollment.course.id)


class EnrollRemoveView(TeacherOrAdminRequiredMixin, View):
    def post(self, request, enrollment_id):
        enrollment = get_object_or_404(Enrollment, id=enrollment_id)
        user = get_current_user(request)

        if user.is_teacher and enrollment.course.teacher != user:
            messages.error(request, 'Access denied.')
            return redirect('course_list')

        enrollment.delete()
        messages.success(request, f'{enrollment.student.username} removed from course.')
        return redirect('course_detail', course_id=enrollment.course.id)
    

class EnrollAcceptInviteView(SessionLoginRequiredMixin, View):
    def post(self, request, enrollment_id):
        user = get_current_user(request)
        enrollment = get_object_or_404(
            Enrollment, id=enrollment_id,
            student=user,
            status=Enrollment.PENDING,
            type=Enrollment.ADMIN_INVITE
        )
        enrollment.status = Enrollment.APPROVED
        enrollment.save()
        messages.success(request, f'You joined "{enrollment.course.name}"! 🎉')
        return redirect('course_detail', course_id=enrollment.course.id)


class EnrollRejectInviteView(SessionLoginRequiredMixin, View):
    def post(self, request, enrollment_id):
        user = get_current_user(request)
        enrollment = get_object_or_404(
            Enrollment, id=enrollment_id,
            student=user,
            status=Enrollment.PENDING,
            type=Enrollment.ADMIN_INVITE
        )
        enrollment.status = Enrollment.REJECTED
        enrollment.save()
        messages.info(request, f'You declined the invitation to "{enrollment.course.name}".')
        return redirect('notification_list')


class CoursePeriodCreateView(TeacherOrAdminRequiredMixin, View):
    def get(self, request, course_id):
        course = get_object_or_404(Course, id=course_id)
        return render(request, 'crm/period_create.html', {'course': course})

    def post(self, request, course_id):
        user = get_current_user(request)
        course = get_object_or_404(Course, id=course_id)

        if user.is_teacher and course.teacher != user:
            messages.error(request, 'Access denied.')
            return redirect('course_detail', course_id=course_id)

        name = request.POST.get('name', '').strip()
        order = request.POST.get('order', 1)
        start_date = request.POST.get('start_date') or None
        end_date = request.POST.get('end_date') or None

        if not name:
            messages.error(request, 'Period name is required.')
            return render(request, 'crm/period_create.html', {'course': course})

        CoursePeriod.objects.create(course=course, name=name, order=order, start_date=start_date, end_date=end_date)
        messages.success(request, f'Period "{name}" created.')
        return redirect('course_detail', course_id=course_id)


class CoursePeriodUpdateView(TeacherOrAdminRequiredMixin, View):
    def get(self, request, period_id):
        period = get_object_or_404(CoursePeriod, id=period_id)
        return render(request, 'crm/period_update.html', {'period': period})

    def post(self, request, period_id):
        user = get_current_user(request)
        period = get_object_or_404(CoursePeriod, id=period_id)

        if user.is_teacher and period.course.teacher != user:
            messages.error(request, 'Access denied.')
            return redirect('course_detail', course_id=period.course.id)

        period.name = request.POST.get('name', period.name).strip()
        period.order = request.POST.get('order', period.order)
        period.start_date = request.POST.get('start_date') or None
        period.end_date = request.POST.get('end_date') or None
        period.save()

        messages.success(request, 'Period updated.')
        return redirect('course_detail', course_id=period.course.id)


class CoursePeriodDeleteView(TeacherOrAdminRequiredMixin, View):
    def post(self, request, period_id):
        user = get_current_user(request)
        period = get_object_or_404(CoursePeriod, id=period_id)

        if user.is_teacher and period.course.teacher != user:
            messages.error(request, 'Access denied.')
            return redirect('course_detail', course_id=period.course.id)

        course_id = period.course.id
        period.delete()
        messages.success(request, 'Period deleted.')
        return redirect('course_detail', course_id=course_id)


JOURNAL_WEEKS = [1, 2, 3, 4]
JOURNAL_DAYS  = [1, 2, 3, 4, 5]


class WeeklyJournalView(TeacherOrAdminRequiredMixin, View):

    def _build_data(self, period):
        students = list(UserModel.objects.filter(
            enrollments__course=period.course,
            enrollments__status=Enrollment.APPROVED
        ).select_related('profile'))

        # DailyScore map: {student_id: {week: {day: score}}}
        score_map = {}
        for ds in DailyScore.objects.filter(period=period):
            score_map.setdefault(ds.student_id, {})\
                     .setdefault(ds.week_number, {})[ds.day_number] = ds.score

        # WeekSummary map: {student_id: {week: WeekSummary}}
        ws_map = {}
        for ws in WeekSummary.objects.filter(period=period):
            ws_map.setdefault(ws.student_id, {})[ws.week_number] = ws

        # Week блоки (4 → 1)
        week_rows = []
        for w in reversed(JOURNAL_WEEKS):
            s_data = []
            for student in students:
                days = [score_map.get(student.id, {}).get(w, {}).get(d) for d in JOURNAL_DAYS]
                daily_total = sum(x or 0 for x in days)
                ws_obj = ws_map.get(student.id, {}).get(w)
                bonus = ws_obj.bonus_score if ws_obj else 0
                exam  = ws_obj.exam_score  if ws_obj else 0
                s_data.append({
                    'student':     student,
                    'days':        days,
                    'daily_total': daily_total,
                    'bonus':       bonus,
                    'exam':        exam,
                    'week_total':  daily_total + bonus + exam,
                })
            week_rows.append({'num': w, 'students': s_data})

        # Статистика для шапки
        summary_rows = []
        for student in students:
            grand = 0
            for w in JOURNAL_WEEKS:
                daily = sum(score_map.get(student.id, {}).get(w, {}).get(d, 0) or 0 for d in JOURNAL_DAYS)
                ws_obj = ws_map.get(student.id, {}).get(w)
                grand += daily + (ws_obj.bonus_score if ws_obj else 0) + (ws_obj.exam_score if ws_obj else 0)
            summary_rows.append({'student': student, 'grand_total': grand})

        return students, week_rows, summary_rows

    def get(self, request, period_id):
        user   = get_current_user(request)
        period = get_object_or_404(CoursePeriod, id=period_id)
        if user.is_teacher and period.course.teacher != user:
            messages.error(request, 'Access denied.')
            return redirect('course_list')
        students, week_rows, summary_rows = self._build_data(period)
        return render(request, 'crm/weekly_journal.html', {
            'period': period, 'students': students,
            'week_rows': week_rows, 'summary_rows': summary_rows,
        })

    def post(self, request, period_id):
        user   = get_current_user(request)
        period = get_object_or_404(CoursePeriod, id=period_id)
        if user.is_teacher and period.course.teacher != user:
            messages.error(request, 'Access denied.')
            return redirect('course_list')

        for sid in request.POST.getlist('student_ids'):
            student = UserModel.objects.filter(id=sid).first()
            if not student:
                continue
            for w in JOURNAL_WEEKS:
                for d in JOURNAL_DAYS:
                    raw = request.POST.get(f'score_{sid}_{w}_{d}', '').strip()
                    sc  = max(1, min(5, int(raw))) if raw else None
                    DailyScore.objects.update_or_create(
                        student=student, period=period,
                        week_number=w, day_number=d,
                        defaults={'score': sc},
                    )
                bonus = min(int(request.POST.get(f'bonus_{sid}_{w}') or 0), 10)
                exam  = min(int(request.POST.get(f'exam_{sid}_{w}')  or 0), 70)
                ws, _ = WeekSummary.objects.get_or_create(
                    student=student, period=period, week_number=w)
                ws.bonus_score = bonus
                ws.exam_score  = exam
                ws.save()

        messages.success(request, 'Journal saved. ✓')
        return redirect('weekly_journal', period_id=period_id)


class StudentJournalView(SessionLoginRequiredMixin, View):
    def get(self, request, period_id):
        user = get_current_user(request)
        period = get_object_or_404(CoursePeriod, id=period_id)

        if user.is_student:
            enrollment = Enrollment.objects.filter(
                student=user, course=period.course, status=Enrollment.APPROVED
            ).first()
            if not enrollment:
                messages.error(request, 'Access denied.')
                return redirect('course_list')
            student = user
        else:
            student = user

        WEEKS = [1, 2, 3, 4]
        DAYS  = [1, 2, 3, 4, 5]

        score_map = {}
        for ds in DailyScore.objects.filter(period=period, student=student):
            score_map.setdefault(ds.week_number, {})[ds.day_number] = ds.score

        ws_map = {}
        for ws in WeekSummary.objects.filter(period=period, student=student):
            ws_map[ws.week_number] = ws

        week_data = []
        grand_total = 0
        for w in WEEKS:
            days = [score_map.get(w, {}).get(d) for d in DAYS]
            daily_total = sum(x or 0 for x in days)
            ws_obj      = ws_map.get(w)
            bonus       = ws_obj.bonus_score if ws_obj else 0
            exam        = ws_obj.exam_score  if ws_obj else 0
            week_total  = daily_total + bonus + exam
            grand_total += week_total
            week_data.append({
                'week_number': w,
                'days':        days,
                'daily_total': daily_total,
                'bonus':       bonus,
                'exam':        exam,
                'week_total':  week_total,
            })

        has_data = any(w['week_total'] > 0 for w in week_data)

        return render(request, 'crm/student_journal.html', {
            'period':      period,
            'week_data':   week_data,
            'grand_total': grand_total,
            'has_data':    has_data,
        })


class GradeListView(TeacherOrAdminRequiredMixin, View):
    def get(self, request, period_id):
        user = get_current_user(request)
        period = get_object_or_404(CoursePeriod, id=period_id)

        if user.is_teacher and period.course.teacher != user:
            messages.error(request, 'Access denied.')
            return redirect('course_list')

        grades = Grade.objects.filter(period=period).select_related('student')
        return render(request, 'crm/grade_list.html', {'period': period, 'grades': grades})


class GradeCreateView(TeacherOrAdminRequiredMixin, View):
    def get(self, request, period_id):
        user = get_current_user(request)
        period = get_object_or_404(CoursePeriod, id=period_id)

        if user.is_teacher and period.course.teacher != user:
            messages.error(request, 'Access denied.')
            return redirect('course_list')

        students = UserModel.objects.filter(
            enrollments__course=period.course,
            enrollments__status=Enrollment.APPROVED
        )
        return render(request, 'crm/grade_create.html', {
            'period': period,
            'students': students,
        })

    def post(self, request, period_id):
        user = get_current_user(request)
        period = get_object_or_404(CoursePeriod, id=period_id)

        if user.is_teacher and period.course.teacher != user:
            messages.error(request, 'Access denied.')
            return redirect('course_list')

        student_id = request.POST.get('student_id')
        title = request.POST.get('title', '').strip()
        score = int(request.POST.get('score', 0) or 0)
        max_score = int(request.POST.get('max_score', 100) or 100)
        comment = request.POST.get('teacher_comment', '')

        if not title:
            messages.error(request, 'Title is required.')
            return redirect('grade_create', period_id=period_id)

        student = get_object_or_404(UserModel, id=student_id)

        Grade.objects.create(
            student=student,
            period=period,
            title=title,
            score=score,
            max_score=max_score,
            teacher_comment=comment,
        )

        messages.success(request, f'Grade "{title}" saved for {student.username}.')
        return redirect('grade_list', period_id=period_id)


class AttendanceView(TeacherOrAdminRequiredMixin, View):
    def get(self, request, period_id):
        user = get_current_user(request)
        period = get_object_or_404(CoursePeriod, id=period_id)

        if user.is_teacher and period.course.teacher != user:
            messages.error(request, 'Access denied.')
            return redirect('course_list')

        date = request.GET.get('date')
        students = UserModel.objects.filter(
            enrollments__course=period.course,
            enrollments__status=Enrollment.APPROVED
        )
        attendance_map = {}
        if date:
            records = Attendance.objects.filter(period=period, date=date)
            attendance_map = {r.student_id: r for r in records}

        return render(request, 'crm/attendance.html', {
            'period': period,
            'students': students,
            'date': date,
            'attendance_map': attendance_map,
            'status_choices': Attendance.STATUS_CHOICES,
        })

    def post(self, request, period_id):
        user = get_current_user(request)
        period = get_object_or_404(CoursePeriod, id=period_id)

        if user.is_teacher and period.course.teacher != user:
            messages.error(request, 'Access denied.')
            return redirect('course_list')

        date = request.POST.get('date')
        student_ids = request.POST.getlist('student_ids')

        if not date:
            messages.error(request, 'Date is required.')
            return redirect('attendance', period_id=period_id)

        for student_id in student_ids:
            student = UserModel.objects.filter(id=student_id).first()
            if not student:
                continue
            status = request.POST.get(f'status_{student_id}', Attendance.PRESENT)
            Attendance.objects.update_or_create(
                student=student,
                period=period,
                date=date,
                defaults={'status': status}
            )

        messages.success(request, f'Attendance saved for {date}.')
        return redirect(f'/crm/period/{period_id}/attendance/?date={date}')


class StudentAttendanceView(SessionLoginRequiredMixin, View):
    def get(self, request, period_id):
        user = get_current_user(request)
        period = get_object_or_404(CoursePeriod, id=period_id)

        if user.is_student:
            enrollment = Enrollment.objects.filter(student=user, course=period.course, status=Enrollment.APPROVED).first()
            if not enrollment:
                messages.error(request, 'Access denied.')
                return redirect('course_list')
            records = Attendance.objects.filter(student=user, period=period).order_by('date')
        else:
            records = Attendance.objects.filter(period=period).order_by('date')

        return render(request, 'crm/student_attendance.html', {
            'period': period,
            'records': records,
        })
    

class AcceptCourseAdminInvitationView(SessionLoginRequiredMixin, View):
    def post(self, request, invitation_id):
        user = get_current_user(request)
        invitation = get_object_or_404(
            CourseAdminInvitation,
            id=invitation_id,
            receiver=user,
            status=CourseAdminInvitation.PENDING
        )

        course = invitation.course
        course.teacher = user
        course.save()

        invitation.status = CourseAdminInvitation.ACCEPTED
        invitation.save()

        messages.success(request, f'You are now the administrator of "{course.name}". ✓')
        return redirect('course_detail', course_id=course.id)


class RejectCourseAdminInvitationView(SessionLoginRequiredMixin, View):
    def post(self, request, invitation_id):
        user = get_current_user(request)
        invitation = get_object_or_404(
            CourseAdminInvitation,
            id=invitation_id,
            receiver=user,
            status=CourseAdminInvitation.PENDING
        )

        invitation.status = CourseAdminInvitation.REJECTED
        invitation.save()

        messages.info(request, f'You declined the admin invitation for "{invitation.course.name}".')
        return redirect('course_list')