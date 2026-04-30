from django.shortcuts import redirect
from django.contrib import messages
from accounts.models import UserModel
from .models import Subject, Lesson


class SubjectAccessMixin:
    def dispatch(self, request, *args, **kwargs):
        user_id = request.session.get('user_id')
        if not user_id:
            messages.error(request, 'Please login first!')
            return redirect('login')

        user = UserModel.objects.filter(id=user_id).first()
        if not user:
            messages.error(request, 'Please login first!')
            return redirect('login')

        subject_id = kwargs.get('subject_id')
        if subject_id:
            subject = Subject.objects.filter(id=subject_id).first()
            if not subject:
                messages.error(request, 'Subject not found.')
                return redirect('subject_list')

            if user.is_student:
                if subject.group and not subject.group.memberships.filter(user=user).exists():
                    messages.error(request, 'You do not have access to this subject.')
                    return redirect('subject_list')

        return super().dispatch(request, *args, **kwargs)


class SubjectTeacherRequiredMixin:
    def dispatch(self, request, *args, **kwargs):
        user_id = request.session.get('user_id')
        if not user_id:
            messages.error(request, 'Please login first!')
            return redirect('login')

        user = UserModel.objects.filter(id=user_id).first()
        if not user:
            messages.error(request, 'Please login first!')
            return redirect('login')

        if not (user.is_teacher or user.is_admin_role):
            messages.error(request, 'Teacher or admin access required.')
            return redirect('subject_list')

        subject_id = kwargs.get('subject_id')
        if subject_id:
            subject = Subject.objects.filter(id=subject_id).first()
            if not subject:
                messages.error(request, 'Subject not found.')
                return redirect('subject_list')

            if user.is_teacher and subject.teacher != user:
                messages.error(request, 'You are not the teacher of this subject.')
                return redirect('subject_detail', subject_id=subject_id)

        return super().dispatch(request, *args, **kwargs)


class LessonAccessMixin:
    def dispatch(self, request, *args, **kwargs):
        user_id = request.session.get('user_id')
        if not user_id:
            messages.error(request, 'Please login first!')
            return redirect('login')

        user = UserModel.objects.filter(id=user_id).first()
        if not user:
            messages.error(request, 'Please login first!')
            return redirect('login')

        subject_id = kwargs.get('subject_id')
        lesson_id = kwargs.get('lesson_id')

        if subject_id:
            subject = Subject.objects.filter(id=subject_id).first()
            if not subject:
                messages.error(request, 'Subject not found.')
                return redirect('subject_list')

            if user.is_student:
                if subject.group and not subject.group.memberships.filter(user=user).exists():
                    messages.error(request, 'You do not have access to this lesson.')
                    return redirect('subject_list')

        if lesson_id and subject_id:
            lesson = Lesson.objects.filter(id=lesson_id, subject_id=subject_id).first()
            if not lesson:
                messages.error(request, 'Lesson not found.')
                return redirect('subject_detail', subject_id=subject_id)

        return super().dispatch(request, *args, **kwargs)