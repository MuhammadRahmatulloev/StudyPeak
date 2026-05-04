from django.shortcuts import redirect
from django.contrib import messages
from accounts.models import UserModel
from .models import Course, Enrollment


class CourseTeacherRequiredMixin:
    def dispatch(self, request, *args, **kwargs):
        user_id = request.session.get('user_id')
        if not user_id:
            messages.error(request, 'Please login first!')
            return redirect('login')

        user = UserModel.objects.filter(id=user_id).first()
        if not user:
            messages.error(request, 'Please login first!')
            return redirect('login')

        # Superuser (createsuperuser) bypasses all course checks
        if user.is_superuser:
            return super().dispatch(request, *args, **kwargs)

        course_id = kwargs.get('course_id')
        if course_id:
            course = Course.objects.filter(id=course_id).first()
            if not course:
                messages.error(request, 'Course not found.')
                return redirect('course_list')

            if not (user.is_teacher or user.is_admin_role):
                messages.error(request, 'Teacher or admin access required.')
                return redirect('course_list')

            if user.is_teacher and course.teacher != user:
                messages.error(request, 'You are not the teacher of this course.')
                return redirect('course_detail', course_id=course_id)

        return super().dispatch(request, *args, **kwargs)


class EnrolledStudentRequiredMixin:
    def dispatch(self, request, *args, **kwargs):
        user_id = request.session.get('user_id')
        if not user_id:
            messages.error(request, 'Please login first!')
            return redirect('login')

        user = UserModel.objects.filter(id=user_id).first()
        if not user:
            messages.error(request, 'Please login first!')
            return redirect('login')

        # Superuser bypasses enrollment check
        if user.is_superuser:
            return super().dispatch(request, *args, **kwargs)

        course_id = kwargs.get('course_id')
        if course_id and user.is_student:
            enrolled = Enrollment.objects.filter(
                student=user,
                course_id=course_id,
                status=Enrollment.APPROVED
            ).exists()

            if not enrolled:
                messages.error(request, 'You are not enrolled in this course.')
                return redirect('course_list')

        return super().dispatch(request, *args, **kwargs)


class PeriodAccessMixin:
    def dispatch(self, request, *args, **kwargs):
        user_id = request.session.get('user_id')
        if not user_id:
            messages.error(request, 'Please login first!')
            return redirect('login')

        user = UserModel.objects.filter(id=user_id).first()
        if not user:
            messages.error(request, 'Please login first!')
            return redirect('login')

        # Superuser bypasses all period checks
        if user.is_superuser:
            return super().dispatch(request, *args, **kwargs)

        from .models import CoursePeriod
        period_id = kwargs.get('period_id')
        if period_id:
            period = CoursePeriod.objects.filter(id=period_id).first()
            if not period:
                messages.error(request, 'Period not found.')
                return redirect('course_list')

            if user.is_student:
                enrolled = Enrollment.objects.filter(
                    student=user,
                    course=period.course,
                    status=Enrollment.APPROVED
                ).exists()
                if not enrolled:
                    messages.error(request, 'You are not enrolled in this course.')
                    return redirect('course_list')

            elif user.is_teacher and period.course.teacher != user:
                messages.error(request, 'Access denied.')
                return redirect('course_list')

        return super().dispatch(request, *args, **kwargs)