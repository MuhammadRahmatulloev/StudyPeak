from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import View
from django.contrib import messages
from accounts.permissions import SessionLoginRequiredMixin, TeacherRequiredMixin, AdminRequiredMixin, TeacherOrAdminRequiredMixin, get_current_user
from accounts.models import UserModel
from .models import Course, CoursePeriod, Enrollment, WeeklyJournal, Grade, Attendance, StudentPeriodSummary


class CourseListView(SessionLoginRequiredMixin, View):
    def get(self, request):
        user = get_current_user(request)
        if user.is_teacher:
            courses = Course.objects.filter(teacher=user)
            available = None
        elif user.is_student:
            courses = Course.objects.filter(
                enrollments__student=user,
                enrollments__status=Enrollment.APPROVED
            )
            enrolled_ids = Enrollment.objects.filter(student=user).values_list('course_id', flat=True)
            available = Course.objects.filter(is_active=True).exclude(id__in=enrolled_ids)
        else:
            courses = Course.objects.all()
            available = None
        return render(request, 'crm/course_list.html', {
            'courses': courses,
            'available': available,
        })


class CourseCreateView(TeacherOrAdminRequiredMixin, View):
    def get(self, request):
        return render(request, 'crm/course_create.html')

    def post(self, request):
        user = get_current_user(request)
        name = request.POST.get('name', '').strip()
        description = request.POST.get('description', '').strip()

        if not name:
            messages.error(request, 'Course name is required.')
            return render(request, 'crm/course_create.html')

        course = Course.objects.create(name=name, description=description, teacher=user)
        messages.success(request, f'Course "{course.name}" created.')
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

        return render(request, 'crm/course_detail.html', {
            'course': course,
            'periods': periods,
            'enrollments': enrollments,
            'pending': pending,
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
        user = get_current_user(request)
        course = get_object_or_404(Course, id=course_id)

        if user.is_teacher and course.teacher != user:
            messages.error(request, 'Access denied.')
            return redirect('course_detail', course_id=course_id)

        student_id = request.POST.get('student_id')
        student = get_object_or_404(UserModel, id=student_id, role=UserModel.STUDENT)

        if Enrollment.objects.filter(student=student, course=course).exists():
            messages.warning(request, f'{student.username} already enrolled or invited.')
            return redirect('course_detail', course_id=course_id)

        Enrollment.objects.create(student=student, course=course, type=Enrollment.ADMIN_INVITE, status=Enrollment.APPROVED)
        messages.success(request, f'{student.username} added to course.')
        return redirect('course_detail', course_id=course_id)


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

class WeeklyJournalView(TeacherOrAdminRequiredMixin, View):
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

        journals = WeeklyJournal.objects.filter(period=period)
        journal_map = {}
        for j in journals:
            if j.student_id not in journal_map:
                journal_map[j.student_id] = {}
            journal_map[j.student_id][j.week_number] = j

        summaries = StudentPeriodSummary.objects.filter(period=period)
        summary_map = {s.student_id: s for s in summaries}

        return render(request, 'crm/weekly_journal.html', {
            'period': period,
            'students': students,
            'journal_map': journal_map,
            'summary_map': summary_map,
            'weeks': JOURNAL_WEEKS,
        })

    def post(self, request, period_id):
        user = get_current_user(request)
        period = get_object_or_404(CoursePeriod, id=period_id)

        if user.is_teacher and period.course.teacher != user:
            messages.error(request, 'Access denied.')
            return redirect('course_list')

        student_ids = request.POST.getlist('student_ids')

        for student_id in student_ids:
            student = UserModel.objects.filter(id=student_id).first()
            if not student:
                continue

            for week in JOURNAL_WEEKS:
                score = int(request.POST.get(f'score_{student_id}_{week}') or 0)
                comment = request.POST.get(f'comment_{student_id}_{week}', '')

                journal, _ = WeeklyJournal.objects.get_or_create(
                    student=student, period=period, week_number=week
                )
                journal.base_score = min(score, 100)
                journal.teacher_comment = comment
                journal.save()

            bonus = int(request.POST.get(f'bonus_{student_id}') or 0)
            exam = int(request.POST.get(f'exam_{student_id}') or 0)

            summary, _ = StudentPeriodSummary.objects.get_or_create(
                student=student, period=period
            )
            summary.bonus_score = min(bonus, 20)
            summary.exam_score = min(exam, 100)
            summary.save()

        messages.success(request, 'Journal saved.')
        return redirect('weekly_journal', period_id=period_id)


class StudentJournalView(SessionLoginRequiredMixin, View):
    def get(self, request, period_id):
        user = get_current_user(request)
        period = get_object_or_404(CoursePeriod, id=period_id)

        if user.is_student:
            enrollment = Enrollment.objects.filter(student=user, course=period.course, status=Enrollment.APPROVED).first()
            if not enrollment:
                messages.error(request, 'Access denied.')
                return redirect('course_list')
            journals = WeeklyJournal.objects.filter(student=user, period=period).order_by('week_number')
        else:
            journals = WeeklyJournal.objects.filter(period=period).order_by('week_number')

        return render(request, 'crm/student_journal.html', {
            'period': period,
            'journals': journals,
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